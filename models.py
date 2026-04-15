from sqlalchemy import String, Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class Department(Base):
    __tablename__ = "departments"

    id      : Mapped[int]   = mapped_column(Integer, primary_key=True)
    name     : Mapped[str]   = mapped_column(String(100),unique=True)

    #relationship
    students : Mapped[list["Student"]] = relationship("Student", back_populates="department")

    def __repr__(self):
        return f"Department(name={self.name})"
    

class Student(Base):
    __tablename__ = "students"

    id       : Mapped[int]      = mapped_column(Integer, primary_key=True)
    name     : Mapped[str]       = mapped_column(String(100), unique=True)
    age      : Mapped[int]       = mapped_column(Integer)
    email    : Mapped[str]      = mapped_column(String, unique=True)
    department_id : Mapped[int]      = mapped_column(Integer, ForeignKey("departments.id"))

    #relationships
    department        : Mapped["Department"] = relationship("Department", back_populates="students")
    grades            : Mapped[list["Grade"]] = relationship("Grade", back_populates="student")

    def __repr__(self):
        return f"Student(name={self.name}, email={self.email})"
    

class Grade(Base):
    __tablename__ = "grades"

    id        : Mapped[int]      = mapped_column(Integer ,primary_key=True)
    student_id : Mapped[int]      = mapped_column(Integer, ForeignKey("students.id"))
    subject      : Mapped[str]      = mapped_column(String(100))
    score     : Mapped[int]         = mapped_column(Numeric(asdecimal=False))

    #relationship
    student      : Mapped["Student"]     = relationship("Student", back_populates="grades")

    def __repr__(self):
        return f"Grade(subject={self.subject}, score={self.score})"

