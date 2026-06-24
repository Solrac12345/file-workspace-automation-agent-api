# File & Workspace Automation Agent

File & Workspace Automation Agent is a web-based application designed to help users organize, manage, and automate file handling in a workspace more efficiently. The project combines a modern backend API with a simple frontend interface to provide a complete experience for authentication, user management, automation services, and product/file-related operations.

This repository contains two main parts:

- Backend: a REST API built with FastAPI, MongoDB, and Docker
- Frontend: a web client built with HTML, CSS, and JavaScript

For detailed backend documentation, see [backend/README.md](backend/README.md).

## Project Goals

The main purpose of this project is to reduce manual effort when working with files and digital workspace resources. It aims to:

- simplify file organization
- provide a clear interface for managing workspace operations
- support automation rules and services
- centralize backend logic for users, services, and products
- make the system easy to run locally or with Docker

## Main Features

- User authentication and access control
- User management
- Service/rule management for automation workflows
- Product/file management
- REST API documentation with Swagger UI and Redoc
- Frontend pages for login, dashboard, and automation views
- CORS-enabled communication between frontend and backend

## Technology Stack

### Backend
- Python 3.12+
- FastAPI
- Pydantic
- Motor (MongoDB async driver)
- MongoDB
- Docker and Docker Compose
- Pytest

### Frontend
- HTML5
- CSS3
- JavaScript (vanilla)
- Fetch API for backend communication

## Project Structure

```text
file-workspace-automation-agent/
├── backend/
│   ├── app/
│   │   ├── controllers/
│   │   ├── database/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
└── frontend/
    ├── index.html
    ├── dashboard.html
    ├── automation.html
    ├── script.js
    ├── styles.css
    └── js/
```

## Prerequisites

Before running the project, make sure you have installed:

- Python 3.12 or newer
- pip
- MongoDB instance or MongoDB Atlas connection
- Docker (optional, for containerized execution)
- A modern web browser

## Backend Setup

1. Open the backend folder:

```bash
cd backend
```

2. Create and activate a virtual environment:

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

On Git Bash or similar:

```bash
python -m venv venv
source venv/Scripts/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the required environment variables:

```env
MONGODB_URI=mongodb://localhost:27017
DB_NAME=automation_agent
SECRET_KEY=your_super_secret_key
```

5. Start the backend server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## Running with Docker

From the backend folder, you can also build and run the container:

```bash
docker build -t automation-agent-api .
docker run -d -p 8000:8000 --env-file .env --name automation-agent automation-agent-api
```

## Frontend Setup

The frontend is a static web application. You can run it locally by opening the HTML files directly in a browser or by using a simple local server such as Live Server in VS Code.

Recommended approach:

1. Open the frontend folder in your editor
2. Start a live server for the project
3. Open the main page from the served folder

The main entry page is:

- [frontend/index.html](frontend/index.html)
- cd frontend
    python -m http.server 5500
    http://localhost:5500

## API Overview

The backend exposes endpoints related to:

- authentication
- users
- services/automation rules
- products/files

You can explore the API live in the Swagger documentation at:

- http://localhost:8000/docs

## Testing

To run the backend test suite:

```bash
cd backend
pytest tests/ -v
```

## Notes

- The frontend uses the backend at http://localhost:8000 by default.
- If you change the backend port or host, update the API base URL in the frontend JavaScript files accordingly.
- For deeper backend implementation details, configuration, and endpoint explanations, refer to [backend/README.md](backend/README.md).

## License

This project is intended for academic use as part of the SENA GA4 activity.
