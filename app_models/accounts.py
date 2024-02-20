from . import db

class Accounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(50))
    account_type = db.Column(db.String(50))
    account_number = db.Column(db.Integer)
    currency = db.Column(db.String(100))
    currency_symbol = db.Column(db.String(5))
    previous_balance = db.Column(db.Integer)
    account_balance = db.Column(db.Integer)
    account_pin = db.Column(db.String(50))
    account_status = db.Column(db.String(50))
    creation_date = db.Column(db.Date)
    creation_time = db.Column(db.Time)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)

    def balance_dict(self):
        return {
            'account_balance': self.account_balance,
        }

class Recipients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(50))
    account_type = db.Column(db.String(50))
    account_number = db.Column(db.Integer)
    currency_symbol = db.Column(db.String(5))
    amount = db.Column(db.Integer)
    creation_date = db.Column(db.Date)
    creation_time = db.Column(db.Time)
    recipient_id = db.Column(db.ForeignKey("user.id"), nullable=False)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)

class Deposits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(50))
    account_type = db.Column(db.String(50))
    account_number = db.Column(db.Integer)
    currency = db.Column(db.String(100))
    currency_symbol = db.Column(db.String(5))
    previous_balance = db.Column(db.Integer)
    account_balance = db.Column(db.Integer)
    deposit_amount = db.Column(db.String(50))
    deposit_date = db.Column(db.Date)
    deposit_time = db.Column(db.Time)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)

class Withdrawals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(50))
    account_type = db.Column(db.String(50))
    account_number = db.Column(db.Integer)
    currency = db.Column(db.String(100))
    currency_symbol = db.Column(db.String(5))
    previous_balance = db.Column(db.Integer)
    withdraw_amount = db.Column(db.String(50))
    account_balance = db.Column(db.Integer)
    withdraw_status = db.Column(db.String(50))
    withdraw_date = db.Column(db.Date)
    withdraw_time = db.Column(db.Time)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)

class Payments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(50))
    account_type = db.Column(db.String(50))
    account_number = db.Column(db.Integer)
    recipient_name = db.Column(db.String(100))
    recipient_account_number = db.Column(db.Integer)
    recipient_id = db.Column(db.Integer)
    currency = db.Column(db.String(100))
    currency_symbol = db.Column(db.String(5))
    previous_balance = db.Column(db.Integer)
    payment_amount = db.Column(db.Integer)
    account_balance = db.Column(db.Integer)
    transaction_status = db.Column(db.String(50))
    reference = db.Column(db.String(100))
    payment_date = db.Column(db.Date)
    payment_time = db.Column(db.Time)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(50))
    sender_account = db.Column(db.String(50))
    recipient_account = db.Column(db.String(50))
    recipient_name = db.Column(db.String(50))
    transaction_type = db.Column(db.String(50))
    transaction_amount = db.Column(db.Integer)
    currency = db.Column(db.String(100))
    currency_symbol = db.Column(db.String(5))
    charges = db.Column(db.Integer)
    before_balance = db.Column(db.Integer)
    remaining_balance = db.Column(db.Integer)
    transaction_date = db.Column(db.Date)
    transaction_time = db.Column(db.Time)
    recipient_id = db.Column(db.Integer)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)

class Account_Charges(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(50))
    sender_account = db.Column(db.String(50))
    recipient_account = db.Column(db.String(50))
    recipient_name = db.Column(db.String(50))
    transaction_type = db.Column(db.String(50))
    transaction_amount = db.Column(db.Integer)
    currency = db.Column(db.String(100))
    currency_symbol = db.Column(db.String(5))
    client_user_id = db.Column(db.Integer)
    charges = db.Column(db.Integer)
    before_balance = db.Column(db.Integer)
    remaining_balance = db.Column(db.Integer)
    transaction_date = db.Column(db.Date)
    transaction_time = db.Column(db.Time)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)

class Recharge_Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Integer, unique=True)
    sender_name = db.Column(db.String(100))
    currency = db.Column(db.String(100))
    currency_symbol = db.Column(db.String(5))
    value = db.Column(db.Integer)
    status = db.Column(db.String(50))
    created_date = db.Column(db.Date)
    created_time = db.Column(db.Time)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)

class Withdraw_Codes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    withdraw_code = db.Column(db.Integer, unique=True)
    withdraw_pin = db.Column(db.Integer)
    code_status = db.Column(db.String(50))
    withdraw_amount = db.Column(db.Integer)
    hashed_password = db.Column(db.String(100))
    currency = db.Column(db.String(20))
    currency_symbol = db.Column(db.String(5))
    charges = db.Column(db.Integer)
    withdraw_account = db.Column(db.Integer)
    created_date = db.Column(db.Date)
    created_time = db.Column(db.Time)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)

class Withdrawn_Funds(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    withdraw_code = db.Column(db.Integer, unique=True)
    withdraw_pin = db.Column(db.Integer)
    code_status = db.Column(db.String(50))
    withdraw_amount = db.Column(db.Integer)
    currency = db.Column(db.String(20))
    currency_symbol = db.Column(db.String(5))
    withdraw_date = db.Column(db.Date)
    withdraw_time = db.Column(db.Time)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)

class Redeemed_Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Integer, unique=True)
    value = db.Column(db.Integer)
    currency = db.Column(db.String(20))
    currency_symbol = db.Column(db.String(5))
    status = db.Column(db.String(50))
    redeemed_date = db.Column(db.Date)
    redeemed_time = db.Column(db.Time)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)

class Fees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deposit_fee = db.Column(db.Integer)
    withdrawal_fee = db.Column(db.Integer)
    paycode_fee = db.Column(db.Integer)
    payment_fee = db.Column(db.Integer)
    applied_date = db.Column(db.Date)
    applied_time = db.Column(db.Time)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)

class Limits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    withdrawal = db.Column(db.Integer)
    paycode = db.Column(db.Integer)
    payments = db.Column(db.Integer)
    daily = db.Column(db.Integer)
    weekly = db.Column(db.Integer)
    monthly = db.Column(db.Integer)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)
