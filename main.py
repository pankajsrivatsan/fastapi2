from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database import Base, get_db, engine
from models import Department, Grade, Student
from schemas import (
    DepartmentCreate,DepartmentResponse,
    GradeCreate,GradeResponse,
    StudentCreate,StudentResponse
)
from typing import List
import time

Base.metadata.create_all(engine)
app=FastAPI(title="student api management")


#cors 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

#middleware
@app.middleware('http')#receives the http request
async def log_requests(request:Request, call_next):#gets access from fastapi for request and call_next(receive response and provides access to next middleware or endpoints in the chain)
    start=time.time()#timer for this func. also, it's the starting timer. 
    response=await call_next(request)#first it receives the request and verify the input is valid then it can be proceeded to further endpoint afterwards. it's like bridge where it connects first and second
    print(f"{request.method}, {request.url}, -> {response.status_code}, ({time.time()-start:.3f}s)")#request.method means get/post etc.., request.url means "http:/// stuff", request.status_code means whether it's 201, 202, 204, etc....
    return response#finally, returns the response with method,url, status_code and it looks like "GET http://127.0.0.1:8000/students → 200 (0.023s)"
#dependencies
def get_department_or_404(department_id:int, db:Session=Depends(get_db) ):
    dept= db.query(Department).filter(Department.id ==department_id).first()
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"department{department_id} not found ")
    return dept

def get_student_or_404(student_id:int, db:Session=Depends(get_db)):
    student=db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"student{student_id} not found")
    return student
#--department endpoint---
@app.post("/departments", response_model=DepartmentResponse, status_code=201)
def create_department(dept: DepartmentCreate, db: Session = Depends(get_db)):

    new_dept = Department(**dept.model_dump())
    db.add(new_dept)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Department already exists")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    db.refresh(new_dept)
    return new_dept

@app.get("/departments", response_model=List[DepartmentResponse])
def get_departments(db:Session = Depends(get_db)):
    return db.query(Department).all()

@app.get("/departments/{department_id}", response_model=DepartmentResponse)
def get_department(dept:Department = Depends(get_department_or_404)):
    return dept

@app.delete("/departments/{department_id}", response_model=DepartmentResponse)
def get_department(dept:Department=Depends(get_department_or_404), db:Session = Depends(get_db)):
    db.delete(dept)
    db.commit()
    return dept


#students endpoints
@app.post("/students", response_model=StudentResponse, status_code= status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    dept=db.query(Department).filter(Department.id == student.department_id).first()
    if not dept:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND)
    existing=db.query(Student).filter(Student.email == student.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    new_student=Student(**student.model_dump())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@app.get("/students", response_model= List[StudentResponse])
def get_students(db:Session = Depends(get_db)):
    return db.query(Student).all()

@app.get("/students/{student_id}", response_model= StudentResponse)
def get_student(student:Student = Depends(get_student_or_404)):
    return student

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student: Student= Depends(get_student_or_404), db:Session = Depends(get_db)):
    db.delete(student)
    db.commit()
    

@app.put("/students/{student_id}", response_model= StudentResponse)
def updata_student(
    data:StudentCreate,
    student: Student = Depends(get_student_or_404),
    db:Session = Depends(get_db)
):
    student.name = data.name
    student.age = data.age
    student.email = data.email
    student.department_id = data.department_id
    db.commit()
    db.refresh(student)
    return student
#grade endpoints 
@app.post("/students/{student_id}/grades",
          response_model=GradeResponse,
          status_code=status.HTTP_201_CREATED)
def add_grade(
    grade: GradeCreate,
    student: Student = Depends(get_student_or_404),
    db: Session = Depends(get_db)
):
    new_grade = Grade(student_id=student.id, **grade.model_dump())
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    return new_grade
#special endpoints
@app.get("/departments/{department_id}/students", response_model= List[StudentResponse])#first request hits the route and then it receives department_id. and here itself we declared how response would be like
def get_students_by_department(dept:Department= Depends(get_department_or_404), db:Session = Depends(get_db)):#we create department, before that it has to satisfy all dependencies just to begin the stuff. and then it creates second dependency as db session 
    return db.query(Student).filter(Student.department_id == dept.id).all()#now after creating session, now it's time to search via query and then it filters out the required stuff. (all() means all items that matches the conditions)
#after all of this it returns the stuff. for ex: Request
 #→ extract department_id
 # call get_department_or_404()
  #get dept object
  #create DB session
 #→ run query
 # return students
  #convert to StudentResponse
 #→ send JSON
#basic query request stuff function 
@app.get("/top-students")
def get_top_students(db: Session = Depends(get_db)):
    results = (
        db.query(
            Student.name,
            func.round(func.avg(Grade.score), 2).label('avg_score')
        )
        .join(Grade).group_by(Student.name).order_by(func.avg(Grade.score).desc()).limit(5).all()
    )
    return [{"name": name, "avg_score": float(avg)} for name, avg in results]

