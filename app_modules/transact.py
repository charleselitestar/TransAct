from flask import render_template, redirect,request,flash,session,url_for, make_response
from flask_login import current_user
from app_models import db,Accounts,Account_Charges,Transactions, Withdrawals,Withdrawn_Funds,Withdraw_Codes, Fees, User, Message
from app_models import Recharge_Tokens, Redeemed_Tokens, Deposits, Recipients, Payments
from app_forms import Withdraw_Funds_Form, Confirm_Withdrawal, Collect_Funds_Form
from app_forms import Recharge_Tokens_Form, Recharge_Form
from .root import initialize_root, root_account
from flask_socketio import SocketIO, emit
from sqlalchemy import desc
from sqlalchemy import or_
from flask_bcrypt import Bcrypt
import random
from datetime import datetime

bcrypt = Bcrypt()

def new_message_alert(recipient_id, message):
    sender_name = current_user.first_name
    alert_recipient = User.query.filter_by(
        id = recipient_id,
    ).first()
    now = datetime.now()
    datestamp = now.date()
    timestamp = now.time()
    hours = now.hour
    minutes = now.minute
    seconds = now.second

    time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    recipient_message = f"New message from {sender_name} at {time}"
    status = 'recieved'

    message_notification = Message(
        message_header = 'message',
        sender = sender_name,
        recipient = alert_recipient.user_name,
        short_text = recipient_message,
        text = message,
        datestamp=datestamp,
        timestamp=timestamp,
        status = status,
        recipient_id=alert_recipient.id,
        user_id=alert_recipient.id,
    )
    db.session.add(message_notification)

def account_notification_message(recipient_account,transaction_amount):
    sender_username = current_user.user_name
    sender_name = current_user.first_name
    currency_symbol = current_user.currency_symbol
    client = Accounts.query.filter_by(account_number=recipient_account).first()
    client_user_id = client.user_id
    client_user = User.query.get(client_user_id)
    recipient_username = client_user.user_name

    now = datetime.now()
    datestamp = now.date()
    timestamp = now.time()
    hours = now.hour
    minutes = now.minute
    seconds = now.second

    time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    sender_message = f"you sent {currency_symbol} {transaction_amount} to {client_user.first_name} at {time}"
    recipient_message = f"you have recived {currency_symbol} {transaction_amount} from {sender_name} at {time}"
    status = 'recieved'

    recipient_notification = Message(
        message_header= 'message',
        sender = 'TransAct',
        recipient = recipient_username,
        short_text=recipient_message,
        text = recipient_message,
        status=status,
        datestamp=datestamp,
        timestamp=timestamp,
        recipient_id=client_user_id,
        user_id=client_user_id,
    )
    db.session.add(recipient_notification)

    sender_notification = Message(
        message_header= 'meassage',
        sender = 'TransAct',
        recipient = sender_username,
        short_text=sender_message,
        text = sender_message,
        status=status,
        datestamp=datestamp,
        timestamp=timestamp,
        recipient_id=current_user.id,
        user_id = current_user.id,
    )
    db.session.add(sender_notification)
    db.session.commit()


def paycode_notification_message(transaction_amount, remaining_balance):
    sender_username = current_user.user_name
    sender_name = current_user.first_name
    currency_symbol = current_user.currency_symbol

    now = datetime.now()
    datestamp = now.date()
    timestamp = now.time()
    hours = now.hour
    minutes = now.minute
    seconds = now.second

    time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    short_text = f"{currency_symbol} {transaction_amount} paycode created at {time} "
    recipient_message = f"{currency_symbol} {transaction_amount} paycode created at {time} remaining balance is {remaining_balance} "
    status = 'recieved'

    paycode_notification = Message(
        message_header= 'message',
        sender = 'TransAct',
        recipient = sender_username,
        short_text=short_text,
        text = recipient_message,
        status=status,
        datestamp=datestamp,
        timestamp=timestamp,
        recipient_id=current_user.id,
        user_id=current_user.id,
    )
    db.session.add(paycode_notification)
    db.session.commit()

