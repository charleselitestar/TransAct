from flask_login import UserMixin
from . import db

class LastLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    last_login = db.Column(db.Date)
    user_name = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(100))
    action_date = db.Column(db.Date)
    action_time = db.Column(db.Time)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    user_name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100))
    password = db.Column(db.String(60), nullable=False)
    phone_number = db.Column(db.String(20))
    main_image = db.Column(db.String(100))
    registration_date = db.Column(db.Date)
    registration_time = db.Column(db.Time)
    status = db.Column(db.String(50))
    online_status =  db.Column(db.String(50))
    role = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    country = db.Column(db.String(200))
    currency = db.Column(db.String(100))
    currency_symbol = db.Column(db.String(5))
    social_media_links = db.Column(db.String(200))
    bio = db.Column(db.Text)

class User_FullProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(100))
    surname = db.Column(db.String(50))
    id_number = db.Column(db.Integer)
    province = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    user_name = db.Column(db.String(20), unique=True, nullable=False)
    main_image = db.Column(db.String(100))
    registration_date = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(100))
    country = db.Column(db.String(200))
    social_media_links = db.Column(db.String(200))
    bio = db.Column(db.Text)
    billing_city = db.Column(db.String(50))
    billing_street = db.Column(db.String(50))
    billing_state = db.Column(db.String(50))
    billing_country = db.Column(db.String(50))
    billing_email = db.Column(db.String(50))
    billing_organization = db.Column(db.String(50))
    billing_contact1 = db.Column(db.String(50))
    billing_contact2 = db.Column(db.String(50))
    billing_house = db.Column(db.String(20))
    billing_suburb = db.Column(db.String(20))
    availability = db.Column(db.String(50))
    preferred_location = db.Column(db.String(50))
    description = db.Column(db.Text)
    education = db.Column(db.String(50))
    school = db.Column(db.String(50))
    qualification = db.Column(db.String(100))
    skill1 = db.Column(db.String(50))
    skill2 = db.Column(db.String(50))
    skill3 = db.Column(db.String(50))
    skill4 = db.Column(db.String(50))
    additional_skills = db.Column(db.Text)
    reference0_name = db.Column(db.String(50))
    reference0_title = db.Column(db.String(50))
    reference0_organization = db.Column(db.String(50))
    reference0_contact = db.Column(db.String(50))
    reference0_email = db.Column(db.String(50))
    reference0_duration = db.Column(db.String(50))
    reference0_duty = db.Column(db.Text)
    reference0_description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Group_Members(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    joined_group = db.Column(db.String(100), nullable=False)
    group_role = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Completed_Applications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    contact_number = db.Column(db.String(50))
    contact_email = db.Column(db.String(50))
    id_number = db.Column(db.String(50))
    availability = db.Column(db.String(50))
    billing_street = db.Column(db.String(100))
    billing_city = db.Column(db.String(50))
    billing_state = db.Column(db.String(50))
    billing_postal_code = db.Column(db.String(20))
    billing_country = db.Column(db.String(50))
    application_date = db.Column(db.Date)
    application_time = db.Column(db.Time)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class UserContacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    phone_number = db.Column(db.Integer)
    message = db.Column(db.Text)
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_header = db.Column(db.String(20))
    sender = db.Column(db.String(100))
    recipient = db.Column(db.String(100))
    short_text = db.Column(db.Text)
    text = db.Column(db.Text)
    datestamp = db.Column(db.Date)
    timestamp = db.Column(db.Time)
    recipient_id = db.Column(db.Integer)
    status = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, message_header ,sender, recipient,short_text, text, datestamp, timestamp, recipient_id , status, user_id):
        self.message_header = message_header
        self.sender = sender
        self.recipient = recipient
        self.short_text = short_text
        self.text = text
        self.datestamp = datestamp
        self.timestamp = timestamp
        self.recipient_id = recipient_id
        self.status = status
        self.user_id = user_id