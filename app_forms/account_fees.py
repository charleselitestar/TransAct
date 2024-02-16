from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, DateField, SubmitField
from wtforms.validators import DataRequired,Length 

class App_Account_Fees(FlaskForm):
    deposits = FloatField('deposits', validators=[DataRequired()])
    withdrawals = FloatField('withdrawals',validators=[DataRequired()] )
    paycodes = FloatField('paycodes', validators=[DataRequired()])
    payments = FloatField('payments', validators=[DataRequired()])
    submit = SubmitField('Done')

class Account_limits(FlaskForm):
    withdrawal = FloatField('withdrawal', validators=[DataRequired()] )
    paycode = FloatField('paycode', validators=[DataRequired()])
    payments = FloatField('payments', validators=[DataRequired()])
    daily = FloatField('daily', validators=[DataRequired()])
    weekly = FloatField('weekly', validators=[DataRequired()])
    monthly = FloatField('monthly', validators=[DataRequired()])
    submit = SubmitField('Done')

    