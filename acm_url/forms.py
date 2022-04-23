from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Regexp, Optional, InputRequired

class CreateForm(FlaskForm):
  vanity = StringField('Custom vanity (optional)', validators=[Optional(), Regexp('^[\w-]+$', message="Short name must only containt letters, digits, and dashes.")])
  url = StringField('Enter long URL to make short', validators=[DataRequired(message="A URL was not entered.")])
  committee = SelectField('Committee', choices=[('Studio'), ('ICPC'), ('Design'), ('Cyber'), ('TeachLA'), ('w'), ('ai'),('Hack')])
  poc = StringField('Name', validators=[DataRequired(message="Please enter your name.")])
  submit = SubmitField('Make URL')

class EditForm(FlaskForm):
  url = StringField('Enter new URL for this vanity', validators=[DataRequired(message="A URL was not entered.")])
  poc = StringField('Enter new name for this vanity', validators=[DataRequired(message="A name was not entered.")])
  committee = SelectField('Committee', choices=[('Studio'), ('ICPC'), ('Design'), ('Cyber'), ('TeachLA'), ('w'), ('ai'),('Hack')])
  submit = SubmitField('Edit URL')

class PasswordForm(FlaskForm):
  password = PasswordField('Password', validators=[InputRequired(message="You must submit the password to create an URL.")])
  submit = SubmitField('Submit')