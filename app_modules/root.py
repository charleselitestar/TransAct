from datetime import datetime
from flask_bcrypt import Bcrypt
from app_models import db, User, Accounts, Fees
from app_config.config import Config, logger

bcrypt = Bcrypt()
root_account = int(231279260738)

def initialize_root():
    root_name = 'EliteTech'
    root_lastname = 'Karl'
    root_username = 'EliteTechRoot'
    root = User.query.filter_by(
        first_name = root_name,
        last_name = root_lastname,
        user_name = root_username
    ).first()
    if not root:
        create_root()
    else:
        pass

def initialize_fees(root_id):
    fees = Fees.query.filter_by(
        user_id=root_id,
    ).first()
    if not fees:
        create_fees(root_id)
    else:
        pass

def create_root():
    first_name = 'EliteTech'
    last_name = 'Karl'
    surname = 'Ndlovu'
    user_name = 'EliteTechRoot'
    password = '10111'
    email = 'elitetechproit@gmail.com'
    phone_number = '0683683674'
    main_image = '/static/images/2023.png'
    action_done = datetime.now()
    registration_date = action_done.date()
    registration_time = action_done.time()
    active = 'active'
    role = 'Agent'
    gender = 'Company'
    social_media_links = 'elitedocs.com'
    country = 'International'
    bio = 'All the best and latest technology put together, document, markets and finance'
    currency_name = 'South African Rand'
    currency_symbol = 'R'
    starting_balance = '100000'

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    root_user = User(
        first_name = first_name,
        last_name=last_name,
        surname=surname,
        user_name=user_name,
        email=email,
        phone_number=phone_number,
        main_image=main_image,
        social_media_links=social_media_links,
        bio=bio,
        gender=gender,
        registration_date=registration_date,
        registration_time=registration_time,
        status=active,
        country=country,
        currency=currency_name,
        currency_symbol=currency_symbol,
        role=role,
        password=hashed_password,
    )
    db.session.add(root_user)
    db.session.commit()

    account_name = first_name
    account_type = role
    account_balance = starting_balance
    account_pin = hashed_password
    account_status = 'Always Active'

    account_number = int(231279260738)

    root_account = Accounts(
        account_name = account_name,
        account_type=account_type,
        account_balance=account_balance,
        currency=currency_name,
        currency_symbol=currency_symbol,
        account_number=account_number,
        account_pin=account_pin,
        account_status=account_status,
        creation_date=registration_date,
        creation_time=registration_time,
        user_id=root_user.id,
    )
    db.session.add(root_account)
    db.session.commit()

    root_id = root_user.id
    initialize_fees(root_id)

    logger.info(f"{role} {user_name} registered at {datetime.now()}")


def create_fees(root_id):
    deposit_fee = int(2)
    withdrawal_fee = int(2)
    paycode_fee = int(2)
    payment_fee = int(2)

    action_done = datetime.now()
    applied_date = action_done.date()
    applied_time = action_done.time()

    fees = Fees(
        deposit_fee=deposit_fee,
        withdrawal_fee=withdrawal_fee,
        paycode_fee=paycode_fee,
        payment_fee=payment_fee,
        applied_date=applied_date,
        applied_time=applied_time,
        user_id = root_id,
    )
    db.session.add(fees)
    db.session.commit()
    logger.info(f"{'fees'} created at {datetime.now()}")
