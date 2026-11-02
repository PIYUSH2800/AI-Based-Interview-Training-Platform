# AI-Based Interview Training Platform

## Overview

The **AI-Based Interview Training Platform** is a full-stack web application designed to help students, fresh graduates, and job seekers practice for technical and behavioral interviews. By leveraging Artificial Intelligence, the platform provides an interactive, realistic interview experience complete with adaptive questioning, voice input, coding challenges, and comprehensive personalized feedback.

It is built to be easily testable, configurable, and deployable, making it an excellent resource for interview preparation or as a demonstrative technical project.

---

## 🚀 Quick Start — Localhost College Demonstration

For full viva and college presentation instructions, see **[LOCALHOST_DEMONSTRATION_GUIDE.md](LOCALHOST_DEMONSTRATION_GUIDE.md)**.

### 1-Click Startup (Windows)
1. Ensure **Docker Desktop** is running.
2. Double-click **`start_demo.bat`** in the project root.
3. Both servers will launch automatically:
   - **Frontend UI:** `http://localhost:5173`
   - **Backend API:** `http://localhost:8000` (Swagger Docs: `http://localhost:8000/docs`)

### Pre-Flight Verification Script
Run the automated environment diagnostic anytime:
```bash
python verify_environment.py
```

### Stop Servers
Double-click **`stop_servers.bat`** to cleanly terminate running servers and free ports 8000 and 5173.

---

## Feature List

### Authentication
* User registration and login
* Secure JWT-based authentication
* Protected routes and session management

### Profile & Resume
* User profile management (target roles, skills, education)
* Resume upload functionality
* Automated PDF/DOCX parsing and resume analysis

### AI Interviews
* Dynamic AI question generation tailored to user profiles
* Real-time answer evaluation
* Google Gemini integration for high-quality responses
* Offline/deterministic Mock AI fallback

### Adaptive Interviews
* Difficulty adaptation based on candidate performance
* Topic adaptation and dynamic interview strategy
* Question coverage tracking and duplicate prevention

### Voice
* Speech-to-text integration for spoken answers
* Text-to-speech capabilities
* Browser-native voice features with editable transcripts

### Communication Analytics
* Word count and sentence metrics tracking
* Filler word detection (e.g., "um", "like")
* Estimated speaking time and Words Per Minute (WPM) calculation

### Interview Intelligence
* Category performance scoring (technical, communication, relevance)
* Topic performance breakdowns
* Identification of strengths and improvement areas
* Actionable practice recommendations and an overall AI summary

### Coding Interviews
* Curated problem bank
* Integrated Monaco Editor for in-browser coding
* Support for Python, Java, and C++
* Secure Docker-based execution for untrusted code
* Automated test cases and scoring
* Submission history tracking
* AI-driven coding feedback and approach suggestions

### Dashboard & History
* Comprehensive interview history
* Score tracking and progression analytics
* Historical performance trends

---

## Architecture Overview

The platform uses a decoupled client-server architecture.

**General Application Flow:**
```text
Frontend (React)
       ↓
FastAPI REST API
       ↓
Services / AI / Database (SQLite)
       ↓
Gemini API or Mock AI Service
```

**Coding Execution Flow:**
```text
Frontend (React)
       ↓
FastAPI REST API
       ↓
Docker Code Execution Service
       ↓
Isolated Language Container (Python/Java/C++)
```

---

## Technology Stack

**Frontend:**
* React 19
* Vite
* Tailwind CSS
* React Router
* Recharts (for analytics)
* Axios
* Monaco Editor (for coding interviews)

**Backend:**
* Python
* FastAPI (REST Framework)
* SQLAlchemy (ORM)
* SQLite (Database)
* Pytest (Testing)

**AI & Execution:**
* Google Gemini (Generative AI)
* Docker (Isolated code execution)

---

## Project Structure

