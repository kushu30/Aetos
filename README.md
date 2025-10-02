# AETOS Project

An AI-powered platform for automated technology intelligence and forecasting.

## Prerequisites

- Python (3.9 or newer)
- Node.js and npm
- Homebrew (for macOS users)
- Git

---

## 1. Initial Setup

First, clone the repository to your local machine.

```bash
git clone <your-repository-url>
cd Aetos
```

---

## 2. Configuration

The application requires API keys and database connection strings. Create a `.env` file in the root of the Aetos project folder:

```bash
touch .env
```

Open this new `.env` file and add the following, replacing the placeholder values with your own keys:

```env
# .env file

# Get this from Google AI Studio. It's required for all AI analysis.
GEMINI_API_KEY="your_google_ai_api_key_here"

# This is the default connection string for a local MongoDB instance.
MONGO_URI="mongodb://localhost:27017/"
```

---

## 3. Install Dependencies

You need to install dependencies for both the Python backend and the React frontend.

### Backend (Python)

Create a virtual environment and install the required packages.

```bash
# From the root Aetos directory
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend (React)

Navigate to the dashboard directory and install the Node packages.

```bash
# From the root Aetos directory
cd aetos-dashboard
npm install
```

---

## 4. Database Setup (for macOS users)

The backend relies on Redis and MongoDB. Use Homebrew to install and run them as background services.

### Redis (Task Queue)

```bash
brew install redis
brew services start redis
```

### MongoDB (Primary Database)

```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

> **Note:** For other operating systems, using Docker to run Redis and MongoDB is recommended.

---

## 5. Running the Application

AETOS requires three separate processes to be running simultaneously in three different terminals.

### Terminal 1: Start the Celery Worker

This process handles all background analysis.

```bash
# Navigate to the root Aetos directory
cd /path/to/Aetos

# Activate the virtual environment
source venv/bin/activate

# Start the worker
celery -A worker.celery_app worker --loglevel=info
```

### Terminal 2: Start the API Server

This process serves the data to the frontend.

```bash
# Navigate to the root Aetos directory in a NEW terminal
cd /path/to/Aetos

# Activate the virtual environment
source venv/bin/activate

# Start the API
python api.py
```

### Terminal 3: Start the React App

This process runs the user interface.

```bash
# Navigate to the dashboard directory in a NEW terminal
cd /path/to/Aetos/aetos-dashboard

# Start the app (DO NOT activate the Python venv here)
npm start
```

Once all three are running, the AETOS dashboard will automatically open in your browser at [http://localhost:3000](http://localhost:3000).