from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from mcrcon import MCRcon
app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    machines = db.relationship('Machine', backref='owner', lazy=True)


class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class MachineForm(FlaskForm):
    name = StringField('Machine Name', validators=[InputRequired()])
    submit = SubmitField('Create Machine')


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=80)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()

        if existing_user_username:
            raise ValidationError(
                "That username already exists. Please choose a different one.")


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
    machines = Machine.query.filter_by(user_id=current_user.id).all()
    machine_count = len(machines)
    return render_template('dashboard.html', machines=machines, machine_count=machine_count)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/server_settings')
@login_required
def server_settings():
    user_id = current_user.id
    return render_template('server_settings.html', user_id=user_id)


@app.route('/servers')
def servers():
    return render_template('servers.html')


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
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
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


@app.route('/start_server', methods=['POST'])
@login_required
def start_server():
    # Your logic to start the server
    flash("Server started successfully.")
    return redirect(url_for('dashboard'))


@app.route('/stop_server', methods=['POST'])
@login_required
def stop_server():
    # Your logic to stop the server
    flash("Server stopped successfully.")
    return redirect(url_for('dashboard'))


@app.route('/create_machine', methods=['GET', 'POST'])
@login_required
def create_machine():
    form = MachineForm()
    if Machine.query.filter_by(user_id=current_user.id).first():
        flash("You have already created a machine. You can't create more than one machine.")
        return redirect(url_for('dashboard'))
    if form.validate_on_submit():
        new_machine = Machine(name=form.name.data, user_id=current_user.id)
        db.session.add(new_machine)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('create_machine.html', form=form)


@app.route('/delete_machine/<int:machine_id>', methods=['POST'])
@login_required
def delete_machine(machine_id):
    machine = Machine.query.get(machine_id)
    if machine:
        db.session.delete(machine)
        db.session.commit()
        return redirect(url_for('dashboard'))
    else:
        return "Machine not found or cannot be deleted"


if __name__ == '__main__':
    app.run(debug=True)
