from flask import Flask, render_template, url_for, redirect
from data import db_session
from data.jobs import Jobs
from data.users import User
from flask_login import LoginManager, login_manager
from flask_login import login_user, logout_user, current_user
from forms.login import LoginForm
from flask_login import login_required
from forms.add_job import AddJob
from flask import session
from forms.reg_form import Reg_form



app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Reg_form()
    if form.validate_on_submit():
        user = User(surname=form.surname.data, name=form.name.data, age=form.age.data,
                    position=form.position.data, speciality=form.speciality.data, address=form.address.data,
                    email=form.login_or_email.data, hashed_password=form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/work/<int:job_id>', methods=['GET', 'POST'])
@login_required
def change(job_id):
    form = AddJob()
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
    if form.validate_on_submit():
        print('Сохраняю...')
        job.job = form.job.data
        job.team_leader = form.team_leader.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        db_sess.commit()
        return redirect('/')
    if job:
        form.job.data = job.job
        form.team_leader.data = job.team_leader
        form.work_size.data = job.work_size
        form.collaborators.data = job.collaborators
        form.is_finished.data = job.is_finished
        return render_template('add_job.html', form=form, title='Редактирование работы')
    return redirect('/')

@app.route('/work_delete/<int:job_id>', methods=['GET', 'POST'])
@login_required
def delete_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
    if job:
        db_sess.delete(job)
        db_sess.commit()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.hashed_password == form.password.data:
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/')
def index():
    jobs = db_sess.query(Jobs).all()
    return render_template('index.html', jobs=jobs)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_job():
    form = AddJob()
    if form.validate_on_submit():
        job = Jobs(team_leader=form.team_leader.data, job=form.job.data, work_size=form.work_size.data,
                   collaborators=form.collaborators.data, is_finished=form.is_finished.data)
        db_sess.add(job)
        db_sess.commit()
        return redirect('/')
    return render_template("add_job.html", form=form, title='Добавление работы')


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    db_sess = db_session.create_session()
    app.run(port=8080, host='127.0.0.1')
