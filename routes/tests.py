import sys
sys.path.insert(0, '/mnt/agents/output/cleverland')

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from web.auth import login_required
from bot.services.firebase_service import FirebaseService
from bot.config import SUBJECTS
from shared.firebase_config import get_db

tests_bp = Blueprint('tests', __name__)

@tests_bp.route('/tests/<subject_id>')
@login_required
def tests_list(subject_id):
    teacher_id = session.get('teacher_id')
    subject = SUBJECTS.get(subject_id, {})

    # Получаем ВСЕ тесты преподавателя по предмету (без фильтра по части)
    db = get_db()
    tests = []
    docs = db.collection('tests').where('subject_id', '==', subject_id).where('teacher_id', '==', teacher_id).stream()
    for doc in docs:
        test = doc.to_dict()
        test['id'] = doc.id
        tests.append(test)

    return render_template('tests_list.html', 
                         subject=subject, 
                         subject_id=subject_id,
                         tests=tests)

@tests_bp.route('/tests/<subject_id>/create', methods=['GET', 'POST'])
@login_required
def create_test(subject_id):
    teacher_id = session.get('teacher_id')
    subject = SUBJECTS.get(subject_id, {})

    if request.method == 'POST':
        title = request.form.get('title')
        part = request.form.get('part')
        questions_data = []

        # Обрабатываем вопросы
        question_count = int(request.form.get('question_count', 0))

        for i in range(question_count):
            q_text = request.form.get(f'question_{i}_text')
            q_type = request.form.get(f'question_{i}_type')
            q_part = request.form.get(f'question_{i}_part', part)

            question = {
                'index': i,
                'text': q_text,
                'type': q_type,
                'part': q_part,
                'image_url': None
            }

            if q_type == 'choice':
                options = []
                for j in range(4):
                    opt = request.form.get(f'question_{i}_option_{j}')
                    if opt:
                        options.append(opt)
                question['options'] = options
                question['correct_option'] = int(request.form.get(f'question_{i}_correct', 0))
                question['correct_text'] = None
            else:
                question['options'] = []
                question['correct_option'] = None
                question['correct_text'] = request.form.get(f'question_{i}_correct_text', '')

            questions_data.append(question)

        # Сохраняем тест
        test_id = f"test_{teacher_id}_{subject_id}_{part}_{int(__import__('time').time())}"

        db = get_db()
        db.collection('tests').document(test_id).set({
            'id': test_id,
            'teacher_id': teacher_id,
            'subject_id': subject_id,
            'part': part,
            'title': title,
            'questions': questions_data,
            'is_active': True,
            'created_at': __import__('datetime').datetime.now()
        })

        flash('Тест успешно создан!', 'success')
        return redirect(url_for('tests.tests_list', subject_id=subject_id))

    return render_template('test_edit.html', 
                         subject=subject, 
                         subject_id=subject_id,
                         test=None)

@tests_bp.route('/tests/<subject_id>/edit/<test_id>', methods=['GET', 'POST'])
@login_required
def edit_test(subject_id, test_id):
    teacher_id = session.get('teacher_id')
    subject = SUBJECTS.get(subject_id, {})
    test = FirebaseService.get_test(test_id)

    if not test or test.get('teacher_id') != teacher_id:
        flash('Тест не найден или нет доступа!', 'error')
        return redirect(url_for('tests.tests_list', subject_id=subject_id))

    if request.method == 'POST':
        # Обновляем тест
        title = request.form.get('title')
        is_active = request.form.get('is_active') == 'on'

        db = get_db()
        db.collection('tests').document(test_id).update({
            'title': title,
            'is_active': is_active
        })

        flash('Тест обновлён!', 'success')
        return redirect(url_for('tests.tests_list', subject_id=subject_id))

    return render_template('test_edit.html', 
                         subject=subject, 
                         subject_id=subject_id,
                         test=test)

@tests_bp.route('/tests/<subject_id>/delete/<test_id>', methods=['POST'])
@login_required
def delete_test(subject_id, test_id):
    teacher_id = session.get('teacher_id')
    test = FirebaseService.get_test(test_id)

    if not test or test.get('teacher_id') != teacher_id:
        flash('Тест не найден или нет доступа!', 'error')
        return redirect(url_for('tests.tests_list', subject_id=subject_id))

    db = get_db()
    db.collection('tests').document(test_id).delete()

    flash('Тест удалён!', 'success')
    return redirect(url_for('tests.tests_list', subject_id=subject_id))