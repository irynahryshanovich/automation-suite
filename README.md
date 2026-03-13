# Miniaturized Automation Suite

The app runs on a scheduled interval (default every 30 minutes, configurable from 5 min to 24 hours). Each run fetches weather and sports data, evaluates rules, updates target states, and logs every action.

## Automation Rules

The system currently implements the following automation rules:

1. **Weather-based**: Pauses Twitter ads when temperature exceeds 86°F, activates otherwise
2. **Sports-based**: Activates Facebook ads if home team wins, pauses them on loss/tie
3. **Time-based**: Activates Instagram ads during prime hours (8 AM - 8 PM), pauses them during off-hours

## Backend (Python/FastAPI):
- REST endpoints — CRUD for state, logs, settings, cadence, and a manual run trigger
- Pydantic models with enum validation for targets (Twitter/Facebook/Instagram) and statuses (active/paused)
- SQLAlchemy ORM with SQLite for persistence (states and logs tables)
- APScheduler runs automation on a configurable interval
- Integrates with NOAA Weather API and TheSportsDB API, with mock fallbacks on failure
- CORS origins configurable via environment variable for deployment flexibility
- FastAPI lifespan context manager for clean startup/shutdown

## Frontend (React):
- Single-page dashboard: controls, target status toggles, weather/sports data display, automation rules reference, action logs
- Polls backend every 60 seconds, plus immediate refresh on user actions

## Testing (pytest):
- Tests covering API endpoints, weather service, and sports service
- Tests run against a temporary in-memory database so they never touch real data
- External API calls are mocked to keep tests fast and deterministic

## API Endpoints

- `GET /api/logs` - Retrieve action logs
- `GET /api/state` - Get current state of social targets
- `PUT /api/state/{target}` - Update target state
- `POST /api/run` - Manually trigger automation
- `PUT /api/cadence` - Update automation cadence
- `GET /api/settings` - Get current settings
- `DELETE /api/logs` - Clear all logs from the database

## Setup and Installation

### Prerequisites
- Node.js 16+ and npm (for local frontend development)
- Python 3.10+ (for local backend development)

### Local Development
#### Backend
1. Go to the backend directory:
cd backend

2. Create a virtual environment:
python -m venv venv
source venv/bin/activate

3. Install dependencies:
pip install -r requirements.txt

4. Run the application:
uvicorn app.main:app --reload (or python run.py)

#### Frontend
1. Go to the frontend directory:
cd frontend

2. Install dependencies:
npm install
npm run build

3. Start the development server:
npm start
