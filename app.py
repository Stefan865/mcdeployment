from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from mcrcon import MCRcon
import random
import bcrypt


app = Flask(__name__)

bcrypt2 = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:7073@localhost/test'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


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
    ip_address = db.Column(db.String(20), nullable=True)
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


@app.route('/services')
def services():
    return render_template('services.html')


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


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and bcrypt2.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


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
        server_address = ('35.159.107.238', 25575)
        password = 'rconpassword123'
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
    # Extract form data
    server_name = request.form['serverName']
    tiers = request.form['tiers']
    seed = request.form['option']
    game_mode = request.form['option0']
    flavor_text = request.form['option1']
    difficulty = request.form['option2']
    online_status = request.form['option3']
    pvp_enabled = request.form['option4']
    max_players = int(request.form['option5'])
    max_chunks = int(request.form['option6'])
    hardcore = request.form['option7']
    generate_structures = request.form['option8']

    # Save server name and tier to the database
    user = Users.query.filter_by(user_id=current_user.user_id).first()
    if user:
        user.server_name = server_name  # Use the extracted server_name variable
        user.tier = tiers  # Keep using tiers for the tier information
        db.session.commit()

    # Placeholder for where you would send the data to the external service
    # Once integrated, replace this with the actual API call
    # Example: response = requests.post('http://external-service.com/api', json=server_data)

    # Process the response from the external service (if any)

    # Redirect to dashboard
    return redirect(url_for('dashboard'))


@app.route('/start_server', methods=['POST'])
@login_required
def start_server():
    flash("Server started successfully.")
    return redirect(url_for('dashboard'))


@app.route('/stop_server', methods=['POST'])
@login_required
def stop_server():
    flash("Server stopped successfully.")
    return redirect(url_for('dashboard'))


@app.route('/delete_server', methods=['POST'])
@login_required
def delete_server():
    user_id = current_user.get_id()
    user = Users.query.get(int(user_id))
    server_name_to_delete = request.form.get('server_name')

    if user and user.server_name:
        servers = user.server_name.split(',')
        if server_name_to_delete in servers:
            servers.remove(server_name_to_delete)
            user.server_name = ','.join(servers)
            db.session.commit()
            flash(f"Server {server_name_to_delete} deleted successfully.", "success")
        else:
            flash("Server not found or invalid server name.", "error")
    else:
        flash("User not found or user has no servers.", "error")

    return redirect(url_for('dashboard'))


@app.route('/submit_servers', methods=['POST'])
@login_required
def submit_servers():
    selected_servers = request.form.getlist('server')
    user = Users.query.filter_by(user_id=current_user.user_id).first()
    if user:
        user.server_name = ','.join(selected_servers)
        db.session.commit()
        flash('Servers updated successfully!')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True, port=80)
