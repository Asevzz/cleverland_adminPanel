import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from web.config import SECRET_KEY
from web.auth import verify_teacher
from web.routes import dashboard_bp, tests_bp, results_bp, keys_bp
from bot.services.firebase_service import FirebaseService

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.secret_key = SECRET_KEY

# Регистрация blueprints
app.register_blueprint(dashboard_bp)
app.register_blueprint(tests_bp, url_prefix='/tests')
app.register_blueprint(results_bp, url_prefix='/results')
app.register_blueprint(keys_bp, url_prefix='/keys')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        teacher = verify_teacher(login, password)

        if teacher:
            session['teacher_id'] = teacher.get('id')
            session['teacher_login'] = teacher.get('login')
            session['teacher_subjects'] = teacher.get('subjects', [])
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Неверный логин или пароль!', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/init-admin')
def init_admin():
    """Инициализация администратора (выполнить один раз)"""
    from web.config import ADMIN_USERNAME, ADMIN_PASSWORD
    from werkzeug.security import generate_password_hash

    # Проверяем, есть ли уже админ
    admin = FirebaseService.get_teacher(ADMIN_USERNAME)
    if admin:
        return "Администратор уже существует!"

    # Создаём администратора
    from shared.firebase_config import get_db
    db = get_db()
    db.collection('teachers').document('admin_001').set({
        'id': 'admin_001',
        'login': ADMIN_USERNAME,
        'password_hash': generate_password_hash(ADMIN_PASSWORD),
        'subjects': ['history_belarus', 'english', 'society'],
        'role': 'admin',
        'created_at': __import__('datetime').datetime.now()
    })

    return f"Администратор создан!\nЛогин: {ADMIN_USERNAME}\nПароль: {ADMIN_PASSWORD}"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
