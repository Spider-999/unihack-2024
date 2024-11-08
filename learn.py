from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import User, Question
from .forms import QuestionForm # type: ignore
from . import db

learn= Blueprint('learn', __name__)

@learn.route('/clasa<int:page_id>')
@login_required
def classes(page_id):
    return render_template(f'pages/invata/clase_mate/clasa{page_id}.html', page_id= page_id)

@learn.route('/clasa<int:page_id>/capitol-<int:capitol_id>/<lesson>', methods=["GET", "POST"])
@login_required
def lessons(page_id, capitol_id, lesson):
    try:
        forms= []
        
        questions= Question.query.filter_by(lesson_id= lesson, user_id= current_user.id).all()
        
        for i in range(0, len(questions)):
            forms.append(QuestionForm(prefix=f"question_{i}"))
        
        for i in range(0, len(forms)):
            if not questions[i].completed:
                print(questions[i])
                
                if(forms[i].validate_on_submit() and forms[i].question.data== questions[i]):
                    questions[i].completed= True
                    user= User.query.filter_by(current_user.id)
                    user.correct_answers+=1
                    db.session.commit()
                    user.update_streak()
                    
                forms[i].question.data= ''
            
        return render_template('pages/invata/clase_mate/lectii_mate/capitol{capitol_id}/lectia{lesson}.html',
                                   page_id= page_id, capitol_id= capitol_id, lesson= lesson, questions = questions, forms= forms)
   
    except:
        return redirect(url_for('learn.classes', page_id= page_id))