from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Regexp, Optional, InputRequired

class CreateForm(FlaskForm):
  vanity = StringField('Custom vanity (optional)', validators=[Optional(), Regexp('^[\w-]+$', message="Short name must only containt letters, digits, and dashes.")])
  url = StringField('Enter long URL to make short', validators=[DataRequired(message="A URL was not entered.")])
  submit = SubmitField('Make URL')

class PasswordForm(FlaskForm):
  password = PasswordField('Password', validators=[InputRequired(message="You must submit the password to create an URL.")])
  submit = SubmitField('Submit')