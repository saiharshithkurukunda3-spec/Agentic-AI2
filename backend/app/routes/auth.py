import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from app.models.user import UserRegister, UserLogin, UserOut, UserDB
from app.auth.utils import hash_password, verify_password, create_access_token, get_current_user
from app.database.mongodb import get_db
from app.utils.config import settings
from app.utils.logging_config import logger

router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserRegister):
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable."
        )

    # Check for existing email
    existing_user_email = await db["users"].find_one({"email": user_data.email})
    if existing_user_email:
        logger.warning("Signup failed: Email already registered", email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )

    # Check for existing username
    existing_user_name = await db["users"].find_one({"username": user_data.username})
    if existing_user_name:
        logger.warning("Signup failed: Username already taken", username=user_data.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken."
        )

    # Hash and save
    try:
        pw_hash = hash_password(user_data.password)
        new_user = UserDB(
            username=user_data.username,
            email=user_data.email,
            password_hash=pw_hash,
            created_at=datetime.datetime.utcnow()
        )
        
        # Save to DB
        result = await db["users"].insert_one(new_user.model_dump(by_alias=True))
        logger.info("New user registered successfully", email=user_data.email, user_id=str(result.inserted_id))
        return {"message": "User registered successfully."}
    except Exception as e:
        logger.error("Error creating user in signup", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred."
        )

@router.post("/login")
async def login(credentials: UserLogin, response: Response):
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable."
        )

    # Find user
    user = await db["users"].find_one({"email": credentials.email})
    if not user:
        logger.warning("Login failed: User email not found", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        logger.warning("Login failed: Incorrect password", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Generate JWT
    token_expires = datetime.timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=token_expires
    )

    # Set Cookie with environment-specific settings
    # For dev, secure=False might be necessary if running on HTTP
    # same_site: Lax is standard.
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite=settings.COOKIE_SAMESITE,
        secure=settings.COOKIE_SECURE
    )

    logger.info("User logged in successfully", email=user["email"], user_id=str(user["_id"]))
    
    # Return user details without password hash
    return {
        "user": {
            "username": user["username"],
            "email": user["email"],
            "_id": str(user["_id"])
        }
    }

@router.post("/logout")
async def logout(response: Response):
    # Overwrite the cookie with an expired date to clear it
    response.delete_cookie(
        key="access_token",
        samesite=settings.COOKIE_SAMESITE,
        secure=settings.COOKIE_SECURE
    )
    logger.info("User logged out, cookie cleared")
    return {"message": "Logged out successfully."}

@router.get("/profile", response_model=UserOut)
async def get_profile(current_user: dict = Depends(get_current_user)):
    return current_user
