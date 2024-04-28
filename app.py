from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/server_settings')
def server_settings():
    return render_template('server_settings.html')

@app.route('/servers')
def servers():
    return render_template('servers.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)