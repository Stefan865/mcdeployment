from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
import requests


class TicketForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Detailed Description', validators=[DataRequired()])
    user = StringField('User', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def send_to_trello(self):
        # Replace with your Trello API key and token
        api_key = 'f3bf6e2d6bc89fc7b7d957f8d93fc676'
        token = 'ATTA661c74b7631b54dda1b8e193da905021202daf39ee0a6e5c404a56970bb7304b291498F1'
        board_id = 'tAH1wePJ'  # ID of the Trello board where cards will be created
        list_id = '6677f12b2631b502c6a72bb5'  # ID of the Trello list where cards will be added

        url = f"https://api.trello.com/1/cards?key={api_key}&token={token}&idList={list_id}"
        payload = {
            'name': self.title.data,
            'desc': f"User: {self.user.data}\n\n{self.body.data}",
            'idList': list_id  # Specify the list ID explicitly in the payload
        }

        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return True
        else:
            return False
