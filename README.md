# AI-Based Interview Training Platform

This is a complete, full-stack web application designed to help students and job seekers practice interviews using Artificial Intelligence.

## Features

- **User Authentication**: Secure JWT-based login and registration.
- **Adaptive AI Interviews**: Dynamic mock interviews based on target job role and difficulty.
- **Real-time Feedback**: Detailed AI evaluation of technical accuracy, relevance, and completeness.
- **Performance Dashboard**: Charts and statistics tracking interview scores over time.
- **Profile Management**: Customize target roles and skills.

## Technology Stack

- **Frontend**: React, Vite, Tailwind CSS, React Router, Recharts, Axios.
- **Backend**: Python, FastAPI, SQLAlchemy, SQLite (Development ready).
- **AI**: Internal Mock AI service that simulates LLM generation and evaluation (can be replaced with OpenAI/Gemini APIs in production).

## Setup Instructions

### 1. Backend Setup

The backend uses FastAPI. You will need Python installed.

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

> **Note on Windows Installation**: If you encounter an error building `pydantic-core` (missing `link.exe`), it means your Python version (e.g., Python 3.14) is missing pre-compiled binary wheels for Pydantic and requires C++ Build Tools. To fix this quickly, use **Python 3.11 or 3.12** instead, or install Visual Studio C++ Build Tools.

#### Running the Backend Server
```bash
uvicorn app.main:app --reload
```
The API documentation will be available at: http://127.0.0.1:8000/docs

### 2. Frontend Setup

The frontend is a React application built with Vite and TailwindCSS.

```bash
cd frontend

# Install dependencies
npm install

# (Optional) If you get tailwind errors on fresh install, ensure you install tailwind explicitly:
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Start the development server
npm run dev
```
The React application will be available at: http://localhost:5173

## Demo Mode

This platform runs entirely offline using the **Mock AI Service** (`backend/app/ai/mock_ai.py`). You do not need an external API key to demonstrate the core functionality! The AI will randomly generate relevant questions and provide structured heuristic-based feedback to simulate a real LLM.

## Project Structure
- `/backend` - Contains FastAPI application, SQLite database connection, Mock AI logic, and Pydantic schemas.
- `/frontend` - Contains Vite React SPA, Tailwind styles, and Recharts dashboard.
