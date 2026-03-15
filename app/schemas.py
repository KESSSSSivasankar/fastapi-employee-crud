from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    department: str | None = Field(default=None, max_length=100)
    title: str | None = Field(default=None, max_length=100)
    salary: float | None = Field(default=None, ge=0)
    date_of_joining: date | None = None
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    department: str | None = Field(default=None, max_length=100)
    title: str | None = Field(default=None, max_length=100)
    salary: float | None = Field(default=None, ge=0)
    date_of_joining: date | None = None
    is_active: bool | None = None


class EmployeeOut(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
