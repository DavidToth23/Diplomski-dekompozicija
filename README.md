# Relational Schema Decomposition Tool

An educational tool for understanding relational schema decomposition algorithms. Built as a final thesis project at the Faculty of Technical Sciences, University of Novi Sad.

## About

This tool takes a set of functional dependencies as input and walks through the decomposition algorithm step by step, allowing students to follow the process with their own examples.

## Tech Stack

- **Backend:** Python, FastAPI, Pydantic
- **Frontend:** React, Vite
- **Testing:** pytest

## Project Structure

```
projekat/
├── backend/
│   ├── main.py            # FastAPI server
│   └── requirements.txt   # Python dependencies
└── frontend/
    ├── src/
    │   ├── App.jsx        # Main React component
    │   └── main.jsx       # Entry point
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## Running the Project

You need **two terminals** open at the same time.

### Terminal 1 — Backend

```bash
cd backend

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

Backend runs at: `http://localhost:8000` 

### Terminal 2 — Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start the dev server
npm run dev
```

Frontend runs at: `http://localhost:5173`

## Running Tests

```bash
cd backend
pytest tests/
```

For detailed output:

```bash
pytest tests/ -v
```