def recharge_notification_message(transaction_amount, available_funds):
    sender_username = current_user.user_name
    sender_name = current_user.first_name
    currency_symbol = current_user.currency_symbol

    now = datetime.now()
    datestamp = now.date()
    timestamp = now.time()
    hours = now.hour
    minutes = now.minute
    seconds = now.second

    time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    short_text = f"Account Recharched With {currency_symbol} {transaction_amount} at {time}"
    recipient_message = f"Account Recharched With {currency_symbol} {transaction_amount} at {time} your balance is {currency_symbol} {available_funds}"
    status = 'recieved'

    recharge_notification = Message(
        message_header= 'meassage',
        sender = 'TransAct',
        recipient = sender_username,
        short_text=short_text,
        text = recipient_message,
        status=status,
        datestamp=datestamp,
        timestamp=timestamp,
        recipient_id=current_user.id,
        user_id=current_user.id,
    )
    db.session.add(recharge_notification)

def withdrawal_notification_message(transaction_amount, remaining_balance):
    sender_username = current_user.user_name
    sender_name = current_user.first_name
    currency_symbol = current_user.currency_symbol

    now = datetime.now()
    datestamp = now.date()
    timestamp = now.time()
    hours = now.hour
    minutes = now.minute
    seconds = now.second

    time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    recipient_message = f"{currency_symbol} {transaction_amount} Withdrawn from Account at {time}"
    short_message = f"{currency_symbol} {transaction_amount} Has Been Withdrawn from Your Account at {time} Your remaining balance is {currency_symbol} {remaining_balance} "
    status = 'recieved'

    withdrawal_notification = Message(
        message_header= 'message',
        sender = 'TransAct',
        recipient = sender_username,
        short_text=recipient_message,
        text = short_message,
        status=status,
        datestamp=datestamp,
        timestamp=timestamp,
        recipient_id=current_user.id,
        user_id=current_user.id,
    )
    db.session.add(withdrawal_notification)


def record_transaction(account_id,price,fee_type):
    root_user_id = int(2)
    root_account = Accounts.query.get(root_user_id)
    root_account_number = root_account.account_number
    if root_account is None:
        # Handle the case where the root account is not found
        flash('Root account not found')
        return initialize_root()

    root_id = root_account.user_id

    client_id = current_user.id
    client_account = Accounts.query.get(client_id)

    if client_account is None:
        # Handle the case where the client account is not found
        flash('Client account not found')

    client_name = client_account.account_name
    client_id = client_account.user_id
    client_balance = client_account.account_balance
    client_account_number = client_account.account_number

    remaining_client_balance = client_balance

    current_balance = root_account.account_balance
    root_account_balance = current_balance

    action_done = datetime.now()
    charge_date = action_done.date()
    charge_time = action_done.time()

    transaction = Account_Charges(
        sender_name=client_name,
        sender_account=client_account_number,
        recipient_account=root_account_number,
        recipient_name=root_account.account_name,
        transaction_type=fee_type,
        charges = price,
        transaction_amount=price,
        currency=client_account.currency,
        currency_symbol=client_account.currency_symbol,
        before_balance=current_balance,
        remaining_balance=root_account_balance,
        transaction_date=charge_date,
        transaction_time=charge_time,
        client_user_id=client_id,
        user_id=root_id,
    )

    db.session.add(transaction)
    db.session.commit()


def fund_root(amount):
    account = Accounts.query.filter_by(account_number=root_account).first()
    current_balance = account.account_balance
    account.account_balance = current_balance + amount
    db.session.commit()

def get_from_root(withdraw_code):
    account = Accounts.query.filter_by(account_number=root_account).first()
    current_balance = account.account_balance
    withdrawal = Withdraw_Codes.query.filter_by(withdraw_code=withdraw_code).first()
    amount = withdrawal.charges
    merchant_amount = amount / 2
    account.account_balance = current_balance - merchant_amount
    db.session.commit()
    return merchant_amount

