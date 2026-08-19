from fastapi import FastAPI, HTTPException
from fastapi import Header
from pydantic import BaseModel
from fastapi.responses import FileResponse
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app = FastAPI()


# =========================
# USERS
# =========================

class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str

# MongoDB connection
client = MongoClient("mongodb+srv://sudeshnashetty_db_user:68Vym45ZiCQLLz0g@cluster0.teg5rdn.mongodb.net/?appName=Cluster0")
db = client["college_db"]
print(client.admin.command("ping"))
# =========================
# USERS COLLECTION
# =========================

users_collection = db["users"]
def get_current_user(username: str = Header(...)):
    return username
@app.post("/register")
def register_user(user: UserRegister):

    existing_user = users_collection.find_one(
        {"username": user.username}
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    users_collection.insert_one(
        user.model_dump()
    )

    return {
        "message": "User registered successfully"
    }


@app.post("/login")
def login_user(user: UserLogin):

    existing_user = users_collection.find_one(
        {
            "username": user.username,
            "password": user.password
        }
    )

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    return {
        "message": "Login successful",
        "username": user.username
    }

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
def create_student(
    student: Student,
    username: str = Header(...)
):
    # Generate Student ID for the logged-in user
    last_student = students_collection.find_one(
        {"username": username},
        sort=[("student_id", -1)]
    )

    if last_student:
        student.student_id = last_student["student_id"] + 1
    else:
        student.student_id = 1

    student_data = student.model_dump()

    # Connect this student record to the logged-in user
    student_data["username"] = username

    students_collection.insert_one(student_data)

    return student


@app.get("/students")
def get_students(
    username: str = Header(...)
):
    return list(
        students_collection.find(
            {"username": username},
            {"_id": 0, "username": 0}
        )
    )


@app.get("/students/{id}")
def get_student(id: int):
    student = students_collection.find_one(
        {"student_id": id},
        {"_id": 0}
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


@app.put("/students/{id}")
def update_student(
    id: int,
    student: Student,
    username: str = Header(...)
):

    updated_data = student.model_dump()
    updated_data["student_id"] = id
    updated_data["username"] = username

    result = students_collection.update_one(
        {
            "student_id": id,
            "username": username
        },
        {
            "$set": updated_data
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


@app.delete("/students/{id}")
def delete_student(
    id: int,
    username: str = Header(...)
):

    result = students_collection.delete_one(
        {
            "student_id": id,
            "username": username
        }
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {
        "message": "Student deleted successfully"
    }

class Teacher(BaseModel):
    teacher_id: int = 0
    name: str
    subject: str
    department: str


teachers_collection = db["teachers"]


@app.post("/teachers")
def create_teacher(teacher: Teacher):
    # Generate the next unique Teacher ID
    last_teacher = teachers_collection.find_one(
        {},
        sort=[("teacher_id", -1)]
    )

    if last_teacher:
        teacher.teacher_id = last_teacher["teacher_id"] + 1
    else:
        teacher.teacher_id = 1

    teachers_collection.insert_one(teacher.model_dump())

    return teacher


@app.get("/teachers")
def get_teachers():
    teachers = list(
        teachers_collection.find().sort("teacher_id", 1)
    )

    next_id = 1

    for teacher in teachers:
        # Give old teachers a Teacher ID if they don't have one
        if "teacher_id" not in teacher:
            teacher["teacher_id"] = next_id

            teachers_collection.update_one(
                {"_id": teacher["_id"]},
                {"$set": {"teacher_id": next_id}}
            )

        next_id = max(next_id, teacher["teacher_id"] + 1)

    # Hide MongoDB's internal _id
    for teacher in teachers:
        teacher.pop("_id", None)

    return teachers


@app.get("/teachers/{id}")
def get_teacher(id: int):
    teacher = teachers_collection.find_one(
        {"teacher_id": id},
        {"_id": 0}
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    return teacher


@app.put("/teachers/{id}")
def update_teacher(id: int, teacher: Teacher):

    # Keep the original Teacher ID
    updated_data = teacher.model_dump()
    updated_data["teacher_id"] = id

    result = teachers_collection.update_one(
        {"teacher_id": id},
        {"$set": updated_data}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    return updated_data


@app.delete("/teachers/{id}")
def delete_teacher(id: int):

    result = teachers_collection.delete_one(
        {"teacher_id": id}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    return {
        "message": "Teacher deleted successfully"
    }

class Course(BaseModel):
    course_id: int = 0
    name: str
    code: str
    department: str


courses_collection = db["courses"]


# =========================
# CREATE COURSE
# =========================

@app.post("/courses")
def create_course(
    course: Course,
    username: str = Header(...)
):

    # Generate the next Course ID for this user
    last_course = courses_collection.find_one(
        {"username": username},
        sort=[("course_id", -1)]
    )

    if last_course:
        course.course_id = last_course["course_id"] + 1
    else:
        course.course_id = 1

    course_data = course.model_dump()
    course_data["username"] = username

    courses_collection.insert_one(course_data)

    return course


# =========================
# VIEW COURSES
# =========================

@app.get("/courses")
def get_courses(
    username: str = Header(...)
):

    courses = list(
        courses_collection.find(
            {"username": username}
        ).sort("course_id", 1)
    )

    # Hide MongoDB's internal _id and username
    for course in courses:
        course.pop("_id", None)
        course.pop("username", None)

    return courses


# =========================
# GET ONE COURSE
# =========================

@app.get("/courses/{id}")
def get_course(
    id: int,
    username: str = Header(...)
):

    course = courses_collection.find_one(
        {
            "course_id": id,
            "username": username
        },
        {
            "_id": 0,
            "username": 0
        }
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return course


# =========================
# UPDATE COURSE
# =========================

@app.put("/courses/{id}")
def update_course(
    id: int,
    course: Course,
    username: str = Header(...)
):

    updated_data = course.model_dump()
    updated_data["course_id"] = id
    updated_data["username"] = username

    result = courses_collection.update_one(
        {
            "course_id": id,
            "username": username
        },
        {
            "$set": updated_data
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return course


# =========================
# DELETE COURSE
# =========================

@app.delete("/courses/{id}")
def delete_course(
    id: int,
    username: str = Header(...)
):

    result = courses_collection.delete_one(
        {
            "course_id": id,
            "username": username
        }
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return {
        "message": "Course deleted successfully"
    }

class Department(BaseModel):
    department_id: int = 0
    name: str
    code: str


departments_collection = db["departments"]


# =========================
# CREATE DEPARTMENT
# =========================

@app.post("/departments")
def create_department(
    department: Department,
    username: str = Header(...)
):

    # Generate the next Department ID for this user
    last_department = departments_collection.find_one(
        {"username": username},
        sort=[("department_id", -1)]
    )

    if last_department:
        department.department_id = (
            last_department["department_id"] + 1
        )
    else:
        department.department_id = 1

    department_data = department.model_dump()
    department_data["username"] = username

    departments_collection.insert_one(department_data)

    return department


# =========================
# VIEW DEPARTMENTS
# =========================

@app.get("/departments")
def get_departments(
    username: str = Header(...)
):

    departments = list(
        departments_collection.find(
            {"username": username}
        ).sort("department_id", 1)
    )

    # Hide MongoDB's internal _id and username
    for department in departments:
        department.pop("_id", None)
        department.pop("username", None)

    return departments


# =========================
# GET ONE DEPARTMENT
# =========================

@app.get("/departments/{id}")
def get_department(
    id: int,
    username: str = Header(...)
):

    department = departments_collection.find_one(
        {
            "department_id": id,
            "username": username
        },
        {
            "_id": 0,
            "username": 0
        }
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department


# =========================
# UPDATE DEPARTMENT
# =========================

@app.put("/departments/{id}")
def update_department(
    id: int,
    department: Department,
    username: str = Header(...)
):

    updated_data = department.model_dump()
    updated_data["department_id"] = id
    updated_data["username"] = username

    result = departments_collection.update_one(
        {
            "department_id": id,
            "username": username
        },
        {
            "$set": updated_data
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department


# =========================
# DELETE DEPARTMENT
# =========================

@app.delete("/departments/{id}")
def delete_department(
    id: int,
    username: str = Header(...)
):

    result = departments_collection.delete_one(
        {
            "department_id": id,
            "username": username
        }
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return {
        "message": "Department deleted successfully"
    }

class Attendance(BaseModel):
    attendance_id: int = 0
    student_id: int
    date: str
    status: str


attendance_collection = db["attendance"]


# =========================
# CREATE ATTENDANCE
# =========================

@app.post("/attendance")
def create_attendance(
    record: Attendance,
    username: str = Header(...)
):

    # Check whether the student belongs to this user
    if students_collection.count_documents(
        {
            "student_id": record.student_id,
            "username": username
        }
    ) == 0:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Generate the next Attendance ID for this user
    last_record = attendance_collection.find_one(
        {"username": username},
        sort=[("attendance_id", -1)]
    )

    if last_record:
        record.attendance_id = (
            last_record["attendance_id"] + 1
        )
    else:
        record.attendance_id = 1

    attendance_data = record.model_dump()
    attendance_data["username"] = username

    attendance_collection.insert_one(
        attendance_data
    )

    return record


# =========================
# VIEW ATTENDANCE
# =========================

@app.get("/attendance")
def get_attendance(
    username: str = Header(...)
):

    records = list(
        attendance_collection.find(
            {"username": username}
        ).sort("attendance_id", 1)
    )

    valid_records = []

    for record in records:

        # Check whether the student belongs to this user
        student_exists = students_collection.count_documents(
            {
                "student_id": record["student_id"],
                "username": username
            }
        ) > 0

        # Skip attendance records of deleted students
        if not student_exists:
            continue

        # Hide MongoDB internal ID and username
        record.pop("_id", None)
        record.pop("username", None)

        valid_records.append(record)

    return valid_records


# =========================
# UPDATE ATTENDANCE
# =========================

@app.put("/attendance/{id}")
def update_attendance(
    id: int,
    record: Attendance,
    username: str = Header(...)
):

    # Check whether the student belongs to this user
    if students_collection.count_documents(
        {
            "student_id": record.student_id,
            "username": username
        }
    ) == 0:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    updated_data = record.model_dump()
    updated_data["attendance_id"] = id
    updated_data["username"] = username

    result = attendance_collection.update_one(
        {
            "attendance_id": id,
            "username": username
        },
        {
            "$set": updated_data
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Attendance record not found"
        )

    return record

# =========================
# MARKS
# =========================

class Marks(BaseModel):
    marks_id: int = 0
    student_id: int
    subject: str
    marks: int


marks_collection = db["marks"]


# =========================
# CREATE MARKS
# =========================

@app.post("/marks")
def create_marks(
    record: Marks,
    username: str = Header(...)
):

    # Check whether the student belongs to this user
    if students_collection.count_documents(
        {
            "student_id": record.student_id,
            "username": username
        }
    ) == 0:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Prevent duplicate marks for the same student
    # and subject for this user
    existing_record = marks_collection.find_one(
        {
            "student_id": record.student_id,
            "subject": record.subject,
            "username": username
        }
    )

    if existing_record:
        raise HTTPException(
            status_code=400,
            detail="Marks already exists for this student and subject."
        )

    # Generate the next Marks ID for this user
    last_record = marks_collection.find_one(
        {"username": username},
        sort=[("marks_id", -1)]
    )

    if last_record:
        record.marks_id = last_record["marks_id"] + 1
    else:
        record.marks_id = 1

    marks_data = record.model_dump()
    marks_data["username"] = username

    marks_collection.insert_one(marks_data)

    return record


# =========================
# VIEW MARKS
# =========================

@app.get("/marks")
def get_marks(
    username: str = Header(...)
):

    records = list(
        marks_collection.find(
            {"username": username}
        ).sort("marks_id", 1)
    )

    valid_records = []

    for record in records:

        # Check whether the student still exists
        # and belongs to this user
        student_exists = students_collection.count_documents(
            {
                "student_id": record["student_id"],
                "username": username
            }
        ) > 0

        # Do not display marks of deleted students
        if not student_exists:
            continue

        # Hide MongoDB internal ID and username
        record.pop("_id", None)
        record.pop("username", None)

        valid_records.append(record)

    return valid_records


# =========================
# UPDATE MARKS
# =========================

@app.put("/marks/{id}")
def update_marks(
    id: int,
    record: Marks,
    username: str = Header(...)
):

    # Check whether the student belongs to this user
    if students_collection.count_documents(
        {
            "student_id": record.student_id,
            "username": username
        }
    ) == 0:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Keep the original Marks ID
    updated_data = record.model_dump()
    updated_data["marks_id"] = id
    updated_data["username"] = username

    result = marks_collection.update_one(
        {
            "marks_id": id,
            "username": username
        },
        {
            "$set": updated_data
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Marks record not found"
        )

    return record
    

