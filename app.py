import time
from threading import Thread
from ast import With
from email.mime import application
from locale import currency
from jinja2.exceptions import TemplateNotFound 
from flask import Flask, render_template, make_response, abort
from flask_login import (LoginManager,login_user,login_required,logout_user,current_user,)
from sqlalchemy import desc
from werkzeug.exceptions import abort
from flask import request, redirect, url_for, flash, session 
from flask_socketio import SocketIO, send, emit
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate, current
from flask_limiter.util import get_remote_address
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import date, datetime
import random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.sql import func
import io
import getpass
import secrets
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from flask_limiter import Limiter
import base64
from weasyprint import HTML
from app_forms.user_forms import Login_Form,Registeration_Form, Disable_Account_Form,Update_Profile
from app_forms import Recharge_Tokens_Form, Instant_PayCode, Recharge_Form,Redeem_Paycode, Pay_Someone, Confirm_Payment, Withdraw_Funds_Form, Confirm_Withdrawal, Load_Account
from app_forms import App_Account_Fees,Account_limits, Collect_Funds_Form

from app_config.config import Config, logger

from app_modules import country_currency, user_accounts, merchant_accounts, collect_funds, account_notification_message
from app_modules import withdraw, withdraw_user_funds, confirm_withdrawal, account_charges
from app_modules import initialize_root, template_charges, recharge_account
from app_modules import paycode_notification_message, withdrawal_notification_message, recharge_notification_message
from app_modules import new_message_alert, paycode_charges, payment_charges, pay

app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)

hashed_password = os.environ.get("APP_PASSWORD")
if not hashed_password:
    print("Please set the environment variable 'APP_PASSWORD_HASH' to start the app.")
    exit()

entered_password = getpass.getpass("Enter the app password: ").encode('utf-8')
if not bcrypt.check_password_hash(hashed_password, entered_password):
    print("Incorrect password. Exiting.")
    exit()

# Initialize extensions
login_manager = LoginManager(app)
from app_models import db
db.init_app(app)
migrate = Migrate(app, db)
limiter = Limiter(app)
mail = Mail(app)
socketio = SocketIO(app)
Base = declarative_base()

from app_models.user import LastLogin, User, User_FullProfile, Group_Members, Completed_Applications, UserContacts, Message
from app_models import Accounts,Recipients,Deposits,Withdrawals,Payments,Transactions,Recharge_Tokens,Redeemed_Tokens,Withdraw_Codes,Withdrawn_Funds,Fees,Limits

with app.app_context():
    db.create_all()

#################################################################################################################################################3#####
    
def get_current_balance():
    user_id = current_user.id
    account = Accounts.query.filter_by(user_id=user_id).first()
    if account:
        account_balance = account.account_balance
        return account_balance
    return None

def get_previous_balance():
    user_id = current_user.id
    account = Accounts.query.filter_by(user_id=user_id).first()
    if account:
        previous_balance = account.previous_balance
        return previous_balance
    return None

@socketio.on('update_balance')
def amount_update(amount):
    sid = request.get('sid')
    new_balance = get_current_balance()
    emit('update_balance', {'amount': new_balance}, room=current_user.id, namespace='sid')
    print('balance has changed')

    # Sleep for a short interval before checking again
    time.sleep(20)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )

# -------------------------------------------app start login, register and profile management-----------------------------------------------#
@app.route("/", methods=["GET", "POST"])
def index():
    page_name = "EliteDocs"
    return render_template("app_templates/index.html", page_name=page_name)