def withdraw_charge_calc(amount):
    fee = Fees.query.first()
    price = fee.withdrawal_fee

    if amount < 100:
        price = price
    elif 100 < amount < 500:
        price = price * 2
    elif 500 < amount < 1000:
        price = price * 3
    elif 1000 < amount < 1500:
        price = price * 4
    elif 1500 < amount < 2000:
        price = price * 5
    else:
        price = price * 10

    return price

def withdrawal_charges(account_id, withdraw_amount):
    price = withdraw_charge_calc(withdraw_amount)
    amount = price
    fund_root(amount)
    fee_type = 'withdrawal fee'
    record_transaction(account_id,price,fee_type)

def deposit_charges(account_id):
    fee = Fees.query.first()
    price = fee.deposit_fee
    amount = price
    fund_root(amount)
    fee_type='deposit charge'
    record_transaction(account_id,price,fee_type)

def payment_charge_calc(amount):
    fee = Fees.query.first()
    price = fee.payment_fee

    if amount < 100:
        price = price
    elif 100 < amount < 500:
        price = price * 2
    elif 500 < amount < 1000:
        price = price * 3
    elif 1000 < amount < 1500:
        price = price * 4
    elif 1500 < amount < 2000:
        price = price * 5
    else:
        price = price * 10

    return price


def payment_charges(account_id,payment_amount):
    price = payment_charge_calc(payment_amount)
    amount = price
    fund_root(amount)
    fee_type='payment charge'
    record_transaction(account_id,price,fee_type)

def paycode_charges(account_id):
    fee = Fees.query.first()
    price = fee.paycode_fee
    amount = price
    fund_root(amount)
    fee_type ='paycode charges'
    record_transaction(account_id,price,fee_type)

def template_charges(fee_type,price,client_account):
    account = Accounts.query.filter_by(account_number=client_account).first()
    client_balance = account.account_balance
    account_id = account.user_id
    remaining_balance = client_balance - price
    account.account_balance = remaining_balance
    db.session.commit()
    amount = price
    fund_root(amount)
    record_transaction(account_id,price,client_account)
    

def account_charges(fee_type,price,client_account,account_id):
    print(price)

    client = Accounts.query.get(account_id)
    client_name = client.account_name
    client_id = client.user_id
    client_balance = client.account_balance

    if price > client_balance:
        flash('not enoph funds recharge and try again')
        return redirect(url_for('menu'))
    
    account = Accounts.query.filter_by(account_number=root_account).first()
    current_balance = account.account_balance
    account.account_balance = current_balance + price

    remaining_client_balance = client_balance - price
    client.account_balance = remaining_client_balance

    client_account_number = client.account_number

    action_done = datetime.now()
    charge_date = action_done.date()
    charge_time = action_done.time()

    transaction = Transactions(
        sender_name = client_name,
        sender_account = client_account_number,
        recipient_account = root_account,
        recipient_name = account.account_name,
        transaction_type = fee_type,
        transaction_amount=price,
        currency = client.currency,
        currency_symbol = client.currency_symbol,
        before_balance=current_balance,
        remaining_balance = account.account_balance,
        transaction_date=charge_date,
        transaction_time=charge_time,
        user_id=current_user.id,
    )
    db.session.add(transaction)

    charge_record = Transactions(
        sender_name = client_name,
        sender_account = client_account_number,
        recipient_account = root_account,
        recipient_name = account.account_name,
        transaction_type = fee_type,
        transaction_amount=price,
        currency = client.currency,
        currency_symbol = client.currency_symbol,
        before_balance=client_balance,
        remaining_balance = remaining_client_balance,
        transaction_date=charge_date,
        transaction_time=charge_time,
        user_id=client_id,
    )
    db.session.add(charge_record)
    db.session.commit()


def menu():
    pass

def current_date():
    now = datetime.now()
    date = now.date()
    return date

