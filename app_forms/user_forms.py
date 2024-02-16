from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, PasswordField, EmailField, FileField, SelectField, BooleanField
from wtforms.validators import DataRequired,Length 

class Login_Form(FlaskForm):
    user_name = StringField('user_name', validators=[DataRequired()], render_kw={"placeholder": "Enter Username", "autofocus": "true"})
    forgot_password = BooleanField('forgot_password')
    password = PasswordField('password', validators=[DataRequired()], render_kw={"placeholder": "Enter Password"})
    submit = SubmitField('Login')

class Disable_Account_Form(FlaskForm):
    user_id = IntegerField('user_id', render_kw={"type": "hidden"})
    submit = SubmitField('Disable')

class Update_Profile(FlaskForm):
    user_name = StringField('username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    email = EmailField('email', validators=[DataRequired()], render_kw={"placeholder": "Email"})
    main_image = FileField('profile picture')
    password = PasswordField('password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('confirm_password', validators=[DataRequired()], render_kw={"placeholder": "confirm password"})
    submit = SubmitField('Update')

class Registeration_Form(FlaskForm):
    first_name = StringField('first_name', validators=[DataRequired()], render_kw={'maxlength': 10, "placeholder": "Enter your First Name", "autofocus": "true"})
    last_name = StringField('last_name', validators=[DataRequired()], render_kw={'maxlength': 10, "placeholder": "Enter Last Name"})
    surname = StringField('surname',  validators=[DataRequired()], render_kw={'maxlength': 10, "placeholder": "Enter Surname"})
    user_name = StringField('user_name', validators=[DataRequired()], render_kw={'maxlength': 50, "placeholder": "Enter User Name"})
    email = EmailField('email',  validators=[DataRequired()], render_kw={'maxlength': 50, "placeholder": "Enter your Email"})
    password = PasswordField('password',  validators=[DataRequired(), Length(min=4 , max=21)], render_kw={"placeholder": "Enter your Password "})
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(), Length(min=4, max=21)], render_kw={"placeholder": "Confirm_Password"})
    phone_number = StringField('phone_number', validators=[DataRequired()], render_kw={'maxlength': 10, "placeholder": "Enter your Contact"})
    main_image = FileField('main_image', validators=[DataRequired()])
    

    role_choices = [
        ('', 'Select a Role'),
        ('Agent', 'Merchant'),
        ('Handy Man', 'Handy Man'),
        ('Service Provider', 'Service Provider'),
        ('Employer', 'Employer'),
        ('Experimental', 'Experimental'),
        ('Job Agency', 'Job Agency'),
    ]

    role = SelectField('Role', choices=role_choices)

    gender_choices = [
        ('', 'Select a Gender'),
        ('female', 'Female'),
        ('male', 'Male')
    ]

    gender = SelectField('Gender', choices=gender_choices)

    country_choices = [
        ('', 'Select a Country'),
        ('south africa', 'South Africa'),
        ('nigeria', 'Nigeria'),
        ('egypt', 'Egypt'),
        ('kenya', 'Kenya'),
        ('morocco', 'Morroco'),
        ('ghana', 'Ghana'),
        ('algeria', 'Algeria'),
        ('ethiopia', 'Ethiopia'),
        ('tanzania', 'Tanzania'),
        ('uganda', 'Uganda'),
        ('zimbabwe', 'Zimbabwe'),
    ]

    country = SelectField('Country', choices=country_choices)
    social_media_links = StringField('social_media_links', validators=[DataRequired()], render_kw={'maxlength': 100, "placeholder": "Enter your Social Links"})
    bio = TextAreaField('bio', validators=[DataRequired()], render_kw={'maxlength': 256, "placeholder": "Enter your Bio"})

    submit = SubmitField('Register')