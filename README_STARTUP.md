# AI Investment Advisory System - Startup Guide

## Current System Architecture

The system is currently using **Streamlit** as the primary interface, with a **FastAPI** backend being developed for future migration.

## Quick Start

### 1. Streamlit Interface (Current Production)
```bash
# Using conda environment
conda activate stock
streamlit run main.py

# Or using the startup script
./start_streamlit.sh
```

Access at: http://localhost:8501

### 2. FastAPI Backend (In Development)
```bash
# Install dependencies and start server
./start_fastapi.sh
```

Access at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. React Frontend (Future)
The React frontend is not yet implemented. The system currently uses Streamlit.

## Environment Setup

### Required Environment Variables
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your-openai-api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key (optional)
```

### For FastAPI Backend
Create `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://stock_user:stock_password@localhost:5432/stock_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
```

## Troubleshooting

### Module Import Errors
If you encounter import errors when running FastAPI:
```bash
cd backend
PYTHONPATH=/path/to/stock/backend uvicorn main:app --reload
```

### Database Connection
FastAPI requires PostgreSQL. If not available, the API will run without database features.

### Missing Dependencies
```bash
# For Streamlit
pip install -r requirements.txt

# For FastAPI
pip install -r backend/requirements.txt
```

## Development Status

- ✅ **Streamlit Interface**: Fully functional
- 🚧 **FastAPI Backend**: Under development
- 📅 **React Frontend**: Planned for future

For now, use Streamlit for all functionality. The FastAPI backend is available for testing API development.