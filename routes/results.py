import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

from flask import Blueprint, render_template, session
from web.auth import login_required
from bot.services.firebase_service import FirebaseService
from bot.config import SUBJECTS
from shared.firebase_config import get_db

results_bp = Blueprint('results', __name__)

@results_bp.route('/results/<subject_id>')
@login_required
def results_list(subject_id):
    teacher_id = session.get('teacher_id')
    subject = SUBJECTS.get(subject_id, {})

    db = get_db()
    tests = []
    docs = db.collection('tests').where('subject_id', '==', subject_id).where('teacher_id', '==', teacher_id).stream()
    for doc in docs:
        test = doc.to_dict()
        test['id'] = doc.id
        tests.append(test)
    
    test_ids = [t.get('id') for t in tests]

    all_answers = []
    for test_id in test_ids:
        answers = []
        answers_docs = db.collection('answers').where('test_id', '==', test_id).stream()
        for ans_doc in answers_docs:
            ans = ans_doc.to_dict()
            ans['id'] = ans_doc.id
            answers.append(ans)
        all_answers.extend(answers)

    # Группируем по ученикам с именами
    students_results = {}
    for answer in all_answers:
        tg_id = answer.get('student_tg_id')
        
        student_doc = db.collection('students').document(str(tg_id)).get()
        student_data = student_doc.to_dict() if student_doc.exists else {}
        full_name = student_data.get('full_name', f"ID: {tg_id}")
        first_name = student_data.get('first_name', '')
        last_name = student_data.get('last_name', '')
        
        if tg_id not in students_results:
            students_results[tg_id] = {
                'tg_id': tg_id,
                'full_name': full_name,
                'first_name': first_name,
                'last_name': last_name,
                'answers': [],
                'correct': 0,
                'total': 0
            }
        students_results[tg_id]['answers'].append(answer)
        students_results[tg_id]['total'] += 1
        if answer.get('is_correct'):
            students_results[tg_id]['correct'] += 1

    return render_template('results.html',
                         subject=subject,
                         subject_id=subject_id,
                         students=list(students_results.values()))