def get_date(date):
    now = date
    year = now.year
    month = now.month
    day = now.day
    date = f"{year}-{month:02d}-{day:02d}"
    return date

def current_time():
    now = datetime.now()
    return now.time()

def get_time(time):
    now = time
    hour = now.hour
    minutes = now.minute
    seconds = now.second
    time = f"{hour:02d}:{minutes:02d}:{seconds:02d}"
    return time


def format_balance(account_balance):
    if account_balance is None:
        return 'R 0.00'
    
    acb = str(account_balance)
    bal = len(acb)

    currency_symbol = current_user.currency_symbol
    
    if bal < 4:
        formatted_balance = '{:.2f}'.format(account_balance)
        formatted_balance = f"{currency_symbol} {formatted_balance}"
    elif bal == 4:
        formatted_balance = '{:.2f}'.format(account_balance)
        formatted_balance = f"{currency_symbol} {formatted_balance[:1]} {formatted_balance[1:]}"
    elif bal == 5:
        formatted_balance = '{:.2f}'.format(account_balance)
        formatted_balance = f"{currency_symbol} {formatted_balance[:2]} {formatted_balance[2:]}"
    elif bal == 6:
        formatted_balance = '{:.2f}'.format(account_balance)
        formatted_balance = f"{currency_symbol} {formatted_balance[:3]} {formatted_balance[3:]}"
    elif bal > 6:
        formatted_balance = '{:,.2f}'.format(account_balance)
        formatted_balance = f"{currency_symbol} {formatted_balance}"
    
    return formatted_balance

        

def user_accounts():
    clue = 'account'
    if request.method == "GET":
        first_name = current_user.first_name
        page_name = f"{first_name}'s account"
        user_id = current_user.id
        account = Accounts.query.get(user_id)
        account_balance = account.account_balance
        bal = account.account_balance

        if bal > 1000:
            balance = 'green'
        else:
            balance = 'red'

        bal = format_balance(account_balance)
        account_balance = bal

    
        latest_transaction = (
            Transactions.query.filter(or_(
                    Transactions.user_id == user_id,
                    Transactions.recipient_account == account.account_number,
                    Transactions.sender_account == account.account_number,
                )
            )
            .order_by(desc(Transactions.transaction_time)).first())

        # Get the most recent 5 transactions
        transactions = (Transactions.query.filter(or_(
                    Transactions.user_id == user_id,
                    Transactions.recipient_account == account.account_number,
                    Transactions.sender_account == account.account_number,
                )
            )
            .order_by(
                Transactions.transaction_date.desc(),
                Transactions.transaction_time.desc(),
            ).all()
        )

        # Update the transactions list with the latest transaction
        if latest_transaction and latest_transaction not in transactions:
            transactions.insert(0, latest_transaction)

        # Ensure transactions list contains at most 5 elements
        transactions = transactions[:5]
        url = '/account'
        return render_template(
            "funds/accounts.html",
            clue=clue,
            page_name=page_name,
            account=account,
            balance=balance,
            account_balance=account_balance,
            transactions=transactions,
            url=url,
        )

