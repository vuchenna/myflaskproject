from flask import render_template, redirect, url_for, request
from application import app, db, bcrypt
from application.models import Users, Upload
from application.forms import RegistrationForm, LoginForm, UploadForm, SearchForm
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home(): 
     return render_template('home.html', title='Home')

@app.route('/music', methods=['GET', 'POST'])
def music():
    form = SearchForm()
    uploads = Upload.query.all()

    if form.validate_on_submit():
        search_data = "%s"%(form.search.data)
        results = Upload.query.filter(Upload.title.like("%"+search_data+"%")).all()
        form = SearchForm()


        return render_template('music.html', title = "Your Search Results", form=form, results =results, uploads=uploads)


    return render_template('music.html', title='Music', uploads=uploads, form=form)



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
        return redirect(url_for('view'))
    else:
        print(form.errors)

    return render_template('upload.html', title ='Upload', form=form)


@app.route('/view', methods=['GET','POST'])
@login_required
def view():
    id = current_user.id
    viewData = Upload.query.filter_by(user_id=id).all()


    return render_template('view.html', title ='View',uploads = viewData )

@app.route('/upload/update/<id>',methods=['GET', 'POST'])
@login_required
def update(id):
    update_form = UploadForm()
    upload = Upload.query.filter_by(id=id).first()
    if update and update_form.validate_on_submit():
        upload.title = update_form.title.data
        upload.category = update_form.category.data
        upload.link = update_form.link.data
        db.session.add(upload)
        db.session.commit()
        return redirect(url_for('view'))
    update_form.title.data = upload.title
    update_form.category.data = upload.category
    update_form.link.data = upload.link
    return render_template('upload.html', title = "Upload", form = update_form)

@app.route('/upload/delete/<id>')
@login_required
def upload_delete(id):
    upload = Upload.query.filter_by(id=id).first()
    db.session.delete(upload)
    db.session.commit()
    return redirect(url_for('view'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



#@app.route('/search_results', methods=['GET', 'POST'])
#def search_results():
   
