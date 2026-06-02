import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

from functools import wraps
from flask import session, redirect, url_for, request
from werkzeug.security import check_password_hash, generate_password_hash

# Исправленный импорт
try:
    from bot.services.firebase_service import FirebaseService
except ImportError:
    # Альтернатива для Render
    import firebase_admin
    from firebase_admin import firestore
    
    class FirebaseService:
        @staticmethod
        def get_teacher(login):
            db = firestore.client()
            doc = db.collection('teachers').document(login).get()
            return doc.to_dict() if doc.exists else None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'teacher_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def verify_teacher(login, password):
    """Проверить логин и пароль преподавателя"""
    teacher = FirebaseService.get_teacher(login)
    if teacher and check_password_hash(teacher.get('password_hash', ''), password):
        return teacher
    return None