def recharge_account():
    form = Recharge_Form()
    if request.method == "POST" and form.validate_on_submit():
        user_id = current_user.id
        account = Accounts.query.get(user_id)
        if account.account_status == 'disabled':
            flash('Not Authorised To TransAct')
            if current_user.role == 'Agent':
                return redirect(url_for('menu'))
            return redirect(url_for('account'))
        currency = account.currency
        currency_symbol = account.currency_symbol
        current_balance = account.account_balance

        token = int(form.token.data)
        if not token:
            flash("please enter a recharge token")
            return redirect(url_for("fund_account"))

        recharge_token = Recharge_Tokens.query.filter_by(token=token).first()
        if not recharge_token:
            flash("Invalid Token")
            return redirect(url_for("fund_account"))

        token_value = recharge_token.value
        status = recharge_token.status
        token_sender = recharge_token.sender_name
        

        if status == "invalid":
            flash("token has been used up")
            return redirect(url_for("fund_account"))
        else:
            account.previous_balance = current_balance
            account.account_balance = current_balance + token_value
            recharge_token.recipient_name = account.account_name
            recharge_token.status = "invalid"
            db.session.commit()

            transaction_amount = token_value
            available_funds = account.account_balance
            account_id = account.user_id
            deposit_charges(account_id)
            recharge_notification_message(transaction_amount, available_funds)

            action_done = datetime.now()
            transaction_type = "Deposit"
            redeemed_date = action_done.date()
            redeemed_time = action_done.time()

            redeemed_token = Redeemed_Tokens(
                token=token,
                value=token_value,
                currency=currency,
                currency_symbol=currency_symbol,
                status=recharge_token.status,
                redeemed_date=redeemed_date,
                redeemed_time=redeemed_time,
                user_id=user_id,
            )
            db.session.add(redeemed_token)
            db.session.commit()

            deposit = Deposits(
                account_name = account.account_name,
                account_type = account.account_type,
                account_number = account.account_number,
                currency = account.currency,
                currency_symbol = account.currency_symbol,
                previous_balance = current_balance,
                account_balance = account.account_balance,
                deposit_amount = token_value,
                deposit_date = redeemed_date,
                deposit_time = redeemed_time,
                user_id=user_id,
            )
            db.session.add(deposit)
            db.session.commit()

            transaction = Transactions(
                sender_name=token_sender,
                sender_account=account.account_number,
                recipient_account=account.account_number,
                recipient_name=account.account_name,
                transaction_type=transaction_type,
                transaction_amount=token_value,
                before_balance = current_balance,
                remaining_balance = account.account_balance,
                currency=currency,
                currency_symbol=currency_symbol,
                transaction_date=redeemed_date,
                transaction_time=redeemed_time,
                user_id=user_id,
            )
            db.session.add(transaction)
            db.session.commit()

            user_role = current_user.role
            current_balance = format_balance(current_balance)
            token_value = format_balance(token_value)
            remaining_balance = format_balance(account.account_balance)

            page_name = 'recharge success'

            if user_role == 'Agent':
                return render_template('merchant/recharge_success.html',page_name=page_name,current_balance=current_balance,token_value=token_value,remaining_balance=remaining_balance)
            return render_template('funds/recharge_success.html',page_name=page_name,current_balance=current_balance,token_value=token_value,remaining_balance=remaining_balance)
            

def merchant_accounts():
        page_name = 'App Agent'
        user_id = current_user.id
        account = Accounts.query.get(user_id)
        account_balance = account.account_balance
        currency = account.currency_symbol
        bal = account_balance

        if bal > 1000:
            balance = 'green'
        else:
            balance = 'red'

        account_balance = format_balance(account_balance)
        form = Recharge_Tokens_Form()
        return render_template('merchant/create_token.html',
                                page_name=page_name,
                                account_balance=account_balance,
                                balance=balance,
                                form=form,
                                )

def country_currency(country_name):
    currencies = {
        'south africa': {'name': 'South African Rand', 'symbol': 'R'},
        'nigeria': {'name': 'Nigerian Naira', 'symbol': '₦'},
        'egypt': {'name': 'Egyptian Pound', 'symbol': '£'},
        'kenya': {'name': 'Kenyan Shilling', 'symbol': 'KSh'},
        'morocco': {'name': 'Moroccan Dirham', 'symbol': 'د.م.'},
        'ghana': {'name': 'Ghanaian Cedi', 'symbol': '₵'},
        'algeria': {'name': 'Algerian Dinar', 'symbol': 'د.ج'},
        'ethiopia': {'name': 'Ethiopian Birr', 'symbol': 'Br'},
        'tanzania': {'name': 'Tanzanian Shilling', 'symbol': 'TZS'},
        'uganda': {'name': 'Ugandan Shilling', 'symbol': 'UGX'},
    }

    # Use country_name as the parameter and iterate through currencies
    for country, data in currencies.items():
        if country_name.lower() == country:
            return data

    # If the country is not found in the dictionary, return None
    return None

