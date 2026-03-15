from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas


def create_employee(db: Session, payload: schemas.EmployeeCreate) -> models.Employee:
    employee = models.Employee(**payload.model_dump())
    db.add(employee)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(employee)
    return employee


def get_employee(db: Session, employee_id: int) -> models.Employee | None:
    return db.get(models.Employee, employee_id)


def get_employee_by_email(db: Session, email: str) -> models.Employee | None:
    stmt = select(models.Employee).where(models.Employee.email == email)
    return db.scalar(stmt)


def list_employees(
    db: Session, *, skip: int = 0, limit: int = 50, q: str | None = None
) -> list[models.Employee]:
    stmt = select(models.Employee).offset(skip).limit(limit).order_by(models.Employee.id.asc())
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                models.Employee.first_name.ilike(like),
                models.Employee.last_name.ilike(like),
                models.Employee.email.ilike(like),
                models.Employee.department.ilike(like),
                models.Employee.title.ilike(like),
            )
        )
    return list(db.scalars(stmt).all())


def update_employee(db: Session, employee: models.Employee, payload: schemas.EmployeeUpdate) -> models.Employee:
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(employee, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee: models.Employee) -> None:
    db.delete(employee)
    db.commit()
