from flask import render_template, redirect, url_for, request
from application import app, db, bcrypt
from application.models import Users, Upload
from application.forms import RegistrationForm, LoginForm, UploadForm
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home(): 
     return render_template('home.html', title='Home')

@app.route('/music')
def music():
    return render_template('music.html', title='Music')



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if current_user.is_authenticated:
            return redirect(url_for('home'))

        user = Users(first_name=form.first_name.data, last_name =form.last_name.data, email=form.email.data,  password=hash_pw)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('music'))
    return render_template('register.html', title ='Register', form=form)




@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))

    return render_template('login.html', title ='Login', form=form)


@app.route('/upload', methods=['GET','POST'])
@login_required

def upload():
    form = UploadForm()
    if form.validate_on_submit():
        uploadData = Upload(
                title=form.title.data,
                category=form.category.data,
                link=form.link.data,
                creator=current_user

            )
        db.session.add(uploadData)
        db.session.commit()
        return redirect(url_for('music'))
    else:
        print(form.errors)

    return render_template('upload.html', title ='Upload', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
