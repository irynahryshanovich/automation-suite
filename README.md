# Miniaturized Automation Suite

Application that fetches data from external sources, performs actions based on defined rules, and presents the system state through a React-based UI.

## Automation Rules

The system currently implements the following automation rules:

1. **Weather-based**: Pauses Twitter ads if temperature exceeds 30°C, activates them otherwise
2. **Sports-based**: Activates Facebook ads if home team wins, pauses them otherwise
3. **Time-based**: Activates Instagram ads during prime hours (8 AM - 8 PM), pauses them during off-hours

## Features

- **Backend API**: FastAPI-based REST API
- **Data Ingestion**: Fetches weather and sports data from external APIs
- **Automation Engine**: Performs actions based on input data
- **React Frontend**: Responsive, component-based UI
- **Scheduling**: Runs on a configurable cadence

## Setup and Installation

### Prerequisites
- Node.js 16+ and npm (for local frontend development)
- Python 3.9+ (for local backend development)

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

uvicorn app.main:app --reload

or

python run.py

#### Frontend
1. Go to the frontend directory:

cd frontend

2. Install dependencies:

npm install

3. Start the development server:
npm start

## API Endpoints

- `GET /api/logs` - Retrieve action logs
- `GET /api/state` - Get current state of social targets
- `PUT /api/state/{target}` - Update target state
- `POST /api/run` - Manually trigger automation
- `PUT /api/cadence` - Update automation cadence
- `GET /api/settings` - Get current settings
- `DELETE /api/logs` - Clear all logs from the database
