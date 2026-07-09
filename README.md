# VERITAS AI - Premium Research Engine

VERITAS AI is a production-ready, full-stack, lightweight Retrieval-Augmented Generation (RAG) assistant. It allows researchers to enter complex queries, search the web, download relevant pages, extract article content, rank chunks using BM25, and generate highly accurate synthesized responses using the Google Gemini API.

It is designed with a ultra-low memory footprint to run comfortably inside Render's **Free Tier (512 MB RAM limit)** with idle RAM usage well under 250 MB.

---

## Features

- **Dynamic Transient RAG**: Search web indices asynchronously, scrape body text with `trafilatura`, chunk it, and rank context chunks using a pure-Python BM25 algorithm. No memory-heavy vector databases or PyTorch dependencies.
- **Secure Authentication**: Cookie-based `HttpOnly` JWT access tokens with environment-specific `Secure` and `SameSite` flags. Protects against XSS and token stealing.
- **Modern Hashing**: OWASP-recommended password protection using `Argon2` (via `argon2-cffi`).
- **Resilience & Reliability**:
  - Connection pooling using a shared `httpx.AsyncClient`.
  - SSRF protection in scraping (denying local, loopback, private, and multicast address ranges).
  - Rate limiting token-bucket middleware.
  - In-memory cache with an active background purger.
  - Exponential backoff retry logic.
  - Graceful degraded startup if database or external keys are missing.
- **Diagnostics**: Detailed `/health` endpoint displaying process memory, uptime, database ping, and Gemini status.

---

## Folder Explanation

```
veritas-ai/
├── render.yaml                 # Render Infrastructure-as-Code Blueprint
├── README.md                   # Project documentation
│
├── backend/
│   ├── app/
│   │   ├── auth/
│   │   │   └── utils.py        # Password hashing (Argon2) and JWT cookie handlers
│   │   ├── database/
│   │   │   └── mongodb.py      # Async Motor client initialization with startup fallback
│   │   ├── models/
│   │   │   ├── user.py         # Registration and Profile Pydantic schemas
│   │   │   └── history.py      # Search log schemas
│   │   ├── routes/
│   │   │   ├── auth.py         # Login, Register, Profile, and Logout (clearing cookie)
│   │   │   ├── history.py      # Isolation-enforced search log management
│   │   │   ├── research.py     # RAG pipeline POST endpoint
│   │   │   └── health.py       # JSON health status and diagnostics
│   │   ├── services/
│   │   │   ├── search.py       # DuckDuckGo async text query service with backoffs
│   │   │   ├── scraper.py      # SSRF-guarded HTTPX page retriever and Trafilatura extractor
│   │   │   ├── rag.py          # BM25 ranker, chunker, and background cache purger
│   │   │   └── llm.py          # LLM Provider abstraction for Gemini JSON generation
│   │   └── utils/
│   │       ├── config.py       # Pydantic Settings environment parser
│   │       ├── http_client.py  # Central HTTPX async client connection pooler
│   │       ├── logging_config.py # Structured JSON logging output
│   │       └── rate_limiter.py # Token-bucket API Rate Limiter middleware
│   │
│   ├── main.py                 # FastAPI application and route mount entrypoint
│   ├── requirements.txt        # Minimal Python dependencies
│   ├── runtime.txt             # Render runtime python version spec
│   ├── Dockerfile              # Multi-stage production container setup
│   └── .env.example            # Environment variables template
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Navbar.jsx          # Cookie-based authenticated navigation
    │   │   ├── ProtectedRoute.jsx  # Page protection router guard
    │   │   ├── SourceCard.jsx      # Individual source details card
    │   │   ├── LoadingSpinner.jsx  # Stage-based RAG pipeline animation
    │   │   └── ErrorMessage.jsx    # Styled warning alerts
    │   ├── pages/
    │   │   ├── Home.jsx            # Premium landing hero
    │   │   ├── Login.jsx           # Clean auth submission page
    │   │   ├── Signup.jsx          # Register panel
    │   │   ├── Profile.jsx         # Diagnostic account statistics
    │   │   ├── Research.jsx        # Search panel, answers, and relevance meters
    │   │   └── History.jsx         # Private query log and deletion panel
    │   ├── hooks/
    │   │   └── useAuth.jsx         # Authentication Context Provider hook
    │   ├── services/
    │   │   └── api.js              # Credentials-enabled Axios instance
    │   ├── App.jsx                 # Routes stitcher
    │   ├── index.css               # Tailwind setup and glassmorphism styling
    │   └── main.jsx                # React bootstrapper
    │
    ├── package.json            # Vite npm script and plugin list
    ├── vite.config.js          # Vite config
    ├── tailwind.config.js      # Custom theme colors and glow selectors
    ├── vercel.json             # Vercel SPA route rewrite rules
    └── index.html              # Main HTML mount template with Inter font
```

