from repositories.grade_repository import get_all, add, delete_by_id

def list_grades():
    return get_all()

def create_grade(student_name, subject, score):
    add(student_name, subject, score)

def delete_grade(grade_id):
    delete_by_id(grade_id)