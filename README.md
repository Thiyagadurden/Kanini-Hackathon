# Django + React (Vite) Scaffold

This is a modern full-stack scaffold with a Django backend and a React (Vite) frontend.

## Project Structure

- `backend/`: Django REST Framework project.
- `frontend/`: React + Vite project.

## Getting Started

### Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the Django server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

## API Endpoint

The frontend is configured to proxy requests starting with `/api/` to the Django backend (running on `http://127.0.0.1:8000`).

A sample endpoint is available at `http://localhost:5173/api/hello/` which is fetched by the React app.
"# Kanini-Hackathon" 
