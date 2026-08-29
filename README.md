# Senior Full-Stack Developer Data Scientist Portfolio Project

This repository contains a collection of small but practical projects focused on data science, backend APIs, and frontend dashboards. The main project demonstrates a dengue surveillance and forecasting prototype for Chonburi Province, while the other folders show related examples of FastAPI + PostgreSQL integration and a district-filter dashboard.

## Included projects

- Chonburi Dengue Watch
  - Full-stack dashboard and prediction service
  - FastAPI backend + React frontend
  - Synthetic dengue forecasting demo

- PostgreSQL + FastAPI
  - Example of a PostgreSQL-backed API using FastAPI
  - Docker Compose setup for local database services

- React Dashboard District Filter
  - Frontend dashboard with district filtering patterns

## Repository structure

```text
senior-full-stack-developer-data-scientist/
├── .gitignore
├── README.md
├── generate_chonburi_dengue_mock.py
├── chonburi-dengue-watch/
│   ├── README.md
│   ├── backend/
│   └── frontend/
├── postgresql-fastapi/
│   └── postgresql/
└── react-dashboard-district-filter/
    └── frontend/
```

## Main project: Chonburi Dengue Watch

This is the core demonstration project for the repository. It combines:

- a synthetic public-health data pipeline
- a RandomForest-based forecasting model
- a FastAPI backend for prediction and storage
- a React dashboard for monitoring district-level risk

## Quick start

### 1) Clone and enter the project

```bash
git clone https://github.com/prapan34-hue/senior-full-stack-developer-data-scientist.git
cd senior-full-stack-developer-data-scientist
```

### 2) Run the dengue project

```powershell
cd chonburi-dengue-watch/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.ml.train
uvicorn app.main:app --reload --port 8000
```

Then launch the frontend:

```powershell
cd ../frontend
pnpm install
pnpm dev
```

### 3) Run PostgreSQL sample

```powershell
cd ../postgresql-fastapi/postgresql
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
docker compose up -d
uvicorn app.main:app --reload --port 8000
```

## Presentation notes

This portfolio demonstrates the combination of:

- backend engineering with Python and FastAPI
- database design with SQLite and PostgreSQL
- machine learning workflow for forecasting
- dashboard development with React and Vite
- API integration and data visualization

## Important note

The dengue dataset used in the main project is synthetic and intended for demonstration, prototyping, and presentation use only. It should not be used for real public-health decisions without independent domain validation and verified operational data.

## License

This repository is intended for academic, research, and portfolio demonstration purposes.
