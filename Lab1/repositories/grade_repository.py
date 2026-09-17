from models.grade import Grade, db

def get_all():
    return Grade.query.all()

def add(student_name, subject, score):
    new_grade = Grade(student_name=student_name, subject=subject, score=score)
    db.session.add(new_grade)
    db.session.commit()

def delete_by_id(grade_id):
    grade = db.session.get(Grade, grade_id) if hasattr(db.session, 'get') else Grade.query.get(grade_id)
    if grade:
        db.session.delete(grade)
        db.session.commit()
