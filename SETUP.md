# Google Cloud Sentinel - Setup Guide

Complete setup instructions for both frontend and backend.

## Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.9+ (for backend)
- **Git** (for version control)
- **GCP Account** with Gemini API access (optional, for AI features)

---

## Backend Setup (Python/FastAPI)

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the `backend/` directory:
```env
# Gemini API
GEMINI_API_KEYS=your_api_key_here

# GCP Configuration
GCP_PROJECT_ID=your_project_id
GCP_BILLING_ACCOUNT=your_billing_account

# Datadog (Optional)
DATADOG_API_KEY=your_datadog_api_key
DATADOG_APP_KEY=your_datadog_app_key
DATADOG_SITE=datadoghq.com

# Server
BACKEND_URL=http://localhost:8000
```

### 5. Run Backend Server
```bash
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**

---

## Frontend Setup (Next.js/React)

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment Variables
Create a `.env.local` file in the `frontend/` directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Google Cloud Sentinel
```

### 4. Run Development Server
```bash
npm run dev
```

Frontend will be available at: **http://localhost:3000** (or **http://localhost:3001** if port 3000 is in use)

### 5. Build for Production
```bash
npm run build
npm start
```

---

## Project Structure

```
google-cloud-sentinel/
├── backend/                    # Python FastAPI API
│   ├── src/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core business logic
│   │   ├── phases/            # 8-phase recommendation engine
│   │   └── telemetry/         # Datadog integration
│   ├── tests/                 # Unit tests
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Backend environment variables
│
├── frontend/                   # Next.js React UI
│   ├── src/
│   │   ├── app/               # Page routes
│   │   ├── components/        # React components
│   │   │   └── phases/        # Phase-specific UI
│   │   └── types/             # TypeScript definitions
│   ├── package.json           # Node.js dependencies
│   ├── package-lock.json      # Dependency lock file
│   └── .env.local             # Frontend environment variables
│
├── terraform/                  # Infrastructure as Code
├── datadog-setup/             # Telemetry configuration
├── .gitignore                 # Git ignore rules
├── SETUP.md                   # This file
└── README.md                  # Project overview
```

---

## Running Both Services Together

### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn src.api.app:app --reload --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

Both services will now be running and communicating with each other.

---

## Available Scripts

### Backend
- `python -m uvicorn src.api.app:app --reload` - Run dev server
- `pytest` - Run tests
- `python check_datadog_credentials.py` - Verify Datadog setup

### Frontend
- `npm run dev` - Development server
- `npm run build` - Production build
- `npm start` - Start production server
- `npm run lint` - Run ESLint

---

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

### Python Virtual Environment Issues
```bash
# Recreate venv if corrupted
rm -rf backend/venv
python -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

### Node Modules Issues
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## API Documentation

Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Team Collaboration Notes

1. **Always activate virtual environment** before running backend:
   ```bash
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies** when pulling changes:
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   npm install
   ```

3. **Keep .env files secret** - Never commit environment variable files

4. **Test before committing**:
   ```bash
   # Backend
   pytest tests/
   
   # Frontend (if available)
   npm run lint
   ```

---

## Getting Help

- Check logs: Backend outputs to console, Frontend to browser console
- Review `.env` files for missing configuration
- Verify API connectivity: http://localhost:8000/health