def banking(user_name):
    page_name = 'create cv'
    print(f"hie {user_name} banking works just fine okay i see that")
    return render_template("create/create_cv.html", page_name=page_name)

def withdraw_user_funds():
    form = Withdraw_Funds_Form()
    page_name = "withdraw funds"
    user_id = current_user.id
    account = Accounts.query.get(user_id)
    account_balance = account.account_balance  # Move this line outside the block

    if request.method == 'POST' and form.validate_on_submit():
        withdraw_amount = int(form.withdraw_amount.data)
        session['withdraw_amount'] = withdraw_amount

        if withdraw_amount < 0:
            flash("enter a valid amount and continue")
            return redirect(url_for('withdraw_funds'))

        if withdraw_amount > account_balance:
            flash('not enough funds, please recharge and try again')
            return redirect(url_for('withdraw_funds'))

        if withdraw_amount >= 500:
            page_name = 'confirm transaction'
            form = Confirm_Withdrawal()
            flash('confirm transaction')
            withdraw_amount = format_balance(withdraw_amount)
            return render_template('funds/confirm_withdrawal.html', page_name=page_name, withdraw_amount=withdraw_amount, form=form)

        return withdraw(withdraw_amount)
    bal = account_balance
    if bal > 1000:
        balance = 'green'
    else:
        balance = 'red'
    account_balance = format_balance(account_balance)
    return render_template("funds/withdraw.html", page_name=page_name, account=account, form=form, account_balance=account_balance, balance=balance)

def confirm_withdrawal(confirm_pin):
    user_id = current_user.id
    account = Accounts.query.get(user_id)
    account_pin_hash = account.account_pin
    withdraw_amount = session.get('withdraw_amount')

    if not bcrypt.check_password_hash(account_pin_hash, confirm_pin):
        flash('Incorrect Pin')
        return redirect(url_for('withdraw_funds'))
    return withdraw(withdraw_amount)

