from flask import render_template, redirect, url_for, request
from application import app, db, bcrypt
from application.models import Users, Upload, SavedSong
from application.forms import RegistrationForm, LoginForm, UploadForm, SearchForm, UpdateAccountForm
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

@app.route('/music/add/<id>', methods=['GET', 'POST'])
@login_required
def add(id):
    saved_song = SavedSong.query.filter_by(user_id=current_user.id, song_id=id).first()
    if saved_song:
        print('song is already saved')
        return redirect(url_for('view'))
    saved_song = SavedSong(user_id=current_user.id, song_id=id)
    db.session.add(saved_song)
    db.session.commit()
    return redirect(url_for('view'))


@app.route('/music/remove/<id>', methods=['GET', 'POST'])
@login_required
def remove(id):
    return "Cannot remove songs that isnt owned by you. Try uploading a new song"

@app.route('/view', methods=['GET','POST'])
@login_required
def view():
    user = Users.query.filter_by(id=current_user.id).first()
    saved_songs = SavedSong.query.filter_by(user_id=user.id).all()
    uploads = []
    for saved_song in saved_songs:
        upload = Upload.query.filter_by(id=saved_song.song_id).first()
        uploads.append(upload)
    songs = user.upload + uploads
    return render_template('view.html', title ='View',uploads = songs )

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
    if current_user.id != upload.user_id:
        return redirect(url_for('view'))
    db.session.delete(upload)
    saved_songs = SavedSong.query.filter_by(song_id=id).all()
    for saved_song in saved_songs:
        db.session.delete(saved_song)
    db.session.commit()
    return redirect(url_for('view'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



#@app.route('/search_results', methods=['GET', 'POST'])
#def search_results()



@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form_email.data
        db.session.commit()
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)
