
Two-part app for career guidance:
- Backend: Flask API with chat endpoints, role data, and optional PDF generation.
- Frontend: React app (Vite-style) that calls the backend.

The backend auto-loads a config.json from anywhere in the project tree and registers blueprints under /api. It also serves a SQLite DB by default if none is configured.

Stack
- Python/Flask, SQLAlchemy, CORS
- Agents: strands-agents + tools
- YouTube / scraping / audio helpers (see requirements)

Repo layout
Actual_Agentic_Code/
├─ backend/
│  └─ src/
│     ├─ main.py          # Flask app entry
│     ├─ routes/          # chat, general_chat, user, etc.
│     └─ models/          # SQLAlchemy models
└─ frontend/
   ├─ src/                # React app
   └─ package.json

Prereqs
- Python ≥ 3.10 (3.12/3.13 fine)
- Node.js ≥ 18 and npm (or pnpm/yarn)
- (Optional) AWS creds in env if you’re using Bedrock via the general chat route.

Install
Backend
  cd backend
  python -m venv .venv
  # Windows: .venv\\Scripts\\activate
  # macOS/Linux: source .venv/bin/activate
  pip install -r requirements.txt

This installs Flask, SQLAlchemy, strands-agents, CORS, YouTube/AI utils, etc.

> Note: If you plan to generate PDFs via the local fallback, add reportlab to requirements.txt.

Frontend
  cd frontend
  npm install

Configuration
- The app will search for a config.json anywhere in the project tree and load it.
- If flask.SQLALCHEMY_DATABASE_URI is absent, it falls back to a local SQLite file at backend/src/database/app.db.
- You can override flask.secret_key.

Environment variables (common)
- FLASK_ENV=development (optional)
- PORT=5000 (Flask default set in code)
- Bedrock (optional)
  - AWS_REGION=<your-region>
  - BEDROCK_MODEL_ID=<your-enabled-model-id>
  - Standard AWS credentials in env/credential chain.

Run
Backend
  cd backend/src
  python main.py
  # Flask starts on http://0.0.0.0:5000

The app registers blueprints: /api/user, /api/chat, /api/general-chat, and the roles API under /api/roles. CORS is enabled for dev.

Frontend (dev)
  cd frontend
  npm run dev
  # open the shown localhost URL

Key API endpoints (quick)
- POST /api/general-chat — general workplace/career support chat (Bedrock-backed if configured).
- GET  /api/general-chat/status — status/info for the general agent.
- Roles API
  - GET  /api/roles — list roles
  - GET  /api/roles/:slug — role details
  - GET  /api/roles/:slug/pdf — generate role PDF

The backend can also serve static files and the app’s index from its static directory (when you build the frontend).

Troubleshooting
- Can’t find config.json: ensure one exists somewhere in the project; the app searches recursively and will exit if none are found.
- DB not set: the app auto-creates a SQLite DB if SQLALCHEMY_DATABASE_URI isn’t provided.
- Bedrock AccessDenied: your AWS account/region may not have model access; set AWS_REGION/BEDROCK_MODEL_ID to an enabled model and ensure IAM allows bedrock:Converse/InvokeModel.

Common scripts
# Backend
cd backend
pip install -r requirements.txt
python src/main.py

# Frontend
cd frontend
npm install
npm run dev

