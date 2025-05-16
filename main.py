import binary
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_gravatar import Gravatar
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor
from datetime import date
from form import RegisterForm, LoginForm, CommentForm, PostForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from functools import wraps
from flask import abort
import gunicorn
import os

#FLASK_KEY='8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

app = Flask(__name__)
app.config['SECRET_KEY'] = app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)




class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="parent_post")

class User(UserMixin,db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    # Child relationship:"users.id" The users refers to the tablename of the User class.
    # "comments" refers to the comments property in the User class.
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    # Child Relationship to the BlogPosts
    post_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")


with app.app_context():
    db.create_all()

# Create an admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    # TODO: Query the database for all the posts. Convert the data to a python list.
    return render_template("index.html", all_posts=posts, current_user=current_user)

@app.route('/post/<int:post_id>',  methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()

    # Only allow logged-in users to comment on posts
    if form.validate_on_submit():
        print("Comment form submited")
        if not current_user.is_authenticated:
            print("User not authenticated for comment")
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
    print("Going to return render")
    return render_template("post.html", post=requested_post, current_user=current_user, form=form)


@app.route('/edit_post', methods=["GET","POST"])
def edit_post():
    form = PostForm()
    post_id = request.args.get('post_id')
    post_selected = db.get_or_404(BlogPost, post_id)
    if form.validate_on_submit():
        post_selected.body=form.body.data
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("edit-post.html",post=post_selected, form=form, current_user=current_user)


@app.route('/delete', methods=["GET","POST"])
@admin_only
def delete():
    post_id = request.args.get('post_id')
    post_selected = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_selected)
    db.session.commit()
    return redirect(url_for('get_all_posts'))



# TODO: add_new_post() to create a new blog post
@app.route('/new_post', methods=["GET","POST"])
@admin_only
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        new_blog_post = BlogPost(
        title=form.title.data,
        subtitle=form.subtitle.data,
        date=date.today().strftime("%B %d,%Y"),
        body=form.body.data,
        author=current_user,
        img_url=form.img_url.data
        )
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=form,current_user=current_user)


# TODO: edit_post() to change an existing blog post

# TODO: delete_post() to remove a blog post from the database

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/contact")
def contact():
    return render_template("contact.html", current_user=current_user)


@app.route('/register',methods=["GET","POST"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        name_n = form.name.data
        email_n = form.email.data
        result = db.session.execute(db.select(User).where(User.email == email_n))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        password_n = generate_password_hash(request.form["password"], method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            name=name_n,
            email=email_n,
            password=password_n

        )

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login',methods=["GET","POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again.")
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template("login.html",form=form, current_user=current_user)

@app.route('/logout',methods=["GET","POST"])
def logout():
    print(current_user.id)
    logout_user()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=False)