def withdraw(withdraw_amount):
    session.pop('withdraw_amount')
    page_name = "withdraw details"
    user_id = current_user.id
    account = Accounts.query.get(user_id)
    account_id = account.user_id
    client_account = account.account_number
    current_balance = account.account_balance
    currency = account.currency
    currency_symbol = account.currency_symbol
    
    if withdraw_amount > current_balance:
        code_status = "Declined"
        flash("Insufficient Funds. Try a Different amount")
        return redirect(url_for("withdraw_funds"))
    else:
        charges = withdraw_charge_calc(withdraw_amount)
        withdrawal_charges(account_id,withdraw_amount)

        withdraw_account = account.account_number
        remaining_balance = current_balance - withdraw_amount
        account.previous_balance = current_balance
        account.account_balance = remaining_balance - charges
        db.session.commit()

        created_date = current_date()
        created_time = current_time()
        code_status = "active"

        # Generate unique withdraw_code and withdraw_pin
        withdraw_code = random.randint(111111111, 999999999)
        withdraw_pin = random.randint(11111, 99999)

        # Ensure the generated withdraw_code is unique in both tables
        existing_withdraw_code = Withdraw_Codes.query.filter_by(
            withdraw_code=withdraw_code
        ).first()

        while (
            existing_withdraw_code
            or Withdrawn_Funds.query.filter_by(
                withdraw_code=withdraw_code, withdraw_pin=withdraw_pin
            ).first()
        ):
            withdraw_code = random.randint(111111111, 999999999)
            withdraw_pin = random.randint(11111, 99999)
            
            
            existing_withdraw_code = Withdraw_Codes.query.filter_by(
                withdraw_code=withdraw_code,
            ).first()

        p_string = str(withdraw_pin)
        hashed_pin = bcrypt.generate_password_hash(p_string).decode("utf-8")
        withdrawn_funds = Withdrawn_Funds.query.filter_by(
            withdraw_code=withdraw_code,
        ).first()

        if withdrawn_funds:
            flash("Withdrawal has already been processed.")
            return redirect(url_for("withdraw_funds"))

        transaction_amount = withdraw_amount
        withdrawal_notification_message(transaction_amount, remaining_balance)

        withdraw_voucher = Withdraw_Codes(
            withdraw_code=withdraw_code,
            withdraw_amount=withdraw_amount,
            currency=currency,
            currency_symbol=currency_symbol,
            withdraw_account=withdraw_account,
            withdraw_pin=hashed_pin,
            code_status=code_status,
            created_date=created_date,
            created_time=created_time,
            user_id=user_id,
        )
        db.session.add(withdraw_voucher)

        transaction = Transactions(
            sender_account = account.account_name,
            recipient_name = account.account_name,
            transaction_type='withdrawal',
            transaction_amount=withdraw_amount,
            before_balance=current_balance,
            remaining_balance=remaining_balance,
            charges=charges,
            currency=currency,
            currency_symbol=currency_symbol,
            transaction_date=created_date,
            transaction_time=created_time,
            user_id=user_id,
        )
        db.session.add(transaction)

        withdrawal = Withdrawals(
            account_name=account.account_name,
            account_type=account.account_type,
            account_number=account.account_number,
            currency=account.currency,
            currency_symbol=currency_symbol,
            previous_balance=current_balance,
            withdraw_amount=withdraw_amount,
            account_balance=remaining_balance,
            withdraw_status='success',
            withdraw_date=created_date,
            withdraw_time=created_time,
            user_id=user_id,
        )
        db.session.add(withdrawal)
        db.session.commit()

        # Pass data to the template
        withdraw_amount = format_balance(withdraw_amount)
        page_name = 'withdraw success'
        return render_template(
            "funds/withdraw_details.html",
            withdraw_code=withdraw_code,
            withdraw_pin=withdraw_pin,  # Use hashed_pin instead of withdraw_pin
            withdraw_amount=withdraw_amount,
            page_name=page_name,
        )


def pay(recipient_account,transaction_amount,reference):
    user_id = current_user.id
    account = Accounts.query.get(user_id)
    currency = account.currency
    currency_symbol = account.currency_symbol
    recipient = Accounts.query.filter_by(account_number=recipient_account).first()

    current_balance = account.account_balance
    valid_account = Accounts.query.filter_by(account_number=recipient_account).first()
    if not valid_account:
        flash('account does not exist')
        return redirect(url_for('payments'))
    else:
        if transaction_amount > current_balance:
            flash("Insufficient funds for this transaction")
            return redirect(url_for("payments"))

        charges = payment_charge_calc(transaction_amount)
        
        account.previous_balance = current_balance
        account.account_balance -= transaction_amount
        valid_account.previous_balance = valid_account.account_balance
        valid_account.account_balance += transaction_amount
        db.session.commit()

        action_done = datetime.now()
        payment_date = action_done.date()
        payment_time = action_done.time()

        # Create a payment transaction record
        transaction = Transactions(
            sender_name=account.account_name,
            sender_account=account.account_number,
            recipient_name=valid_account.account_name,
            recipient_account=valid_account.account_number,
            currency=currency,
            currency_symbol=currency_symbol,
            transaction_type="Payment",
            transaction_amount=transaction_amount,
            transaction_date=payment_date,
            transaction_time=payment_time,
            recipient_id=valid_account.user_id,
            user_id=user_id,
        )

        db.session.add(transaction)
        db.session.commit()

        recipient = Recipients(
            account_name = recipient.account_name,
            account_type = recipient.account_type,
            account_number = recipient.account_number,
            currency_symbol = recipient.currency_symbol,
            amount = transaction_amount,
            creation_date = payment_date,
            creation_time = payment_time,
            recipient_id = recipient.user_id,
            user_id = current_user.id,
        )
        db.session.add(recipient)
        db.session.commit()

        payment = Payments(
            account_name = recipient.account_name,
            account_type = recipient.account_type,
            account_number = recipient.account_number,
            currency = currency,
            currency_symbol = recipient.currency_symbol,
            payment_amount = transaction_amount,
            previous_balance = current_balance,
            account_balance = account.account_balance,
            transaction_status = 'payment',
            reference = reference,
            payment_date = payment_date,
            payment_time = payment_time,
            recipient_id = recipient.user_id,
            user_id = user_id,
        )
        db.session.add(payment)
        db.session.commit()

        account_notification_message(recipient_account,transaction_amount)

        flash("Payment successful")
        page_name = 'payment success'
        previous_balance = format_balance(account.previous_balance)
        payment_amount = format_balance(transaction_amount)
        remaining_balance = format_balance(account.previous_balance) 
        date = get_date(payment_date)
        time = get_time(payment_time)
        
        return render_template('funds/payment_success.html',
                               page_name=page_name,
                               payment=payment,
                               previous_balance=previous_balance,
                               payment_amount=payment_amount,
                               remaining_balance=remaining_balance,
                               date=date,
                               time=time,
                               )


