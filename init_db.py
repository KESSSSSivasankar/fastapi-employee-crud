"""Initialize the SQLite database and create the employee table"""
from app.database import Base, engine

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Database initialized successfully!")
    print("[OK] Employee table created at: employee.db")
