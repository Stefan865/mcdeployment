from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from mcrcon import MCRcon
import random
import bcrypt
from wtforms.validators import DataRequired
from forms import TicketForm
import requests
import socket
import time
import os

app = Flask(__name__)

bcrypt2 = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://webuserdb:math1234@ip-10-0-159-217.eu-central-1.compute.internal:5432/mchosting'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:7073@localhost:5432/test'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

API_BASE_URL = "https://429lybrh7e.execute-api.eu-central-1.amazonaws.com/prod"


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


def query_user_servers(user_id):
    users = Users.query.filter_by(user_id=user_id).first()
    if users and users.server_name:
        return users.server_name.split(',')
    else:
        return []


class Users(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    server_name = db.Column(db.String(20), nullable=True)
    subdomain = db.Column(db.String(20), nullable=True)
    tier = db.Column(db.String(20), nullable=True)

    def get_id(self):
        return str(self.user_id)


class User_id_setup():
    @staticmethod
    def generate_user_id():
        user_id = random.randint(100000, 999999)
        return user_id

    def validate_user_id(self):
        while True:
            new_user_id = self.generate_user_id()
            existing_user = Users.query.filter_by(user_id=new_user_id).first()
            if not existing_user:
                return new_user_id


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    email = StringField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=80)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = Users.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")

    def validate_email(self, email):
        existing_user_email = Users.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError("That email already exists. Please login.")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=80)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/service_desk', methods=['GET', 'POST'])
@login_required
def service_desk():
    form = TicketForm()
    form.user.data = current_user.username  # Pre-fill username field with current user

    if form.validate_on_submit():
        # Process the form data (e.g., save to Trello)
        if form.send_to_trello():
            return redirect(url_for('home'))  # Redirect to home or another page after submission
        else:
            # Handle error if card creation fails
            return "Failed to create Trello card. Please try again later."

    return render_template('service_desk.html', form=form)


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    user = Users.query.filter_by(user_id=current_user.user_id).first()
    if user:
        server_names = user.server_name.split(',') if user.server_name else []
        return render_template('dashboard.html', server_names=server_names, tier=user.tier)
    else:
        flash('No server information found.')
        return render_template('dashboard.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/delete_server', methods=['POST'])
@login_required
def delete_server():
    try:
        user = Users.query.filter_by(user_id=current_user.user_id).first()
        if user and user.server_name:
            server_name = user.server_name

            # Adjusting to use a query parameter for POST requests
            response = requests.post(f"{API_BASE_URL}/delete?user_id={user.user_id}")
            if response.status_code == 200:
                flash('Server deleted successfully!', 'success')
            else:
                flash('Failed to delete server.', 'danger')
        else:
            flash('User or server information not found.', 'danger')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))


@app.route('/server_settings', methods=['GET', 'POST'])
@login_required
def server_settings():
    if request.method == 'POST':
        server_name = request.form['server_name']
        tier = request.form['tier']
        user = Users.query.filter_by(user_id=current_user.user_id).first()
        if user:
            user.server_name = server_name
            user.tier = tier
            db.session.commit()
            flash('Server settings updated successfully!', 'success')
            return redirect(url_for('dashboard'))

    # Render the server_settings.html template for GET requests or errors
    return render_template('server_settings.html')


@app.route('/servers', methods=['GET', 'POST'])
@login_required
def servers():
    user_id = current_user.user_id
    servers = query_user_servers(user_id)
    return render_template('servers.html', servers=servers)


@app.route('/server_details', methods=['POST'])
@login_required
def server_details():
    server_name = request.form['server_name']
    user = Users.query.filter_by(user_id=current_user.user_id).first()
    server_info = {
        'server_name': server_name,
        'ip_address': user.ip_address,
        'tier': user.tier
    }
    return render_template('server_details.html', **server_info)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and bcrypt2.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/upgrade_tier', methods=['POST'])