def redeem_funds(withdraw_code):
    user_id = current_user.id
    account = Accounts.query.get(user_id)
    currency = account.currency
    currency_symbol = account.currency_symbol
    current_balance = account.account_balance
    account_number = account.account_number

    withdrawn_funds = Withdrawn_Funds.query.filter_by(withdraw_code=withdraw_code).first()
    if withdrawn_funds:
        flash('Token has been redeemed')
        return redirect(url_for('collect_funds'))

    withdrawal = Withdraw_Codes.query.filter_by(withdraw_code=withdraw_code).first()

    if not withdrawal:
        flash("Incorrect voucher or withdrawal pin")
        return redirect(url_for("collect_funds"))

    try:
        withdraw_amount = withdrawal.withdraw_amount
        withdraw_account_number = withdrawal.withdraw_account
        withdraw_account = Accounts.query.filter_by(account_number=withdraw_account_number).first()
        status = withdrawal.code_status
        code_status = 'withdrawal'

        merchant_amount = get_from_root(withdraw_code)

        account.previous_balance = current_balance
        account.account_balance += withdrawal.withdraw_amount
        account.account_balance += merchant_amount

        withdraw_date = current_date()
        withdraw_time = current_time()
        action = "withdrawal"
        code_status = "Success"

        withdrawn_funds = Withdrawn_Funds(
            withdraw_code=withdraw_code,
            withdraw_pin=withdrawal.withdraw_pin,
            code_status=code_status,
            withdraw_amount=withdraw_amount,
            currency=currency,
            currency_symbol=currency_symbol,
            withdraw_date=withdraw_date,
            withdraw_time=withdraw_time,
            user_id=user_id,
        )
        db.session.add(withdrawn_funds)
        db.session.commit()

        withdrawal = Withdrawals(
            account_name=account.account_name,
            account_type=account.account_type,
            account_number=account.account_number,
            currency=currency,
            currency_symbol=currency_symbol,
            previous_balance=current_balance,
            withdraw_amount=withdraw_amount,
            account_balance=account.account_balance,
            withdraw_date=withdraw_date,
            withdraw_time=withdraw_time,
            withdraw_status=code_status,
            user_id=user_id,
        )
        db.session.add(withdrawal)
        db.session.commit()

        transaction = Transactions(
            transaction_type=action,
            transaction_amount=withdraw_amount,
            currency=currency,
            currency_symbol=currency_symbol,
            transaction_date=withdraw_date,
            transaction_time=withdraw_time,
            user_id=user_id,
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Withdrawal success')

        return render_template('funds/withdraw_success.html', withdrawal=withdrawal)

    except Exception as e:
        # Log the exception for debugging
        flash(f"An error occurred: {str(e)}")
        db.session.rollback()

    finally:
        db.session.close()