

 # Import libraries
from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from flaskext.mysql import MySQL
from functools import wraps
import yaml
import os

app = Flask(__name__)

# app.config.from_object(os.environ['APP_SETTINGS'])
app.config.update(SECRET_KEY='dontyouworrychild83!')

# # Configure database
# db = yaml.safe_load(open('db.yaml'))
# app.config['MYSQL_HOST'] = db['mysql_host']
# app.config['MYSQL_USER'] = db['mysql_user']
# app.config['MYSQL_PASSWORD'] = db['mysql_password']
# app.config['MYSQL_DB'] = db['mysql_db']

# Database connection info. Note that this is not a secure connection.
app.config['MYSQL_DATABASE_USER'] = 'joshsamsmith'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Thelorry!'
app.config['MYSQL_DATABASE_DB'] = 'drive_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

# Initialize MySQL
mysql = MySQL()
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

# Login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

# Endpoint for inserting data dynamically in the database
@app.route('/track', methods=['GET', 'POST'])
@login_required
def insert():
    if request.method == "POST":
        spend = request.form['fuel_spend']
        litre = request.form['fuel_litre']
        cursor.execute("INSERT INTO dim_trans (fuel_spend, fuel_litre) Values (%s,%s)", (spend, litre))
        conn.commit()
        return redirect("/home", code=302)
    return render_template('track.html')

# Endpoint for home
@app.route('/home')
@login_required
def home():
    if request.method == "GET":
        cursor.execute("SELECT sum(fuel_spend) as total_spend, sum(fuel_litre) as total_litre FROM dim_trans")
        conn.commit()
        data = cursor.fetchall()
        return render_template('index.html', data=data)
    return render_template('index.html')

# Endpoint for welcome
@app.route('/')
def welcome():
    return render_template('welcome.html')

# Endpoint for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin123!':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            # flash('You are logged in!')
            return redirect("/home")
    return render_template('login.html', error=error)

# Endpoint for login
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    # flash('You are logged out!')
    return redirect("/")


if __name__ == "__main__":
    app.debug = True
    app.run()
