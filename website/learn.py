from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from .forms import QuestionForm, ThemeForm
from .models import Question, User, Theme, Lesson
from . import db


learn = Blueprint('learn', __name__)


@learn.route('/clasa<int:page_id>')
@login_required
def classes(page_id):
    lessons= Lesson.query.filter_by().all()
    return render_template(f'pages/invata/clase_mate/clasa{page_id}.html', page_id=page_id, lessons=lessons)


@learn.route('/clasa<int:page_id>/capitol-<int:capitol_id>/<lesson>', methods=['POST', 'GET'])
@login_required
def lessons(page_id, capitol_id, lesson):
    try:
        forms = []
        image = None
        # Get all the questions for the particular lesson id
        questions = Question.query.filter_by(lesson_id=lesson, user_id=current_user.id).all()
        theme_form = ThemeForm()
        theme = Theme.query.filter_by(lesson_id=lesson, name='Minecraft').first()
        
        if theme_form.validate_on_submit():
            theme = Theme.query.filter_by(lesson_id=lesson, name=theme_form.themes.data).first()
        
        image = (theme.name + '.jpg').lower()
        for i in range(0, len(questions)):
            forms.append(QuestionForm(prefix=f'question_{i}'))
        
        for i in range(0, len(forms)):
            if not questions[i].completed:
                
                if forms[i].validate_on_submit() and forms[i].question.data == questions[i].answer:
                    questions[i].completed = True
                    user = User.query.get(current_user.id)
                    user.correct_answers += 1
                    user.experience += 10
                    user.daily_experience += 10
                    user.daily_correct_answers += 1
                    user.update_streak()
                    user.award_badge()
                    user.check_quests()
                    user.level_up()
                    db.session.commit()
            forms[i].question.data = ''
        
        return render_template(f'pages/invata/clase_mate/lectii_mate/capitol{capitol_id}/lectia1.html',
                    page_id=page_id,capitol_id=capitol_id,lesson=lesson, forms=forms, questions=questions, text=theme.content,
                    theme_form=theme_form, title='Lectie', img=image)
    except:
        return redirect(url_for('learn.classes', page_id=page_id))
    
