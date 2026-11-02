# AI Interview Training Platform — Localhost Demonstration Guide

**Project:** AI-Based Interview Training Platform
**Target Environment:** Local Windows Laptop (College Project Demonstration & Viva)
**Architecture:** FastAPI (Backend) + React 19 / Vite (Frontend) + SQLite (Persistent Storage) + Docker Sandbox (Code Execution) + Google Gemini AI (with deterministic Mock AI fallback)

---

## 1. Quick Start (One-Click Demo Launch)

For your presentation, everything can be started with a single click:

1. **Start Docker Desktop** on your Windows laptop.
2. Open the project root folder:
   ```cmd
   C:\Users\HP\OneDrive\Desktop\PROJECT\AI_interview_platform
   ```
3. **Double-click `start_demo.bat`** (or run `.\start_demo.bat` in PowerShell / Command Prompt).

### What `start_demo.bat` Does Automatically:
- Runs pre-flight verification (`verify_environment.py`).
- Launches the **FastAPI Backend** on `http://127.0.0.1:8000` in a dedicated console window.
- Launches the **Vite Frontend** on `http://127.0.0.1:5173` in a dedicated console window.
- Automatically opens your default web browser to `http://localhost:5173`.
- Provides a clean shutdown option (`stop_servers.bat`) to instantly terminate both servers and free ports when your presentation is complete.

---

## 2. Manual Startup (Alternative Option)

If you prefer opening two separate terminal windows:

### Terminal 1 — Backend API
```cmd
cd C:\Users\HP\OneDrive\Desktop\PROJECT\AI_interview_platform\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger API Docs: `http://localhost:8000/docs`

### Terminal 2 — Frontend UI
```cmd
cd C:\Users\HP\OneDrive\Desktop\PROJECT\AI_interview_platform\frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
- User Interface: `http://localhost:5173`

---

## 3. Real Gemini AI vs. Offline Mock Fallback

The platform is designed to be **100% demonstration-ready both online (with real Gemini) and offline (with deterministic Mock AI)**.

### Mode A: Real Gemini AI (Online Mode)
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. In `backend/.env`, set:
   ```ini
   AI_PROVIDER=gemini
   GEMINI_API_KEY=AIzaSy...your_actual_key_here
   AI_MODEL=gemini-2.5-flash
   AI_ENABLED=true
   AI_FALLBACK_TO_MOCK=true
   ```
3. Test your connection before the presentation:
   ```cmd
   cd backend
   python test_gemini_connection.py
   ```
   If successful, `test_gemini_connection.py` will generate a live question and evaluate sample answers in ~1.5s.
4. When real Gemini is active, the frontend sidebar displays **`AI Engine: Real Gemini (gemini-2.5-flash)`**.

### Mode B: Offline Mock AI (No Internet / Zero Latency Mode)
- If your laptop has no internet connection during the presentation or your API quota is exceeded, the platform **automatically falls back to Mock AI**.
- The fallback generates realistic technical questions, evaluates answers with calibrated heuristics, and accurately scores candidate responses.
- The frontend sidebar clearly displays **`AI Engine: Mock Mode`**, maintaining complete transparency.

---

## 4. Real Docker Code Execution (Offline Ready)

Untrusted code submitted by the user is executed in isolated, ephemeral Docker containers with strict resource and security controls.

### Pre-Installed Local Images (Zero Download Required)
All three language runtimes are already pulled and cached locally:
- **Python**: `python:3.11-slim`
- **C++**: `gcc:latest`
- **Java**: `eclipse-temurin:17-jdk-jammy`

### Sandbox Security Controls:
- **Network Isolation**: Containers run with `--network none` (preventing unauthorized external network requests).
- **Resource Constraints**: Capped at `--memory 128m` and `--cpus 0.5`.
- **Execution Timeout**: Containers terminate automatically after `2.0 seconds` to prevent infinite loops.
- **Ephemeral**: Containers are created with `--rm` and destroyed immediately after output collection.

---

## 5. SQLite Data Persistence & Integrity

The active SQLite database is anchored at:
```
backend/interview_platform.db
```
- **Guaranteed Path Resolution**: Regardless of whether commands are run from the project root or the `backend/` directory, the backend anchors directly to `backend/interview_platform.db`, preventing split or empty databases.
- **Pre-Loaded Curriculum**:
  - **6 Progressive Learning Modules**
  - **48 Coding Problems** (8 per module)
  - **195 Automated Test Cases**
  - **Zero Duplicate Seeds** & **0 Foreign Key Violations**
- **Existing User Records**: 35 registered test users, historical interviews, and submissions are preserved.

### Database Backup
A verified backup is stored at:
```
backend/interview_platform.db.backup_checkpoint10gd.db
```
To restore if ever needed:
```cmd
copy backend\interview_platform.db.backup_checkpoint10gd.db backend\interview_platform.db
```

---

## 6. College Demonstration Presentation Script (Step-by-Step)

Follow this 5–7 minute walkthrough for a polished demonstration to professors and evaluators:

### Step 1: Pre-Flight Environment Verification (30 Seconds)
Open a terminal and run:
```cmd
python verify_environment.py
```
- Show evaluators the green checkmarks: Python 3.10+, FastAPI, PyJWT, Docker Desktop running with 3 sandbox images, and SQLite curriculum integrity (6 modules, 48 problems, 195 test cases).
- Explain: *"Our application includes an automated environment health check that validates all architectural dependencies prior to runtime."*

