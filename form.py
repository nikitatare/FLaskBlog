from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


class PostForm(FlaskForm):
    title = StringField('The blog post title')
    subtitle = StringField('The subtitle')
    author = StringField('The authors name')
    img_url = StringField('Image URL')
    body =  CKEditorField('Body')
    submit = SubmitField('Submit')

class EditPostForm(FlaskForm):
    body =  CKEditorField('Body')
    submit = SubmitField('Submit')
# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    name = StringField("NAME", validators=[DataRequired()])
    email = StringField("EMAIL", validators=[DataRequired()])
    password = StringField("PASSWORD", validators=[DataRequired()])
    submit = SubmitField("Register")


# TODO: Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = StringField("EMAIL", validators=[DataRequired()])
    password = StringField("PASSWORD", validators=[DataRequired()])
    submit = SubmitField("Login")

# TODO: Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Comment")