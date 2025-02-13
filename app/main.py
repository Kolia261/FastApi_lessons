from json_db_lite import JSONDatabase
from fastapi import FastAPI, HTTPException
from datetime import date
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from enum import Enum

# Определяем перечисление для специальностей
class Major(str, Enum):
    computer_science = "Computer Science"
    mathematics = "Mathematics"
    physics = "Physics"
    chemistry = "Chemistry"
    biology = "Biology"
    engineering = "Engineering"
    literature = "Literature"
    history = "History"
    economics = "Economics"

# Инициализация объекта
small_db = JSONDatabase(file_path='students.json')

# Получаем все записи
def json_to_dict_list():
    return small_db.get_all_records()

# Добавляем студента
def add_student(student: dict):
    student['date_of_birth'] = student['date_of_birth'].strftime('%Y-%m-%d')
    small_db.add_records(student)
    return True

# Обновляем данные по студенту
def upd_student(upd_filter: dict, new_data: dict):
    small_db.update_record_by_key(upd_filter, new_data)
    return True

# Удаляем студента
def dell_student(key: str, value: str):
    small_db.delete_record_by_key(key, value)
    return True

class Student(BaseModel):
    student_id: int
    phone_number: str = Field(default=..., description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(default=..., min_length=1, max_length=50, description="Имя студента, от 1 до 50 символов")
    last_name: str = Field(default=..., min_length=1, max_length=50, description="Фамилия студента, от 1 до 50 символов")
    date_of_birth: date = Field(default=..., description="Дата рождения студента в формате ГГГГ-ММ-ДД")
    email: EmailStr = Field(default=..., description="Электронная почта студента")
    address: str = Field(default=..., min_length=10, max_length=200, description="Адрес студента, не более 200 символов")
    enrollment_year: int = Field(default=..., ge=2002, description="Год поступления должен быть не меньше 2002")
    major: Major = Field(default=..., description="Специальность студента")
    course: int = Field(default=..., ge=1, le=5, description="Курс должен быть в диапазоне от 1 до 5")
    special_notes: Optional[str] = Field(default=None, max_length=500,
                                   description="Дополнительные заметки, не более 500 символов")

class SUpdateFilter(BaseModel):
    student_id: int

# Определение модели для новых данных студента
class SStudentUpdate(BaseModel):
    course: int = Field(..., ge=1, le=5, description="Курс должен быть в диапазоне от 1 до 5")
    major: Optional[Major] = Field(..., description="Специальность студента")

class SDeleteFilter(BaseModel):
    key: str
    value: Any

app = FastAPI()

@app.post("/add_student")
def add_student_handler(student: Student):
    student_dict = student.dict()
    check = add_student(student_dict)
    if check:
        return {"message": "Студент успешно добавлен!"}
    else:
        return {"message": "Ошибка при добавлении студента"}

@app.put("/update_student")
def update_student_handler(filter_student: SUpdateFilter, new_data: SStudentUpdate):
    check = upd_student(filter_student.dict(), new_data.dict())
    if check:
        return {"message": "Информация о студенте успешно обновлена!"}
    else:
        raise HTTPException(status_code=400, detail="Ошибка при обновлении информации о студенте")

@app.delete("/delete_student")
def delete_student_handler(filter_student: SDeleteFilter):
    check = dell_student(filter_student.key, filter_student.value)
    if check:
        return {"message": "Студент успешно удален!"}
    else:
        raise HTTPException(status_code=400, detail="Ошибка при удалении студента")
