from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from pymongo import MongoClient

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb+srv://sudeshnashetty_db_user:68Vym45ZiCQLLz0g@cluster0.teg5rdn.mongodb.net/?appName=Cluster0")
db = client["college_db"]
print(client.admin.command("ping"))

@app.get("/")
def home():
    return FileResponse("index.html")


class Student(BaseModel):
    student_id: int = 0
    name: str
    age: int
    course: str
    department: str


students_collection = db["students"]


@app.post("/students")
def create_student(student: Student):
    student.student_id = students_collection.count_documents({}) + 1
    students_collection.insert_one(student.model_dump())
    return student


@app.get("/students")
def get_students():
    return list(students_collection.find({}, {"_id": 0}))


@app.get("/students/{id}")
def get_student(id: int):
    student = students_collection.find_one(
        {"student_id": id},
        {"_id": 0}
    )

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@app.put("/students/{id}")
def update_student(id: int, student: Student):
    result = students_collection.update_one(
        {"student_id": id},
        {"$set": student.model_dump()}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@app.delete("/students/{id}")
def delete_student(id: int):
    result = students_collection.delete_one({"student_id": id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student deleted successfully"}

class Teacher(BaseModel):
    name: str
    subject: str
    department: str


teachers_collection = db["teachers"]


@app.post("/teachers")
def create_teacher(teacher: Teacher):
    teacher_data = teacher.dict()
    result = teachers_collection.insert_one(teacher_data)
    teacher_data["_id"] = str(result.inserted_id)
    return teacher_data


@app.get("/teachers")
def get_teachers():
    teachers = list(teachers_collection.find())
    for teacher in teachers:
        teacher["_id"] = str(teacher["_id"])
    return teachers


@app.get("/teachers/{id}")
def get_teacher(id: str):
    from bson import ObjectId

    teacher = teachers_collection.find_one({"_id": ObjectId(id)})

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher["_id"] = str(teacher["_id"])
    return teacher


@app.put("/teachers/{id}")
def update_teacher(id: str, teacher: Teacher):
    from bson import ObjectId

    result = teachers_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": teacher.dict()}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher_data = teacher.dict()
    teacher_data["_id"] = id
    return teacher_data


@app.delete("/teachers/{id}")
def delete_teacher(id: str):
    from bson import ObjectId

    result = teachers_collection.delete_one(
        {"_id": ObjectId(id)}
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Teacher not found")

    return {"message": "Teacher deleted successfully"}

class Course(BaseModel):
    name: str
    code: str
    department: str


courses_collection = db["courses"]


@app.post("/courses")
def create_course(course: Course):
    course_data = course.dict()
    result = courses_collection.insert_one(course_data)
    course_data["_id"] = str(result.inserted_id)
    return course_data


@app.get("/courses")
def get_courses():
    courses = list(courses_collection.find())
    for course in courses:
        course["_id"] = str(course["_id"])
    return courses


@app.get("/courses/{id}")
def get_course(id: str):
    from bson import ObjectId

    course = courses_collection.find_one({"_id": ObjectId(id)})

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course["_id"] = str(course["_id"])
    return course


@app.put("/courses/{id}")
def update_course(id: str, course: Course):
    from bson import ObjectId

    result = courses_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": course.dict()}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Course not found")

    course_data = course.dict()
    course_data["_id"] = id
    return course_data


@app.delete("/courses/{id}")
def delete_course(id: str):
    from bson import ObjectId

    result = courses_collection.delete_one(
        {"_id": ObjectId(id)}
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Course not found")

    return {"message": "Course deleted successfully"}

class Department(BaseModel):
    name: str
    code: str


departments_collection = db["departments"]


@app.post("/departments")
def create_department(department: Department):
    department_data = department.dict()
    result = departments_collection.insert_one(department_data)
    department_data["_id"] = str(result.inserted_id)
    return department_data


@app.get("/departments")
def get_departments():
    departments = list(departments_collection.find())
    for department in departments:
        department["_id"] = str(department["_id"])
    return departments


@app.get("/departments/{id}")
def get_department(id: str):
    from bson import ObjectId

    department = departments_collection.find_one(
        {"_id": ObjectId(id)}
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    department["_id"] = str(department["_id"])
    return department


@app.put("/departments/{id}")
def update_department(id: str, department: Department):
    from bson import ObjectId

    result = departments_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": department.dict()}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    department_data = department.dict()
    department_data["_id"] = id
    return department_data


@app.delete("/departments/{id}")
def delete_department(id: str):
    from bson import ObjectId

    result = departments_collection.delete_one(
        {"_id": ObjectId(id)}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return {"message": "Department deleted successfully"}

class Attendance(BaseModel):
    student_id: int
    date: str
    status: str


attendance_collection = db["attendance"]


@app.post("/attendance")
def create_attendance(record: Attendance):
    if students_collection.count_documents(
        {"student_id": record.student_id}
    ) == 0:
        raise HTTPException(
            status_code=404,
            detail="Student ID does not exist"
        )

    attendance_data = record.dict()
    result = attendance_collection.insert_one(attendance_data)

    attendance_data["_id"] = str(result.inserted_id)
    return attendance_data


@app.get("/attendance")
def get_attendance():
    records = list(attendance_collection.find())

    for record in records:
        record["_id"] = str(record["_id"])

    return records


@app.put("/attendance/{id}")
def update_attendance(id: str, record: Attendance):
    if students_collection.count_documents(
        {"student_id": record.student_id}
    ) == 0:
        raise HTTPException(
            status_code=404,
            detail="Student ID does not exist"
        )

    from bson import ObjectId

    result = attendance_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": record.dict()}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Attendance record not found"
        )

    attendance_data = record.dict()
    attendance_data["_id"] = id

    return attendance_data

class Marks(BaseModel):
    student_id: int
    subject: str
    marks: int


marks_collection = db["marks"]


@app.post("/marks")
def create_marks(record: Marks):
    if marks_collection.count_documents(
        {"student_id": record.student_id}
    ) >= 0:
        if students_collection.count_documents(
            {"student_id": record.student_id}
        ) == 0:
            raise HTTPException(
                status_code=404,
                detail="Student ID does not exist"
            )

    marks_collection.insert_one(record.model_dump())
    return record


@app.get("/marks")
def get_marks():
    marks = list(marks_collection.find({}, {"_id": 0}))
    return marks


@app.put("/marks/{id}")
def update_marks(id: str, record: Marks):
    if students_collection.count_documents(
        {"student_id": record.student_id}
    ) == 0:
        raise HTTPException(
            status_code=404,
            detail="Student ID does not exist"
        )

    from bson import ObjectId

    result = marks_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": record.model_dump()}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Marks record not found"
        )

    return record