```text
AI_interview_platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── ai/
│   │   ├── auth/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   ├── uploads/
│   ├── .env.example
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   └── services/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

---

## Prerequisites

To run this project locally, ensure you have the following installed:
* **Python**: 3.9+ (Python 3.11 or 3.12 recommended on Windows to avoid build issues)
* **Node.js**: v18+ and **npm**
* **Docker Desktop**: Required for executing coding interview submissions securely.
* **WSL2**: (Windows only) Required by Docker Desktop for Linux containers.
* **Gemini API Key**: (Optional) Required only if you wish to use the live AI mode.

---

## Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on Windows:
   venv\Scripts\activate
   # Activate on macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Copy the example environment file and fill in your details:
   ```bash
   cp .env.example .env
   ```
   *(See the Environment Variables section for configuration details)*

5. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend API will run on `http://127.0.0.1:8000`

---

## Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure API base URL:**
   By default, the Vite app proxies or points requests to `http://localhost:8000`. If your backend runs on a different port, update the API base URL in your frontend configuration or environment.

4. **Start the development server:**
   ```bash
   npm run dev
   ```
   The React application will be available at `http://localhost:5173`

5. **Build the production bundle:**
   ```bash
   npm run build
   ```

---

## Environment Variables

The backend relies on environment variables defined in `backend/.env`. Important variables include:

* `SECRET_KEY`: Used for signing JWTs. You must generate a secure, random string (e.g., using `python -m secrets`).
* `ENVIRONMENT`: `development` | `staging` | `production`.
* `ALLOWED_ORIGINS`: Comma-separated list of allowed frontend origins for CORS.
* `AI_PROVIDER`: Set to `gemini` to use live AI, or `mock` to force deterministic responses.
* `GEMINI_API_KEY`: Your Google Gemini API key.
* `AI_MODEL`: e.g., `gemini-2.5-flash`.
* `AI_ENABLED`: Feature flag (`true`/`false`).
* `AI_FALLBACK_TO_MOCK`: Automatically switch to Mock AI if the live API fails (`true`/`false`).
* `CODE_EXECUTION_TIMEOUT`: Maximum time allowed for user code execution.
* `CODE_MAX_SOURCE_SIZE` / `CODE_MAX_OUTPUT_SIZE`: Limits on code size and stdout length.
* `CODE_EXECUTION_MEMORY`: Memory limit for the Docker container (e.g., `128m`).

**Generating a secure `SECRET_KEY`**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
*Never commit your real `.env` file or expose your API keys!*

---

## Gemini / Mock Mode

The platform supports two AI operational modes to facilitate both rich experiences and reliable offline demonstrations:

### Live AI (Gemini)
Requires a valid `GEMINI_API_KEY`. The platform communicates with Google's Gemini models to evaluate resumes, dynamically generate adaptive questions, and score answers organically based on deep natural language understanding.

### Mock AI
Works entirely offline without an API key. It provides deterministic, heuristic-based responses for all AI operations. This mode is excellent for local development, automated testing, and guaranteed demonstrations without risking network timeouts or rate limits.

*Selection is based on the `AI_PROVIDER` and `AI_FALLBACK_TO_MOCK` environment variables.*

---

## Docker Coding Execution

User-submitted code is never executed directly on the host machine. Instead, it is executed securely using ephemeral Docker containers.

The following security restrictions are strictly enforced for every submission:
* **Network Disabled**: Containers are run with `--network none` to prevent malicious outbound requests.
* **Memory Limit**: Memory consumption is capped to prevent OOM attacks (e.g., `--memory 128m`).
* **CPU Limit**: CPU usage is constrained to prevent denial of service (e.g., `--cpus 0.5`).
* **Timeout Execution**: Processes are forcefully killed if they exceed the configured execution timeout.
* **Restricted Language Allowlist**: Only predefined languages and commands are permitted.
* **Container Cleanup**: Containers are automatically destroyed immediately after execution (`--rm`).

---

## Supported Languages

For coding interviews, the platform officially supports:
* **Python** 
* **Java** 
* **C++** 