@login_required
def upgrade_tier():
    try:
        new_tier = request.form['tier']
        user = Users.query.filter_by(user_id=current_user.user_id).first()
        if user:
            user.tier = new_tier
            db.session.commit()

            # Send parameters in the body of the POST request
            response = requests.post(
                f"{API_BASE_URL}/upgrade",
                json={'user_id': user.user_id, 'tier': new_tier}
            )

            if response.status_code == 200:
                flash('Tier upgraded successfully!', 'success')
            else:
                flash('Failed to upgrade tier through API.', 'danger')
        else:
            flash('User not found.', 'danger')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))


@app.route('/start_server', methods=['GET'])
@login_required
def start_server():
    try:
        user = Users.query.filter_by(user_id=current_user.user_id).first()
        if user and user.server_name:
            # Correctly passing user_id as a query parameter
            response = requests.get(f"{API_BASE_URL}/start?user_id={user.user_id}")
            if response.status_code == 200:
                flash('Server started successfully!', 'success')
            else:
                flash('Failed to start server.', 'danger')
        else:
            flash('User or server information not found.', 'danger')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))


@app.route('/stop_server', methods=['POST'])
@login_required
def stop_server():
    try:
        user = Users.query.filter_by(user_id=current_user.user_id).first()
        if user and user.server_name:
            server_name = user.server_name

            # Adjusting to use a query parameter for POST requests
            # Note: While this is unconventional for POST requests, it follows the corrected approach
            response = requests.post(f"{API_BASE_URL}/stop?user_id={user.user_id}")
            if response.status_code == 200:
                flash('Server stopped successfully!', 'success')
            else:
                flash('Failed to stop server.', 'danger')
        else:
            flash('User or server information not found.', 'danger')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    user_id_setup = User_id_setup()
    user_id = user_id_setup.validate_user_id()
    if user_id and form.validate_on_submit():
        hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = Users(user_id=user_id, username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/connect', methods=['GET', 'POST'])
def connect():
    message = ""
    if request.method == 'POST':
        command = request.form['command']
        server_address = (os.getenv('RCON_HOST'), int(os.getenv('RCON_PORT')))
        password = os.getenv('RCON_PASSWORD')
        try:
            with MCRcon(server_address, password) as rcon:
                response = rcon.execute(command)
                message = response.body.decode('utf-8')
        except Exception as e:
            message = f"Failed to send RCON command: {str(e)}"
    return render_template('connect.html', message=message)


@app.route('/create_server', methods=['POST'])
@login_required
def create_server():
    try:
        # Extract form data
        server_name = request.form['serverName']
        tier = request.form['tiers']
        level_seed = request.form.get('level_seed', '')
        gamemode = request.form.get('gamemode', 'survival')
        motd = request.form.get('motd', 'A Minecraft Server')
        pvp = request.form.get('pvp', 'true')
        difficulty = request.form.get('difficulty', 'easy')
        max_players = request.form.get('max_players', '20')
        online_mode = request.form.get('online_mode', 'true')
        view_distance = request.form.get('view_distance', '10')
        hardcore = request.form.get('hardcore', 'false')

        # Update user's server_name and tier in the database
        user = Users.query.filter_by(user_id=current_user.user_id).first()
        if user:
            user.server_name = server_name
            user.tier = tier
            db.session.commit()

        # Construct JSON payload for the API request
        server_data = {
            "user_id": str(current_user.user_id),  # Ensure user_id is a string
            "tier": tier,
            "server_settings": {
                "level_seed": level_seed,
                "gamemode": gamemode,
                "motd": motd,
                "pvp": pvp,
                "difficulty": difficulty,
                "max_players": max_players,
                "online_mode": online_mode,
                "view_distance": view_distance,
                "hardcore": hardcore
            }
        }

        # Send POST request to the API endpoint
        response = requests.post(f"{API_BASE_URL}/create", json=server_data)

        # Check response status and handle accordingly
        if response.status_code == 200:
            flash("Server created successfully!", 'success')
        else:
            flash("Failed to create server. Please try again.", 'danger')

        return redirect(url_for('dashboard'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('create_server'))


if __name__ == "__main__":
    app.run(debug=True)
