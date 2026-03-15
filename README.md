# FastAPI Employee CRUD (SQLite)

Basic CRUD API for an `employees` table using FastAPI + SQLAlchemy + SQLite.

## Quickstart (Windows PowerShell)

```powershell
cd C:\Users\sivas\OneDrive\projects\fastapi-employee-crud
python -m venv .venv   # if this fails, try: py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

SQLite DB file will be created at `employee.db` in the project root on first run.

## Postman

Import this collection file into Postman:
- `postman/Employee CRUD API.postman_collection.json`

Set the collection variable `baseUrl` to `http://127.0.0.1:8000` (default).