---

## API Overview

The platform exposes a robust REST API. Key namespaces include:

* **Authentication** (`/api/auth`): Login, registration, token generation.
* **Profile** (`/api/profile`): User profile management.
* **Resume** (`/api/resume`): Resume upload, parsing, and analysis endpoints.
* **Interviews** (`/api/interviews`): Creation and management of interview sessions.
* **AI** (`/api/ai`): Endpoints for AI question generation, adaptive routing, and feedback.
* **Coding** (`/api/coding`): Endpoints to fetch coding problems, submit code for Docker execution, and retrieve test results.
* **Analytics** (`/api/analytics`): Aggregation of communication metrics and overall interview intelligence scores.

---

## Running Tests

The platform includes comprehensive test suites.

### Backend
To run the full backend testing suite:
```bash
cd backend
python -m pytest
```
*Current verified status: **97 passed*** (including rigorous security hardening tests).

### Frontend
To verify the frontend compiles cleanly for production:
```bash
cd frontend
npm run build
```
*Current verified status: **Successful production build***.

---

## Deployment Readiness

### Database
The platform defaults to **SQLite** (`interview_platform.db`) for rapid development and straightforward single-server deployments.
* **Schema Creation**: Tables are created automatically on startup.
* **Migrations**: A database migration framework (e.g., Alembic) is not currently implemented.
* **Production Note**: For high-concurrency cloud deployments, transitioning to PostgreSQL or MySQL is recommended.

### File Storage
Uploaded resumes are temporarily stored locally in the `backend/uploads/` directory.
* **Security**: This directory must not be publicly exposed via a static web server.
* **Future Scaling**: For distributed deployments, consider migrating upload handling to an external object storage service (e.g., AWS S3).

### Health Checks
To verify the application is running, a safe public endpoint is available:
* `GET /` returns a welcome JSON payload.

### Deployment Options

#### 1. Local Demo
* **Stack**: Python, Node.js, Docker Desktop (Windows/Mac/Linux).
* **Setup**: Follow the standard setup steps above using `npm run dev` and `uvicorn --reload`.

#### 2. Single-Server Deployment
* **Stack**: FastAPI (Uvicorn), Frontend Static Build, Docker Engine.
* **Backend**: Run FastAPI with a production ASGI server configuration:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
* **Frontend**: Serve the static `dist/` bundle (generated via `npm run build`) using Nginx or a similar web server, configured to proxy API requests to the backend on port 8000.
* **Coding Execution**: Ensure the host environment has Docker Engine installed and accessible to the backend process. Note: The application itself does not require containerization; Docker is only invoked to isolate user code execution.

#### 3. Future Cloud Deployment
* Host the backend on a secure VM or container platform (with access to a Docker daemon for code execution).
* Host the frontend static files on a CDN (e.g., Vercel, Netlify, AWS CloudFront).
* Utilize an external managed database (e.g., AWS RDS) and object storage (e.g., AWS S3).

### Backup / Data Considerations
* **Database**: Regularly backup `backend/interview_platform.db` if utilizing SQLite in production.
* **Uploads**: Back up the `backend/uploads/` directory to preserve candidate resumes.
* **Secrets**: Securely rotate your `SECRET_KEY` and `GEMINI_API_KEY`.

### Pre-Deployment Checklist
Before deploying to any production or staging environment, verify the following:
- [ ] Generate and configure a secure, random `SECRET_KEY`.
- [ ] Configure `ALLOWED_ORIGINS` to precisely match your frontend domain(s).
- [ ] Set `ENVIRONMENT=production`.
- [ ] Set `GEMINI_API_KEY` (if utilizing live AI).
- [ ] Ensure Docker Engine is running and accessible.
- [ ] Run the backend test suite (`python -m pytest`).
- [ ] Build the frontend (`npm run build`).
- [ ] Verify functionality (Authentication, AI Interviews, Coding Execution, Resume Uploads).
