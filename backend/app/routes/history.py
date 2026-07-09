from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.models.history import HistoryOut
from app.auth.utils import get_current_user
from app.database.mongodb import get_db
from app.utils.logging_config import logger

router = APIRouter()

@router.get("/", response_model=List[HistoryOut])
async def list_history(current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable."
        )

    user_id = current_user["_id"]
    try:
        # Fetch history records matching user_id, sorted by timestamp descending
        cursor = db["history"].find({"user_id": user_id}).sort("timestamp", -1)
        history_list = await cursor.to_list(length=100)
        
        # Format MongoDB IDs as strings
        formatted_list = []
        for item in history_list:
            item["_id"] = str(item["_id"])
            formatted_list.append(item)
            
        return formatted_list
    except Exception as e:
        logger.error("Error retrieving search history", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve history."
        )

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
async def delete_history_item(item_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable."
        )

    user_id = current_user["_id"]
    try:
        oid = ObjectId(item_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid history item ID format."
        )

    # Confirm the item exists and belongs to the authenticated user (History Isolation)
    item = await db["history"].find_one({"_id": oid})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History item not found."
        )
        
    if item["user_id"] != user_id:
        logger.warning(
            "Access Denied: Attempt to delete history item of another user",
            attempted_by=user_id,
            owner=item["user_id"],
            item_id=item_id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this history item."
        )

    try:
        await db["history"].delete_one({"_id": oid})
        logger.info("Deleted history item", user_id=user_id, item_id=item_id)
        return {"message": "History item deleted successfully."}
    except Exception as e:
        logger.error("Failed to delete history item", item_id=item_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete history item."
        )
