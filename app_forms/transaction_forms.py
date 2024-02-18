from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, PasswordField
from wtforms.validators import DataRequired,Length 

class Recharge_Form(FlaskForm):
    token = StringField('token', validators=[DataRequired()], render_kw={'maxlength': 10, "placeholder": "Enter your Token", "autofocus": "true"})
    submit = SubmitField('Done')

class Recharge_Tokens_Form(FlaskForm):
    value = StringField('value', validators=[DataRequired()], render_kw={"placeholder": "Enter Token Amount", "autofocus": "true"})
    submit = SubmitField('Done')

class Instant_PayCode(FlaskForm):
    pay_amount = StringField('pay_amount', validators=[DataRequired()], render_kw={"placeholder": "Enter your token amount", "autofocus": "true"})
    submit = SubmitField('Done')

class Pay_Someone(FlaskForm):
    account_number = StringField('account_number', validators=[DataRequired()], render_kw={'maxlength': 12, "placeholder": "Enter Recipient Account", "autofocus": "true"})
    pay_amount = StringField('pay_amount', validators=[DataRequired()], render_kw={"placeholder": "Enter Payment Amount"})
    reference_name = StringField('reference name', validators=[DataRequired()], render_kw={"placeholder": "Enter Reference Here"})
    submit = SubmitField('Done')

class Confirm_Payment(FlaskForm):
    account_pin = PasswordField('account_pin', validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder": "enter password", "autofocus": "true"})
    submit = SubmitField('Confirm')

class Withdraw_Funds_Form(FlaskForm):
    withdraw_amount = StringField('pay_amount', validators=[DataRequired()], render_kw={"placeholder": "Enter your Withdraw amount", "autofocus": "true"})
    submit = SubmitField('Withdraw')

class Confirm_Withdrawal(FlaskForm):
    account_pin = PasswordField('account_pin', validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder": "enter password", "autofocus": "true"})
    submit = SubmitField('Confirm')

class Collect_Funds_Form(FlaskForm):
    withdraw_code = StringField('withdraw_code', validators=[DataRequired()], render_kw={"placeholder": "Voucher Code"})
    withdraw_pin = StringField('withdraw_pin', validators=[DataRequired()], render_kw={"placeholder": "Withdraw Pin"})
    submit = SubmitField('Done')

class Redeem_Paycode(FlaskForm):
    paycode = StringField('paycode', validators=[DataRequired(), Length(10)], render_kw={"placeholder": "Enter Voucher Code"})
    submit = SubmitField('Done')

class Load_Account(FlaskForm):
    account_name = StringField('first_name', validators=[DataRequired()], render_kw={'maxlength': 50, "placeholder": "Enter Account Name", "autofocus": "true"})
    account_number = StringField('account_number', validators=[DataRequired()], render_kw={'maxlength': 12, "placeholder": "Enter Recipient Account"})
    load_amount = StringField('load_amount', validators=[DataRequired()], render_kw={"placeholder": "Amount"})
    submit = SubmitField('Done')