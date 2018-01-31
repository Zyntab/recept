from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Användarnamn eller email',
                           validators=[DataRequired(message='Du måste ange ett användarnamn')])
    password = PasswordField('Lösenord',
                             validators=[DataRequired(message='Du måste ange ett lösenord')])
    remember_me = BooleanField('Kom ihåg mig')
    submit = SubmitField('Logga in')

class RegistrationForm(FlaskForm):
    username = StringField('Användarnamn',
                           validators=[DataRequired(message='Du måste ange ett användarnamn')])
    email = StringField('Email',
                        validators=[DataRequired(message='Du måste ange en email-adress'),
                                    Email(message='Detta verkar inte vara en email-adress')])
    password = PasswordField('Lösenord',
                             validators=[DataRequired(message='Du måste ange ett lösenord')])
    password2 = PasswordField('Upprepa lösenord',
                              validators=[DataRequired(message='Måste vara ifyllt'),
                                          EqualTo('password',
                                                  message='Lösenordet måste skrivas likadant två gånger')])
    submit = SubmitField('Registrera')

    def validate_username(self, username):
        if '@' in username.data:
            raise ValidationError('Användarnamnet får inte innehålla "@".')
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Användarnamnet är upptaget. Välj ett annat.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Det finns redan en användare med den email-adressen.')

class EditProfileForm(FlaskForm):
    username = StringField('Användarnamn',
                           validators=[DataRequired(
                               message='Måste vara ifyllt')])
    submit = SubmitField('Spara')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Användarnamnet är upptaget. Vänligen välj ett annat.')

class RecipeForm(FlaskForm):
    name = StringField('Namn',
                       validators=[DataRequired(
                           message='Du måste ge receptet ett namn')])
    notes = TextAreaField('Anteckningar')
    submit = SubmitField('Spara')
