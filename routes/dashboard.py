import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

from flask import Blueprint, render_template, session
from web.auth import login_required
from bot.config import SUBJECTS

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def dashboard():
    teacher_subjects = session.get('teacher_subjects', [])

    # Теперь словарь: {subject_id: {name, type, parts}}
    subjects_data = {}
    for subject_id in teacher_subjects:
        subject_info = SUBJECTS.get(subject_id, {})
        subjects_data[subject_id] = {
            'id': subject_id,
            'name': subject_info.get('name', subject_id),
            'type': subject_info.get('type', 'ct').upper(),
            'parts': subject_info.get('parts', [])
        }

    return render_template('dashboard.html', subjects=subjects_data)