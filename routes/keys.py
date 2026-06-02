import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from web.auth import login_required
from bot.services.firebase_service import FirebaseService
from bot.config import SUBJECTS
from shared.firebase_config import get_db

keys_bp = Blueprint('keys', __name__)

@keys_bp.route('/keys')
@login_required
def keys_list():
    teacher_id = session.get('teacher_id')
    subject_ids = session.get('teacher_subjects', [])
    
    db = get_db()
    all_keys = []
    
    for subject_id in subject_ids:
        docs = db.collection('activation_keys').where('subject_id', '==', subject_id).stream()
        for doc in docs:
            key = doc.to_dict()
            key['id'] = doc.id
            
            if key.get('student_tg_id'):
                student_doc = db.collection('students').document(str(key['student_tg_id'])).get()
                student_data = student_doc.to_dict() if student_doc.exists else {}
                key['student_name'] = student_data.get('full_name', f"ID: {key['student_tg_id']}")
            else:
                key['student_name'] = None
                
            all_keys.append(key)
    
    return render_template('keys.html', 
                         keys=all_keys,
                         subjects=SUBJECTS)

@keys_bp.route('/keys/create', methods=['GET', 'POST'])
@login_required
def create_key():
    teacher_id = session.get('teacher_id')
    subject_ids = session.get('teacher_subjects', [])
    
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        
        if subject_id not in subject_ids:
            flash('У вас нет доступа к этому предмету!', 'error')
            return redirect(url_for('keys.keys_list'))
        
        key_code = FirebaseService.create_key(subject_id, teacher_id)
        flash(f'Ключ {key_code} создан! Ученик активирует сам в боте.', 'success')
        
        return redirect(url_for('keys.keys_list'))
    
    return render_template('keys.html',
                         subjects={k: v for k, v in SUBJECTS.items() if k in subject_ids})

@keys_bp.route('/keys/unbind/<key_code>', methods=['POST'])
@login_required
def unbind_key(key_code):
    key = FirebaseService.get_key(key_code)
    if not key or key.get('subject_id') not in session.get('teacher_subjects', []):
        flash('Ключ не найден или нет доступа!', 'error')
        return redirect(url_for('keys.keys_list'))
    
    FirebaseService.unbind_key(key_code)
    flash(f'Ключ {key_code} отвязан от ученика!', 'success')
    return redirect(url_for('keys.keys_list'))