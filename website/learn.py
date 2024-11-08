from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from .forms import QuestionForm
from .models import Question, User
from . import db


learn = Blueprint('learn', __name__)


@learn.route('/clasa<int:page_id>')
@login_required
def classes(page_id):
    return render_template(f'pages/invata/clase_mate/clasa{page_id}.html', page_id=page_id)


@learn.route('/clasa<int:page_id>/capitol-<int:capitol_id>/<lesson>', methods=['POST', 'GET'])
@login_required
def lessons(page_id, capitol_id, lesson):
    try:

        forms = []
        
        # Get all the questions for the particular lesson id
        questions = Question.query.filter_by(lesson_id=lesson, user_id=current_user.id).all()
        
        for i in range(0, len(questions)):
            forms.append(QuestionForm(prefix=f'question_{i}'))
        
        for i in range(0, len(forms)):
            if not questions[i].completed:
                
                print(questions[i])
                if forms[i].validate_on_submit() and forms[i].question.data == questions[i].answer:
                    questions[i].completed = True
                    user = User.query.get(current_user.id)
                    user.correct_answers += 1
                    db.session.commit()
                    user.update_streak()
            forms[i].question.data = ''
        
        return render_template(f'pages/invata/clase_mate/lectii_mate/capitol{capitol_id}/lectia{lesson}.html',
                    page_id=page_id,capitol_id=capitol_id,lesson=lesson, forms=forms, questions=questions)
    except:
        return redirect(url_for('learn.classes', page_id=page_id))
    