---

## Installation Guide

### Backend Setup

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a python virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   source venv/bin/activate      # On Linux/macOS
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill out your credentials:
   - `MONGODB_URI`: Your MongoDB Atlas URI.
   - `GEMINI_API_KEY`: Your Google Gemini API Key.
   - `JWT_SECRET`: A long random string.
5. Start the server locally:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend folder:
   ```bash
   cd ../frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Create a `.env` file in the frontend folder:
   ```env
   VITE_API_URL=http://localhost:8000
   ```
4. Run the local development server:
   ```bash
   npm run dev
   ```
5. Open your browser to `http://localhost:5173`.

---

## Deployment Guide

### Backend to Render (Free Tier)

1. Connect your repository to **Render**.
2. Click **New** -> **Web Service** (or use the Blueprint file `render.yaml`).
3. Set your service variables in the Render Dashboard:
   - `MONGODB_URI`: Connect string.
   - `JWT_SECRET`: Random key.
   - `GEMINI_API_KEY`: Gemini credentials.
   - `ALLOWED_ORIGINS`: Address of your deployed frontend (e.g. `https://veritas-ai.vercel.app`).
   - `COOKIE_SECURE`: `true`.
   - `COOKIE_SAMESITE`: `none`.
4. Deploy the service. The service will build and run using Python 3.11, running well within 512 MB.

### Frontend to Vercel

1. Install Vercel CLI or import the repository on **Vercel**.
2. Set Environment Variables in Vercel:
   - `VITE_API_URL`: Your deployed Render API root URL (e.g. `https://veritas-ai-backend.onrender.com`).
3. Deploy. The project's `vercel.json` ensures that routing works correctly when clicking links.

---

## API Documentation

The backend endpoints are documented interactively at `/docs`. Below is a summary of the main endpoints.

### Authentication (Cookies Auth)

- **`POST /auth/signup`**
  - Body: `{"username": "...", "email": "...", "password": "..."}`
  - Action: Registers new user (Argon2 hash).

- **`POST /auth/login`**
  - Body: `{"email": "...", "password": "..."}`
  - Action: Validates credentials. Writes `access_token` HttpOnly cookie.

- **`POST /auth/logout`**
  - Action: Clears the `access_token` cookie.

- **`GET /auth/profile`**
  - Protected. Returns current user details.

### RAG Pipeline

- **`POST /research`**
  - Protected.
  - Body: `{"query": "User research query"}` (Max 250 chars).
  - Flow: DDGS -> HTML scrapes (SSRF-protected) -> BM25 ranking -> Gemini synthesis.
  - Cache: In-memory query response cache (10 mins TTL).
  - Returns:
    ```json
    {
      "answer": "Grounded synthesized text...",
      "sources": [
        { "title": "Title", "url": "URL", "relevance_score": 0.85 }
      ],
      "relevance_score": 85
    }
    ```

### History Management

- **`GET /history`**
  - Protected. Lists history records belonging to the authenticated user.

- **`DELETE /history/{item_id}`**
  - Protected. Deletes the given item (asserts owner user ID matches).

### System Status

- **`GET /health`**
  - Returns system diagnostics (Uptime, Memory RSS load in MB, DB connection test, Gemini configuration check).
