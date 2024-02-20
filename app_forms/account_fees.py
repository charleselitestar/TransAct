from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField, IntegerField
from wtforms.validators import DataRequired,Length 

class App_Account_Fees(FlaskForm):
    deposits = IntegerField('deposits', validators=[DataRequired()])
    withdrawals = IntegerField('withdrawals',validators=[DataRequired()] )
    paycodes = IntegerField('paycodes', validators=[DataRequired()])
    payments = IntegerField('payments', validators=[DataRequired()])
    submit = SubmitField('Done')

class Account_limits(FlaskForm):
    withdrawal = IntegerField('withdrawal', validators=[DataRequired()] )
    paycode = IntegerField('paycode', validators=[DataRequired()])
    payments = IntegerField('payments', validators=[DataRequired()])
    daily = IntegerField('daily', validators=[DataRequired()])
    weekly = IntegerField('weekly', validators=[DataRequired()])
    monthly = IntegerField('monthly', validators=[DataRequired()])
    submit = SubmitField('Done')

    