### Step 2: One-Click Startup (30 Seconds)
- Double-click `start_demo.bat`.
- Show evaluators that both services launch in parallel and the browser automatically opens to `http://localhost:5173`.

### Step 3: Authentication & Profile (1 Minute)
- **Login**: Enter an existing account:
  - **Email**: `learner@interview.com`
  - **Password**: `password123`
  - *(Or demonstrate registering a new user with real-time client validation)*.
- **Profile / Resume Upload**:
  - Navigate to **Profile**.
  - Show the candidate skills, experience level, and target role (*e.g., Full Stack Engineer*).
  - Highlight that interview question generation dynamically ingests this candidate profile context.

### Step 4: AI Mock Interview Demonstration (2 Minutes)
- Navigate to **Interview Setup** (`/interviews/setup`).
- Configure a session:
  - Role: `Software Developer`
  - Interview Type: `Technical Interview`
  - Difficulty: `Intermediate`
  - Number of Questions: `3` (for quick demo)
- Click **Start Interview**.
- **Demonstrate Scoring Accuracy & Reliability**:
  - **Question 1**: Enter an intentional nonsense/gibberish answer:
    ```
    hbasjhkdfggasklfdg
    ```
    Click **Submit Answer**.
  - **Question 2**: Enter a concise technical answer:
    *e.g., "A tuple is an immutable sequence in Python, while a list is mutable. Tuples are faster and hashable, making them usable as dictionary keys."*
    Click **Submit Answer**.
  - **Question 3**: Enter a standard technical answer:
    *e.g., "HTTP 404 indicates that the server cannot locate the requested resource at the specified URI."*
    Click **Submit Answer & Complete**.
- **Results Review Page**:
  - Show the comprehensive score breakdown (Technical, Communication, Relevance, Completeness).
  - Open the **Question & Answer Review Modal**:
    - Highlight that Question 1 received **0%** with a clear explanation that the response contained no meaningful technical information.
    - Highlight that Questions 2 and 3 received justified high scores (~85–95%).
    - Explain: *"Our platform enforces strict evaluation heuristics that prevent false inflation on meaningless or random inputs."*

### Step 5: Coding Interview, Roadmap & AI Mentor (2 Minutes)
- Navigate to **Coding Interview** (`/coding`).
- **Interactive Roadmap**:
  - Show the **6 Progressive Modules** (*Foundations & Logic*, *Arrays & Strings*, *Linear Data Structures*, *Searching/Sorting/Recursion*, *Trees/Heaps/Graphs*, *Dynamic Programming*).
  - Point out the server-side prerequisite badges (Modules 1 & 2 open; subsequent modules require 1 solved problem from earlier modules).
- **Problem Catalog & Workspace**:
  - Click **Problem Catalog** and open **Two Sum** (or **Reverse String**).
  - Show the integrated **Monaco Editor** with syntax highlighting for Python, Java, and C++.
- **AI Coding Mentor**:
  - Click the **AI Hints** tab.
  - Reveal **Level 1 (Conceptual Guidance)**.
  - Show that hints unlock progressively without spoiling the solution.
  - Click the **Approach & Complexity** tab to show time/space complexity explanations.
- **Real Docker Sandbox Execution**:
  - Click **Run Code** to execute the starter solution against visible test cases.
  - Show the live Docker execution logs (CPU/memory isolated container output).
  - Modify the code to solve the problem and click **Submit Solution** to run visible + hidden test cases.
  - Point out that solved counts and module progress update in real time.

### Step 6: Interview History & Dashboard Analytics (1 Minute)
- Return to **Dashboard**.
- Show the visual performance charts, recent interview scores, completed coding problems, and personalized skill recommendations.
- Navigate to **Interview History** to show that past sessions and Q&A logs are stored permanently in SQLite.

---

## 7. Troubleshooting Matrix

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| **Port 8000 or 5173 already in use** | A previous server instance is still running in background. | Double-click `stop_servers.bat` to terminate running processes and free both ports. |
| **Docker Desktop not running** | Docker daemon is stopped or not launched. | Start Docker Desktop from Windows Start Menu. The platform will automatically use MockCodeExecutor until Docker is online. |
| **`google-genai` or Python import errors** | Missing Python dependencies. | Run `pip install -r backend/requirements.txt` from Command Prompt. |
| **Gemini API returns Quota/Key Error** | Free quota exceeded or invalid API key. | The platform automatically falls back to Mock AI. Check `python backend/test_gemini_connection.py` for detailed status. |
| **Frontend shows white screen on refresh** | Browser cached old asset bundle. | Hard refresh with `Ctrl + F5` or clear local cache. |
| **SQLite database locked** | Multiple concurrent long transactions. | Close any external SQLite GUI tools (*DB Browser for SQLite*) that may have a write-lock on `interview_platform.db`. |

---

## 8. Summary of Verification Baseline

- **Automated Backend Tests**: **259 passing tests** (`python -m pytest -q`).
- **Frontend Production Build**: **0 errors**, built in < 3s (`npm run build`).
- **Coding Library**: **48 problems**, **195 test cases**, across **6 modules**.
- **Docker Validation Matrix**: Multi-language support (Python, Java, C++) with network isolation and timeout protection.
- **Evaluation Accuracy**: Verified 0% score enforcement for gibberish/invalid responses and calibrated scoring for valid technical answers.
- **Account Recovery**: Secure email-based password reset with 256-bit hashed tokens, 20-min expiration, rate limiting, and JWT session invalidation.
