from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from database import get_db
from models import Department, Student
from schemas import StudentCreate, StudentOut


router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("/", response_model=list[StudentOut])
def get_students(db: Session = Depends(get_db)) -> list[StudentOut]:
    students = db.scalars(
        select(Student).options(selectinload(Student.department))
    ).all()
    return [
        StudentOut(
            student_id=student.student_id,
            student_name=student.student_name,
            department_id=student.department_id,
            department_name=student.department.department_name,
        )
        for student in students
    ]


@router.post(
    "/",
    response_model=StudentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
) -> StudentOut:
    department = db.get(Department, student_data.department_id)
    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    student = Student(
        student_name=student_data.student_name,
        department_id=student_data.department_id,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return StudentOut(
        student_id=student.student_id,
        student_name=student.student_name,
        department_id=student.department_id,
        department_name=department.department_name,
    )