@app.route("/elitedocs_website", methods=['GET', 'POST'])
def elite_website():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        message = request.form.get('message')

        new_contact = UserContacts(
            first_name = first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            message=message,
        )
        db.session.add(new_contact)
        db.session.commit()
        return render_template('website/contact_success.html')
    
    return render_template('website/elitedocs_website.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    page_name = "login"
    max_login_attempts = 3

    form = Login_Form()
    if request.method == "POST" and form.validate_on_submit():
        user_name = form.user_name.data

        forgot_password = request.form.get("forgot_password")
        if forgot_password:
            return redirect(url_for("forgot_password"))
        password = form.password.data
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            flash("user does not exist ! Register Instead")
            return redirect(url_for('login'))

        status = user.status
        if status != 'active':
            page_name = 'Disabled Account'
            flash("account has been disabled")
            return render_template('admin/disabled.html', page_name=page_name)

        if user and bcrypt.check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_name"] = user.user_name
            session["first_name"] = user.first_name
            session["last_login"] = last_login = datetime.now()
            session.pop('login_attempts', None) 
            action = "login"
            action_done = datetime.now()
            action_date = action_done.date()
            action_time = action_done.time()
            last_log = LastLogin(
                last_login=last_login,
                user_name=user_name,
                action=action,
                action_date=action_date,
                action_time=action_time,
                user_id=user.id,
            )
            db.session.add(last_log)
            user.online_status = 'online'
            db.session.commit()
            login_user(user)
            logger.info(f"{user.role} {user_name} logged in at {datetime.now()}")

            return redirect(url_for("menu"))
        else:
            # Incorrect login attempt
            flash("Login failed. Please check your username and password.", "danger")
            if 'login_attempts' in session:
                session['login_attempts'] += 1
            else:
                session['login_attempts'] = 1

            # Check if the maximum login attempts have been reached
            if session['login_attempts'] >= max_login_attempts:
                return disable_account(user_name)
            return redirect(url_for("login"))

    return render_template("app_templates/login.html", page_name=page_name, form=form)

def disable_account(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    if not user:
        return redirect(url_for('/'))
    user.status = 'disabled'
    db.session.commit()
    return render_template('admin/disabled.html')
    
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    page_name = "reset password"

    if request.method == "POST":
        account_first_name = request.form.get('first_name')
        account_last_name = request.form.get('last_name')
        account_email = request.form.get('email')
        user_name = request.form.get("user_name")

        existing_user = User.query.filter_by(user_name=user_name).first()

        if not existing_user:
            flash("Invalid username.")
            return redirect(url_for("login"))

        confirm_first_name = existing_user.first_name
        confirm_last_name = existing_user.last_name
        confirm_email = existing_user.email
        confirm_user_name = existing_user.user_name

        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if (
            account_first_name == confirm_first_name and
            account_last_name == confirm_last_name and
            account_email == confirm_email and
            user_name == confirm_user_name
        ):
            if new_password != confirm_password:
                flash("Passwords do not match.")
                return redirect(url_for("forgot_password"))

            hashed_new_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
            existing_user.password = hashed_new_password
            db.session.commit()

            flash("Password reset successfully! You can now log in with your new password.", "success")
            return redirect(url_for("login"))
        else:
            flash("Account information does not match.")
            return redirect(url_for("forgot_password"))

    return render_template("app_templates/forgot_password.html", page_name=page_name)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/register", methods=["GET", "POST"])
def register():
    page_name = "register"
    form = Registeration_Form()
    if request.method == "POST":
        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
        surname = form.surname.data.strip()
        user_name = form.user_name.data.strip()
        email = form.email.data.strip()
        country = form.country.data
        if country:
            country_name = country
            currency_data = country_currency(country_name)
            
            if currency_data:
                currency_name = currency_data.get('name', '')
                currency_symbol = currency_data.get('symbol', '')

        phone_number = form.phone_number.data

        social_media_links = form.social_media_links.data
        bio = form.bio.data
        gender = form.gender.data
        role = form.role.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        if password == confirm_password:
            password = password
        else:
            flash("passwords do not match")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        main_image = form.main_image.data
        if not main_image:
            if gender == "male":
                main_image = "placeholder_male.jpeg"
            elif gender == "female":
                main_image = "placeholder_female.jpeg"
            else:
                # Handle other cases if needed
                main_image = "default_placeholder.jpeg"

        main_image_filename = None

        if (
            main_image
            and isinstance(main_image, FileStorage)
            and allowed_file(main_image.filename)
        ):
            main_image_filename = secure_filename(main_image.filename)
            main_image.save(
                os.path.join(app.root_path, "static", "uploads", main_image_filename)
            )

        registration = datetime.now()
        registration_date = registration.date()
        registration_time = registration.time()

        active = 'active'
        # Check if a user with the same username already exists (you may have to customize this part)
        existing_user = User.query.filter_by(user_name=user_name).first()

        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
        else:
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                surname=surname,
                user_name=user_name,
                email=email,
                phone_number=phone_number,
                main_image=main_image_filename,
                social_media_links=social_media_links,
                bio=bio,
                gender=gender,
                registration_date=registration_date,
                registration_time=registration_time,
                status=active,
                online_status = 'offline',
                country=country,
                currency=currency_name,
                currency_symbol=currency_symbol,
                role=role,
                password=hashed_password,
            )
            db.session.add(new_user)
            db.session.commit()

            action = "registration"
            action_done = datetime.now()
            last_login = action_done
            action_date = action_done.date()
            action_time = action_done.time()

            last_log = LastLogin(
                last_login=last_login,
                user_name=user_name,
                action=action,
                action_date=action_date,
                action_time=action_time,
                user_id=new_user.id,
            )
            db.session.add(last_log)
            db.session.commit()

            account_name = first_name
            account_type = role
            account_balance = "0"
            account_pin = hashed_password
            account_status = "active"

            random_account_number = random.randint(1000, 9999)

            now = datetime.now()

            month = now.month
            day = now.day
            week = now.strftime("%U")  # Week number
            hours = now.hour
            minutes = now.minute

            account_number = f"{minutes:02d}{hours:02d}{month:02d}{day:02d}{random_account_number}"

            existing_account = Accounts.query.filter_by(
                account_number=account_number
            ).first()

            while existing_account:
                random_account_number = random.randint(1000, 9999)
                account_number = f"{month:02d}{day:02d}{random_account_number}{week}{hours:02d}{minutes:02d}"
                existing_account = Accounts.query.filter_by(
                    account_number=account_number
                ).first()

            new_account = Accounts(
                account_name=account_name,
                account_type=account_type,
                account_balance=account_balance,
                currency=currency_name,
                currency_symbol=currency_symbol,
                account_number=account_number,
                account_pin=account_pin,
                account_status=account_status,
                creation_date=action_date,
                creation_time=action_time,
                user_id=new_user.id,
            )

            db.session.add(new_account)
            db.session.commit()

            logger.info(f"{role} {user_name} registered at {datetime.now()}")

            flash("Account created successfully!", "success")
            initialize_root()
            return redirect(url_for("login"))

    # If the code reaches here, it means there was an issue with the registration
    # flash('Error: Please enter correct details.', 'error')

    return render_template("app_templates/register.html", page_name=page_name,form=form)


@app.route("/profile", methods=["GET"])
@login_required
def profile():
    user_profile = session.get("first_name")
    page_name = user_profile + "'s Profile"
    code = 'profile_page'
    user_id = session.get("user_id")  # Retrieve the user ID from the session
    if user_id:
        user = User.query.get(user_id)
        last_login = LastLogin.query.filter_by(user_id=user_id).first()
        return render_template(
            "admin/profile.html", user=user, page_name=page_name, last_login=last_login, code=code
        )
    else:
        return redirect("/login")

@app.route("/update_profile", methods=["GET", "POST"])
@login_required
def update_profile():
    user_id = session.get("user_id")  # Retrieve the user ID from the session
    if user_id:
        user = User.query.get(user_id)  # Retrieve the user object from the database
        if request.method == "POST":
            user.name = request.form["name"]
            user.email = request.form["email"]
            password = request.form["password"]
            confirm_password = request.form.get("confirm_password")
            if password != confirm_password:
                flash("Incorrect password")
                return redirect(url_for("profile"))
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            user.password = hashed_password
            db.session.commit()
            db.session.close()
            return redirect("/profile")

        # Now that you have the user object, you can access user.first_name
        page_name = f"Update {user.first_name} profile"
        return render_template(
            "admin/update_profile.html", user=user, page_name=page_name
        )
    else:
        return redirect("/login")

@app.route('/root_admin', methods=['GET','POST'])
@login_required
def root_admin():
        page_name = 'ROOT ADMIN'
        form = Disable_Account_Form()
        if current_user.role != 'Agent' and current_user.user_name != 'EliteTechRoot':
            flash('Access Denied')
            return redirect('/')
        users = User.query.order_by(desc(User.registration_time)).all()
        online_users = (
            User.query.filter(or_(
                User.online_status == 'online',
            )).count()
        )
        disabled_users = (
            User.query.filter(or_(
                User.status == 'disabled',
            )).count()
        )
        user_count = User.query.count()
        url = '/root_admin'
        return render_template('admin/root.html',page_name=page_name,
                               users=users,
                               user_count=user_count, 
                               form=form, 
                               online_users=online_users,
                               disabled_users=disabled_users,
                               url=url)

@app.route("/root_accounts", methods=['GET','POST'])
@login_required
def root_accounts():
    page_name = 'Accounts'
    if current_user.role != 'Agent' and current_user.user_name != 'EliteTechRoot':
        flash('Access Denied')
        return redirect('/')
    accounts = Accounts.query.all()
    active_accounts = (
        Accounts.query.filter(or_(
            Accounts.account_status == 'active',
        )).count()
    )
    disabled_accounts = (
        Accounts.query.filter(or_(
            Accounts.account_status == 'disabled',
        )).count()
    )
    account_count = Accounts.query.count()
    url = '/root_accounts'
    return render_template('admin/root_accounts.html',page_name=page_name,
                           accounts=accounts,
                           account_count=account_count,
                           active_accounts=active_accounts,
                           disabled_accounts=disabled_accounts,
                           url=url,
                           )

@app.route('/disable_user_account/<int:user_id>', methods=['POST'])
@login_required
def disable_user_account(user_id):
    user_to_disable = User.query.get_or_404(user_id)
    if user_to_disable:
        user_to_disable.status = 'disabled'
        user_to_disable.online_status = 'offline'
    db.session.commit()
    flash('User Disabled successfully', 'success')
    return redirect(url_for('root_admin'))

@app.route('/disable_funds_account/<int:account_id>', methods=['POST'])
@login_required
def disable_funds_account(account_id):
    funds_to_disable = Accounts.query.get_or_404(account_id)
    if funds_to_disable:
        funds_to_disable.account_status = 'disabled'
    db.session.commit()
    flash('Account Disabled successfully', 'success')
    return redirect(url_for('root_accounts'))

@app.route('/activate_funds_account/<int:account_id>', methods=['POST'])
@login_required
def activate_funds_account(account_id):
    funds_to_activate = Accounts.query.get_or_404(account_id)
    if funds_to_activate:
        funds_to_activate.account_status = 'active'
    db.session.commit()
    flash('Account Activated successfully', 'success')
    return redirect(url_for('root_accounts'))

@app.route('/delete_account/<int:account_id>', methods=['POST'])
@login_required
def delete_account(account_id):
    account_to_delete = Accounts.query.get_or_404(account_id)
    db.session.delete(account_to_delete)
    db.session.commit()
    flash('Account deleted successfully', 'success')
    return redirect(url_for('root_accounts'))

@app.route('/activate_user_account/<int:user_id>', methods=['POST'])
@login_required
def activate_user_account(user_id):
    user_to_activate = User.query.get_or_404(user_id)
    if user_to_activate:
        user_to_activate.status = 'active'
    db.session.commit()
    flash('User Activated successfully', 'success')
    return redirect(url_for('root_admin'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('root_admin'))

@app.route("/complete_user_profile", methods=["GET", "POST"])
@login_required
def complete_user_profile():
    page_name = "complete profile"
    if request.method == "POST":
        user_id = current_user.id
        first_name = current_user.first_name
        last_name = current_user.last_name
        surname = current_user.surname
        gender = current_user.gender
        id_number = request.form.get("id number")
        registration_date = current_user.registration_date
        registration_time = current_user.registration_time
        account_role = current_user.role
        account_status = current_user.active
        social_media_links = current_user.social_media_links
        bio = current_user.bio
        billing_city = request.form.get("billing_city")
        billing_street = request.form.get("biling_street")
        billing_state = request.form.get("billing_state")
        billing_country = current_user.country
        billing_email = current_user.email
        billing_organization = request.form.get("billing_organization")
        billing_contact1 = current_user.phone_number
        billing_contact2 = request.form.get("billing_contact2")
        billing_house = request.form.get("billing_house")
        billing_suburb = request.form.get("billing_suburb")
        availability = request.form.get("availability")
        preferred_location = request.form.get("preferred_location")
        description = request.form.get("description")
        education = request.form.get("education")
        school = request.form.get("school")
        skill1 = request.form.get("skill1")
        skill2 = request.form.get("skill2")
        skill3 = request.form.get("skill3")
        skill4 = request.form.get("skill4")
        additional_skills = request.form.get("additional_skills")
        reference0_name = request.form.get("reference0_name")
        reference0_title = request.form.get("reference0_title")
        reference0_organization = request.form.get("reference0_organization")
        reference0_contact = request.form.get("reference0_contact")
        reference0_email = request.form.get("reference0_email")
        reference0_duration = request.form.get("reference0_duration")
        reference0_duty = request.form.get("reference0_duty")
        reference0_description = request.form.get("reference0_description")

        qualification = request.files.get("qualification")

        if qualification:
            try:
                # Securely rename the file
                filename = secure_filename(qualification.filename)
                # pdfs.save(qualification, name=filename)

                # Save the filename in your User_FullProfile object
                full_user_profile.qualification = filename
                return "File uploaded successfully"
            except:  # UploadNotAllowed:
                # Handle the case where the file type is not allowed (e.g., not a PDF)
                flash("Invalid file type. Please upload a PDF file.")
        else:
            flash("No file selected")

            full_user_profile = User_FullProfile(
                first_name=first_name,
                last_name=last_name,
                surname=surname,
                gender=gender,
                id_number=id_number,
                registration_date=registration_date,
                registration_time=registration_time,
                account_role=account_role,
                account_status=account_status,
                social_media_links=social_media_links,
                bio=bio,
                billing_city=billing_city,
                billing_street=billing_street,
                billing_state=billing_state,
                billing_country=billing_country,
                billing_email=billing_email,
                billing_organization=billing_organization,
                billing_contact1=billing_contact1,
                billing_contact2=billing_contact2,
                billing_house=billing_house,
                billing_suburb=billing_suburb,
                availability=availability,
                preferred_location=preferred_location,
                description=description,
                education=education,
                school=school,
                qualification=qualification,
                skill1=skill1,
                skill2=skill2,
                skill3=skill3,
                skill4=skill4,
                additional_skills=additional_skills,
                reference0_name=reference0_name,
                reference0_title=reference0_title,
                reference0_organization=reference0_organization,
                reference0_contact=reference0_contact,
                reference0_email=reference0_email,
                reference0_duration=reference0_duration,
                reference0_duty=reference0_duty,
                reference0_description=reference0_description,
            )
            db.session.add(full_user_profile)
            db.session.commit()

    return render_template("admin/full_profile.html", page_name=page_name)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to access this page.", "danger")
    return redirect(url_for("login"))

@app.route("/logout")
@login_required
def logout():
    user = current_user
    user_name = current_user.user_name
    user_id = session.get("user_id")
    logger.info(f"{user.role} {user_name} logged out at {datetime.now()}")
    last_login = session.get("last_login")
    action = "logout"
    action_done = datetime.now()
    action_date = action_done.date()
    action_time = action_done.time()
    last_log = LastLogin(
        last_login=last_login,
        user_name=user_name,
        action=action,
        action_date=action_date,
        action_time=action_time,
        user_id=user_id,
    )
    db.session.add(last_log)
    current_user.online_status = 'offline'
    db.session.commit()
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/menu", methods=["GET", "POST"])
@login_required
def menu():
    user_name = session.get("first_name")
    page_name = user_name + " @ EliteDocs"
    user_role = current_user.role
    if user_role == 'Agent':
        return merchant_accounts()
    return render_template("app_templates/menu.html", page_name=page_name)

@app.route("/account", methods=["GET"])
@login_required
def account():
    user_role = current_user.role
    if user_role == 'Agent':
        return merchant_accounts()
    else:
        return user_accounts()

@app.route("/account_limits")
@login_required
def account_limits():
    form = Account_limits
    withdrawal = form.withdrawal.data
    paycode = form.paycode.data
    payments = form.payments.data
    daily = form.daily.data
    weekly = form.daily.data
    monthly = form.monthly.data

    user_account_limit = Limits(
        withdrawal = withdrawal,
        paycode = paycode,
        payments = payments,
        daily = daily,
        weekly = weekly,
        monthly = monthly,
        user_id = current_user.id
    )
    db.session.begin()
    db.session.add(user_account_limit)
    db.session.commit()

@app.route("/withdraw_funds", methods=['GET', 'POST'])
@login_required
def withdraw_funds():
    user_id = current_user.id
    account = Accounts.query.get(user_id)
    if account.account_status == 'disabled':
        flash('Not Authorised To TransAct')
        if current_user.role == 'Agent':
            return redirect(url_for('menu'))
        return redirect(url_for('account'))    
    return withdraw_user_funds()


@app.route('/confirm_withdrawal', methods=['POST'])
@login_required
def confirm_user_withdrawal():
    form = Confirm_Withdrawal()

    if not current_user.is_authenticated:
        return redirect('login')

    if not form.validate_on_submit():
        # Handle form validation failure, e.g., show an error message
        flash('Withdrawal confirmation failed. Please check your PIN.')
        return redirect('withdraw_funds')

    user_id = current_user.id
    account = Accounts.query.get(user_id)

    if not account:
        flash('Account not found')
        return redirect('withdraw_funds')

    confirm_pin = form.account_pin.data

    return confirm_withdrawal(confirm_pin)


@app.route("/withdrawals", methods=['GET'])
@login_required
def withdrawals():
    page_name = 'withdrawals'
    user_id = current_user.id
    account = Accounts.query.get(user_id)
    account_number = account.account_number
    withdrawals = Withdrawals.query.filter_by(user_id=user_id).order_by(
        Withdrawals.withdraw_date.desc(),
        Withdrawals.withdraw_time.desc(),
    ).all()
    
    if current_user.role == 'Agent':
        page_name = 'merchant withdrawals'
        return render_template("merchant/merchant_withdrawals.html",
                               page_name=page_name,
                               withdrawals=withdrawals,
                               )
    return render_template("funds/withdrawals.html",
                           page_name=page_name,
                           withdrawals=withdrawals,
                           )


@app.route("/deposits", methods=['GET'])
@login_required
def deposits():
    page_name = 'deposits'
    user_id = current_user.id
    account = Accounts.query.get(user_id)
    account_number = account.account_number
    deposits = Deposits.query.filter_by(user_id=user_id).order_by(
        Deposits.deposit_date.desc(),
        Deposits.deposit_time.desc(),
    ).all()

    if current_user.role == 'Agent':
        page_name = 'merchant deposits'
        return render_template("merchant/merchant_deposits.html",
                               page_name=page_name,
                               deposits=deposits,
                               )
    return render_template("funds/deposits.html",
                           page_name=page_name,
                           deposits=deposits,
                           )


@app.route("/collect_funds", methods=["GET", "POST"])
@login_required
def collect_user_funds():
    if current_user.role != 'Agent':
        return redirect(url_for('account'))
    
    user_id = current_user.id
    account = Accounts.query.get(user_id)

    if account.account_status == 'disabled':
        flash('Not Authorised To TransAct')
        return redirect(url_for('account'))
    return collect_funds()

@app.route("/payment_plaque")
@login_required
def payment_plaque():
    user_id = current_user.id
    account = Accounts.query.get(user_id)
    account_name = account.account_name
    account_number = account.account_number
    return render_template("funds/plaque.html",
                           account_name=account_name,
                           account_number=account_number,)

@app.route("/fund_account")
@login_required
def fund_account():
    if request.method == "GET":
        form = Recharge_Form()
        page_name = "fund account"
        user_role = current_user.role
        if user_role == 'Agent':
            page_name = 'recharge'
            return render_template("merchant/recharge.html",page_name=page_name,form=form)
        return render_template("funds/recharge.html",page_name=page_name,form=form)

@app.route("/recharge", methods=["POST"])
@login_required
def recharge():
    return recharge_account()

@app.route("/view_transaction", methods=["GET", "POST"])
@login_required
def view_transaction():
    page_name = "transaction details"
    if request.method == "POST":
        view_transaction = request.form.get("view_transaction")

        transaction = Transactions.query.filter_by(id=view_transaction).first()

    return render_template(
        "funds/view_transaction.html",
        page_name=page_name,
        transaction=transaction,
    )

@app.route("/view_payment", methods=["GET", "POST"])
@login_required
def view_payment():
    page_name = "payment details"
    if request.method == "POST":
        view_payment = request.form.get("view_payment")

        payment = Payments.query.filter_by(id=view_payment).first()

    return render_template(
        "funds/view_payment.html",
        page_name=page_name,
        payment=payment,
    )

@app.route("/view_paycode", methods=["GET", "POST"])
@login_required
def view_paycode():
    page_name = "paycode details"
    if request.method == "POST":
        user_id = current_user.id
        view_paycode = request.form.get("view_paycode")

        paycode = Recharge_Tokens.query.filter_by(id=view_paycode).first()

        total_codes = Recharge_Tokens.query.filter_by(user_id=user_id).count()


        used_codes = Recharge_Tokens.query.filter_by(
                    user_id=user_id,
                    status='invalid'
        ).count()
        valid_codes = Recharge_Tokens.query.filter_by(
                    user_id=user_id,
                    status='Valid'
        ).count()


    return render_template(
        "funds/view_paycode.html",
        page_name=page_name,
        paycode=paycode,
        used_codes=used_codes,
        valid_codes=valid_codes,
        total_codes=total_codes,
    )

@app.route("/payments", methods=["GET","POST"])
@login_required
def payments():
    if request.method == 'GET':
        page_name = "payments"
        user_id = current_user.id
        account = Accounts.query.get(user_id)
        account_balance = account.account_balance
        currency_symbol = account.currency_symbol
        if account_balance < int(1000):
            balance = 'red'
        elif account_balance > int(1000):
            balance = 'green'

        recipients = Recipients.query.filter_by(user_id=user_id).order_by(
            Recipients.creation_date.desc(),
            Recipients.creation_time.desc(),
        ).all()
        form = Pay_Someone()
        return render_template("funds/payments.html",
                               page_name=page_name,
                               account_balance=account_balance,
                               balance=balance,
                               form=form,
                               recipients=recipients,
                               currency_symbol=currency_symbol)
    
    form = Pay_Someone()
    if request.method == 'POST' and form.validate_on_submit():
        user_id = current_user.id
        account = Accounts.query.get(user_id)
        if account.account_status == 'disabled':
            flash('Not Authorised To TransAct')
            if current_user.role == 'Agent':
                return redirect(url_for('menu'))
            return redirect(url_for('account'))
        recipient_account = int(form.account_number.data)
        transaction_amount = int(form.pay_amount.data)
        if transaction_amount < 0:
            flash("enter a valid amount and continue")
            return redirect(url_for('payments'))
        reference = str(form.reference_name.data)
        session['recipient_account'] = recipient_account
        session['transaction_amount'] = transaction_amount
        session['reference'] = reference
        valid_account = Accounts.query.filter_by(account_number=recipient_account).first()
        if not valid_account:
            flash("Invalid account")
            return redirect(url_for("payments"))
        if transaction_amount > int(1000):
            session['recipient_name'] = valid_account.account_name
            return redirect(url_for('confirm_payment'))
    return pay(recipient_account,transaction_amount,reference)

@app.route("/pay_again", methods=['GET', 'POST'])
@login_required
def pay_again():
    if request.method == 'POST':
        user_id = current_user.id
        account = Accounts.query.get(user_id)
        if account.account_status == 'disabled':
            flash('Not Authorised To TransAct')
            if current_user.role == 'Agent':
                return redirect(url_for('menu'))
            return redirect(url_for('account'))
        account_balance = account.account_balance
        transaction_amount = int(request.form.get('transaction_amount'))
        if transaction_amount > account_balance:
            flash('not enouph funds')
            return redirect(url_for('payments'))
        recipient_account = int(request.form.get('recipient_account'))
        recipient_name = request.form.get('recipient_name')
        date = request.form.get('date')
        time = request.form.get('time')

        previous_transaction = Recipients.query.filter_by(account_number = recipient_account,
                                                          account_name = recipient_name,
                                                          amount = transaction_amount,
                                                          creation_date = date,
                                                          creation_time = time,
                                                          ).first()
        if not previous_transaction:
            flash('transaction does not exist')
            return redirect(url_for('payments'))
        
        return pay(recipient_account,transaction_amount)


@app.route("/confirm_payment", methods=['GET','POST'])
@login_required
def confirm_payment():
    page_name = 'confirm payment'
    if not current_user.is_authenticated:
        return redirect('login')  
    transaction_amount = session.get('transaction_amount')
    recipient_account = session.get('recipient_account')
    reference = session.get('reference')
    form = Confirm_Payment()
    if request.method == 'POST' and form.validate_on_submit():

        user_id = current_user.id
        account = Accounts.query.get(user_id)
        if not account:
            flash('Account not found')
            return redirect('payments')
        account_pin_hash = account.account_pin
        confirm_pin = form.account_pin.data
        if not bcrypt.check_password_hash(account_pin_hash, confirm_pin):
            flash('Incorrect Pin')
            return redirect('payments')
        
        return pay(recipient_account,transaction_amount, reference)
    recipient_name = session.get('recipient_name')
    return render_template("funds/confirm_payment.html", 
                           page_name=page_name, 
                           recipient_name=recipient_name, 
                           transaction_amount=transaction_amount,
                           form=form,
                           )


@app.route("/pay_store", methods=['GET', 'POST'])
@login_required
def pay_store():
    page_name = 'Instant Pay'
    user_id = current_user.id
    user = User.query.get(user_id)
    account = Accounts.query.get(user_id)
    account_id = user_id
    currency = user.currency,
    currency_string = str(currency[0])
    currency_symbol = account.currency_symbol
    account_balance = account.account_balance
    client_account = account.account_number
    if account_balance <= int(1000):
        balance = 'red'
    elif account_balance >= int(1000):
        balance = 'green'
    formatted_balance = '{: .2f}'.format(account_balance)
    formatted_amount = formatted_balance[:3] + ' ' + formatted_balance[3:]
    formated_account_balance = f"{currency_symbol} {formatted_amount}"
    
    form = Instant_PayCode()
    if request.method == 'POST' and form.validate_on_submit():
        if account.account_status == 'disabled':
            flash('Not Authorised To TransAct')
            if current_user.role == 'Agent':
                return redirect(url_for('menu'))
            return redirect(url_for('account'))

        current_balance = account.account_balance
        pay_amount = int(form.pay_amount.data)
        if pay_amount < 0:
            flash("enter a valid amount and continue")
            return redirect(url_for('pay_store'))

        if pay_amount > current_balance:
            flash('Yod dont enouph Funds')
            return redirect(url_for('pay_store'))
        else:
            pay_code = random.randint(1111111111, 9999999999)
            existing_pay_code = Recharge_Tokens.query.filter_by(token = pay_code).first()
            redeemed_token = Redeemed_Tokens.query.filter_by(token = pay_code).first()
            while existing_pay_code or redeemed_token:
                pay_code = random.randint(1111111111, 9999999999)

            account.account_balance = current_balance - pay_amount
            db.session.commit()
            status = 'Valid'
            action_done = datetime.now()
            created_date = action_done.date()
            created_time = action_done.time()


            transaction_amount = pay_amount
            remaining_balance = account.account_balance
            paycode_charges(account_id)
            paycode_notification_message(transaction_amount, remaining_balance)

            recharge_token = Recharge_Tokens(
                token = pay_code,
                sender_name = account.account_name,
                value = pay_amount,
                currency= currency_string,
                currency_symbol=currency_symbol,
                status=status,
                created_date=created_date,
                created_time=created_time,
                user_id=user_id,
            )
            db.session.add(recharge_token)
            db.session.commit()

            transaction = Transactions(
                sender_name = account.account_name,
                transaction_type = 'PayCode',
                sender_account = account.account_number,
                recipient_account = 'pending',
                recipient_name = 'pending',
                transaction_amount = pay_amount,
                currency=currency_string,
                currency_symbol=currency_symbol,
                before_balance = current_balance,
                remaining_balance = account.account_balance,
                transaction_date = created_date,
                transaction_time = created_time,
                user_id = user_id
            )
            db.session.add(transaction)
            db.session.commit()
            return render_template('funds/instant_paycode.html', 
                                   page_name=page_name,
                                   pay_code=pay_code,
                                   remaining_balance=transaction.remaining_balance,
                                   currency_symbol=currency_symbol,
                                   pay_amount=pay_amount,
                                   )
    return render_template('funds/create_paycode.html',
                           page_name=page_name,
                           currency_symbol=currency_symbol,
                           balance=balance,
                           form=form,
                           formated_account_balance=formated_account_balance,
                           )

@app.route("/redeem_paycode", methods=['GET','POST'])
@login_required
def redeem_paycode():
    page_name = 'Redeem PayCode'
    form = Redeem_Paycode()
    if request.method == 'POST' and form.validate_on_submit():
        paycode = int(form.paycode.data)

        valied_paycode = Recharge_Tokens.query.filter_by(token=paycode).first()
        if not valied_paycode:
            flash("PayCode Is Invalied")
            return redirect(url_for('redeem_paycode'))
        
        token_status = valied_paycode.status
        if token_status == 'invalid':
            flash('token has been used')
            return redirect(url_for('redeem_paycode'))
        elif token_status == 'reversed':
            flash('token has been reversed')
            return redirect(url_for('redeem_paycode'))
        
        token_value = valied_paycode.value

        user_id = current_user.id
        account = Accounts.query.get(user_id)
        before_balance = account.account_balance
        account.account_balance = before_balance + token_value
        valied_paycode.status = 'invalid'
        db.session.commit()

        action_date = datetime.now()
        redeemed_date = action_date.date()
        redeemed_time = action_date.time()

        redeemed_token = Redeemed_Tokens(
            token = paycode,
            value = valied_paycode.value,
            currency = valied_paycode.currency,
            currency_symbol = valied_paycode.currency_symbol,
            status = valied_paycode.status,
            redeemed_date = redeemed_date,
            redeemed_time = redeemed_time,
        )
        db.session.add(redeemed_token)
        db.session.commit()
        db.session.close()

    return render_template('merchant/redeem_paycode.html', page_name=page_name, form=form)


@app.route("/load_account", methods=['GET', 'POST'])
@login_required
def load_account():
    if current_user.role != 'Agent':
        flash('Access Denied')
        return redirect(url_for('/'))
    page_name = 'load account'
    form = Load_Account()
    if request.method == 'POST' and form.validate_on_submit():
        user_id = current_user.id
        merchant_account = Accounts.query.get(user_id)
        current_merchant_balance = merchant_account.account_balance

        account_number = int(form.account_number.data)
        load_amount = int(form.load_amount.data)

        if load_amount > current_merchant_balance:
            flash('Not Enough Funds, Try Lower Amount')
            return redirect(url_for('load_account'))

        valied_account = Accounts.query.filter_by(account_number=account_number).first()
        if not valied_account:
            flash('Account Does Not Exist')
            return redirect(url_for('load_account'))

        recipient_account = account_number
        transaction_amount = load_amount
        reference = current_user.first_name

        pay(recipient_account,transaction_amount,reference)

    return render_template('merchant/load_user_accounts.html', page_name=page_name)

@app.route("/merchant_history")
@login_required
def merchant_history():
    page_name = 'Transactions History'
    user_id = current_user.id
    user_role = current_user.role
    if user_role != 'Agent':
        flash('not a merchant')
        return redirect(url_for('accounts'))
    
    transactions = Transactions.query.filter_by(user_id=user_id).order_by(
    Transactions.transaction_date.desc(),
    Transactions.transaction_time.desc()).limit(50).all()


    return render_template('merchant/history.html',
                           page_name=page_name,
                           transactions=transactions,
                           )

@app.route("/statements", methods=['GET', 'POST'])
@login_required
def statements():
    page_name = 'statements'
    user_id = current_user.id
    account = Accounts.query.get(user_id)
    account_name = account.account_name
    account_balance = account.account_balance
    withdrawal_count = Withdrawals.query.filter_by(user_id=user_id).count()
    deposit_count = Deposits.query.filter_by(user_id=user_id).count()
    paycode_count = Recharge_Tokens.query.filter_by(user_id=user_id).count()
    payment_count = Payments.query.filter_by(user_id=user_id).count()
    transactions = Transactions.query.filter_by(user_id=user_id).order_by(Transactions.transaction_date.desc()).all()
    return render_template("funds/statements.html",page_name=page_name,
                           account_balance=account_balance,
                           account_name=account_name,
                           transactions=transactions,
                           withdrawal_count=withdrawal_count,
                           deposit_count=deposit_count,
                           paycode_count=paycode_count,
                           payment_count=payment_count,
                           )

@app.route("/my_paycodes")
@login_required
def my_paycodes():
    page_name = 'My Token History'
    user_id = current_user.id
    account = Accounts.query.get(user_id)
    sender_name = account.account_name
    tokens = Recharge_Tokens.query.filter_by(user_id=user_id,).order_by(
        Recharge_Tokens.created_date.desc(),
        Recharge_Tokens.created_time.desc()
    ).all()

    return render_template("funds/my_paycodes.html", tokens=tokens,page_name=page_name,sender_name=sender_name)

@app.route("/my_payments")
@login_required
def my_payments():
    page_name = 'My Payments'
    user_id = current_user.id
    account = Accounts.query.get(user_id)
    sender_name = account.account_name
    payments = Payments.query.filter_by(user_id=user_id).order_by(
        Payments.payment_time.desc()).all()
    
    return render_template("funds/my_payments.html",
                           page_name=page_name,
                           sender_name=sender_name,
                           payments=payments)

@app.route("/pos",methods=['GET', 'POST'])
@login_required
def pos():
    page_name = 'POS System'
    if current_user.role != 'Agent':
        flash('not available')
        return redirect(url_for('menu'))
    return render_template('pos/pos.html', page_name=page_name)

@app.route("/merchant_menu", methods=["GET"])
@login_required
def merchant_menu():
    if current_user.role != "Agent":
        flash("Access Denied")
        return redirect(url_for('user_accounts'))
    
    page_name = 'menu'
    return render_template('merchant/merchant_menu.html',page_name=page_name)

@app.route("/app_account_fees", methods=['GET', 'POST'])
@login_required
def app_account_fees():
    if current_user.role != 'Agent' and current_user.first_name != 'EliteTech':
        flash('not permitted for this route')
        return redirect(url_for('menu'))

    page_name = 'App Fees'
    user_id = current_user.id
    form = App_Account_Fees()

    if request.method == 'POST' and form.validate_on_submit():
        # Check if the record exists
        fees = Fees.query.get(user_id)

        if fees is not None:
            try:
                fees.deposit_fee = form.deposits.data
                fees.withdrawal_fee = form.withdrawals.data
                fees.paycode_fee = form.paycodes.data
                fees.payment_fee = form.payments.data

                action_done = datetime.now()

                action_date = action_done.date()
                action_time = action_done.time()
                fees.applied_date = action_date
                fees.applied_time = action_time

                db.session.commit()
                flash('Fees updated successfully!', 'success')
                return render_template('admin/account_fees.html')
            except Exception as e:
                # Handle the exception (e.g., log the error)
                flash('Error updating fees. Please try again.', 'error')
                db.session.rollback()  # Rollback the transaction to avoid leaving the database in an inconsistent state
    print('we ended here')
    return render_template('admin/app_account_fees.html', form=form, page_name=page_name)


@app.route("/recharge_tokens", methods=["GET", "POST"])
@login_required
def recharge_tokens():
    page_name = "recharge tokens"
    user_id = current_user.id
    user_role = current_user.role
    account = Accounts.query.get(user_id)
    sender_name = account.account_name
    currency = account.currency
    currency_symbol = account.currency_symbol
    current_balance = account.account_balance

    form = Recharge_Tokens_Form()
    if request.method == "POST" and form.validate_on_submit():
        if account.account_status == 'disabled':
            flash('Not Authorised To TransAct')
            if current_user.role == 'Agent':
                return redirect(url_for('menu'))
            return redirect(url_for('account'))
    
        token = random.randint(1111111111, 9999999999)
        if token:
            try:
                int(token)
            except ValueError:
                flash("incorrect token try again")

        existing_token = Recharge_Tokens.query.filter_by(token=token).first()
        if existing_token:
            flash("token does exist")
            if user_role == 'Agent':
                return redirect(url_for('menu'))
            return redirect(url_for("recharge_tokens"))

        redeemed_token = Redeemed_Tokens.query.filter_by(token=token).first()
        if redeemed_token:
            flash("token has been used up")
            if user_role == 'Agent':
                return redirect(url_for('menu'))
            return redirect(url_for("recharge_tokens"))

        value = int(form.value.data)

        if value > current_balance:
            flash('Not Enouph Funds To Procced')
            if user_role == 'Agent':
                return redirect(url_for('menu'))
            return redirect(url_for('recharge_tokens'))

        status = "valid"
        date = datetime.now()
        created_date = date.date()
        created_time = date.time()
        account.account_balance = current_balance - value

        new_token = Recharge_Tokens(
            token=token,
            value=value,
            sender_name=sender_name,
            currency=currency,
            currency_symbol=currency_symbol,
            status=status,
            created_date=created_date,
            created_time=created_time,
            user_id=current_user.id,
        )
        db.session.add(new_token)
        db.session.commit()

        transaction = Transactions(
            sender_name = account.account_name,
            recipient_name = 'pending',
            sender_account = account.account_number,
            recipient_account = 'pending',
            transaction_type='recharge code',
            transaction_amount = value,
            currency=currency,
            currency_symbol=currency_symbol,
            transaction_date = created_date,
            transaction_time = created_time,
            user_id = user_id,
        )
        db.session.add(transaction)
        db.session.commit()

        flash("token created successfully")
        return render_template('merchant/token_details.html',currency_symbol=currency_symbol, token=token, value=value, page_name=page_name)

    return render_template("merchant/create_token.html", page_name=page_name, form=form)

@app.route("/delete_token/<int:token_id>", methods=["POST"])
@login_required
def delete_token(token_id):
    user_id = current_user.id
    token_to_delete = Recharge_Tokens.query.get_or_404(token_id)
    token_status = token_to_delete.status
    sender_name = token_to_delete.sender_name
    if token_status == 'Valid' and token_to_delete.sender_name == sender_name:
        sender_account = Accounts.query.get(user_id)
        account_number = sender_account.account_number
        account_balance = sender_account.account_balance
        refund_amount = token_to_delete.value

        sender_account.account_balance = account_balance + refund_amount
        db.session.commit

    db.session.delete(token_to_delete)
    db.session.commit()
    flash("token deleted successfully", "success")
    return redirect(url_for("my_paycodes"))

@app.route("/reverse_token/<int:token_id>", methods=["POST"])
@login_required
def reverse_token(token_id):
    user_id = current_user.id
    token_to_reverse = Recharge_Tokens.query.get_or_404(token_id)
    token_status = token_to_reverse.status
    sender_name = token_to_reverse.sender_name
    if token_status == 'Valid' and token_to_reverse.sender_name == sender_name:
        sender_account = Accounts.query.get(user_id)
        account_number = sender_account.account_number
        account_balance = sender_account.account_balance
        refund_amount = token_to_reverse.value

        sender_account.account_balance = account_balance + refund_amount
        token_to_reverse.status = 'Reversed'
        db.session.commit

    db.session.commit()
    flash("token reversed successfully", "success")
    return redirect(url_for("my_paycodes"))

@app.route("/reverse_payment/<int:payment_id>", methods=["POST"])
@login_required
def reverse_payment(payment_id):
    user_id = current_user.id
    payment_to_reverse = Payments.query.get_or_404(payment_id)
    payment_status = payment_to_reverse.transaction_status
    sender_name = payment_to_reverse.account_name

    if sender_name == current_user.first_name:
        sender_account = Accounts.query.get(user_id)
        recipient_account = Accounts.query.filter_by(account_number=payment_to_reverse.recipient_account_number).first()

        if recipient_account and recipient_account.account_balance >= payment_to_reverse.amount:
            # Update sender's account balance
            sender_account.account_balance += payment_to_reverse.amount

            # Update recipient's account balance
            recipient_account.account_balance -= payment_to_reverse.amount

            # Update payment status
            payment_to_reverse.transaction_status = 'Reversed'

            # Commit changes to the database
            db.session.commit()

            flash("Payment reversed successfully", "success")
        else:
            flash("Recipient account does not have sufficient funds", "error")
    else:
        flash("Invalid transaction or unauthorized access", "error")

    return redirect(url_for("my_payments"))

if __name__ == "__main__":
    # Start the background task in a separate thread
    bg_thread = Thread(target=amount_update)
    bg_thread.daemon = True
    bg_thread.start()

    socketio.run(app, debug=True)