**AskMyPhysician Associate AI (Streamlit + FastAPI)**

An empathetic AI-powered health assistant that classifies user symptoms (mild, moderate, or severe) and provides professional medical triage guidance .
Built using LangChain, OpenAI, Streamlit, and FastAPI for web integration.

📁 Project Structure
medical-chatbot/
│
├── demo_logic.py       # Fallback triage logic
├── .env.example        # Template for environment variables
├── app.py              # FastAPI backend (API endpoint)
├── agent.py            # Streamlit chatbot UI
├── .env                # Environment file (contains OpenAI API key)
└── requirements.txt    # Project dependencies

**⚙️ Installation**

```powershell
cd "medical-chatbot"
```

**Create a virtual environment (optional but recommended)**

```powershell
python -m venv venv
venv\Scripts\activate   # (on Windows)
source venv/bin/activate  # (on macOS/Linux)
```

**Install dependencies**

```powershell
pip install -r requirements.txt
```

**Create a .env file and add your OpenAI API key:**

1. Copy `.env.example` to `.env`.
2. Open `.env` and add your key:
   `OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx`

**How to Create OpenAI Account & Get API Key**

1. Go to 🔗 https://platform.openai.com
2. Log in (or sign up).
3. Click your profile icon → View API Keys.
4. Click “Create new secret key”.
5. Copy your API key (looks like: sk-xxxxxxx).

**🚀 Run the Chatbot**

🧩 Step 1 — Run FastAPI Backend
```powershell
uvicorn app:app --reload
```

This will start your API at:
http://127.0.0.1:8000

POST Endpoint:
`POST /chat`

Sample Request:
```json
{ "message": "I have a fever and headache" }
```

Sample Response:
```json
{ "status": "success", "response": "I'm sorry you're feeling unwell...", "session_id": "default_session" }
```

💬 Step 2 — Run Streamlit Chatbot
```powershell
streamlit run agent.py
```

Then open in your browser:
http://localhost:8501

You’ll see the AskMyPhysician Associate AI Chat UI where users can chat and get responses in real time.

**🌐 Deployment Notes**

1. Deploy `app.py` (FastAPI) to your hosting service (e.g., Render, Railway, or your own server).
2. Connect the frontend (website or Streamlit app) to the API URL.
3. Streamlit app can also be hosted on Streamlit Cloud or any VPS.

**🧠 Tech Stack**

*🧠 Tech Stack*

Python 3.10+

Streamlit – Chat UI

FastAPI – Backend API

LangChain – LLM Orchestration

OpenAI GPT-4o-mini – Model

dotenv – Environment management


### 🧪 Running Tests
A small pytest suite has been added to exercise the fallback/demo logic and
API handler. The tests are self‑contained and don’t require a valid OpenAI key.

1. Install the testing dependency (pytest) via the requirements file:

powershell
pip install -r requirements.txt


2. Run the suite from the project root:

powershell
python -m pytest


All tests should pass regardless of your API quota. Additional tests may be
added under tests/ as the application grows.

- **Python 3.10+**
- **Streamlit**: Modern UI for healthcare applications.
- **FastAPI**: High-performance backend API.
- **LangChain**: LLM orchestration and logic.
- **OpenAI GPT-4o-mini**: Advanced medical triage processing.
- **Python-dotenv**: Secure configuration management.
