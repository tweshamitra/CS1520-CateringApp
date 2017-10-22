from flask import Flask, flash, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.update(dict(
    DEBUG= True,
    SECRET_KEY= 'development key',
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'catering.db')
))

db = SQLAlchemy()

class Owner(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique = True)
    password = db.Column(db.String(80), unique = True)

    def __repr__(self):
        return "<Owner {}>".format(repr(self.username))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique = True)
    password = db.Column(db.String(80), unique = True)

    def __init__(self, username, password):
        self.username = username
        self.password = password 

    def __repr__(self):
        return "<Customer {}>".format(repr(self.username))

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), unique=True)
    events = db.relationship('Event', backref='person', lazy ='select')

    def __repr__(self):
        return "<Staff {}>".format(repr(self.username))


class Event(db.Model):
    id=db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime)
    title = db.Column(db.String(80))
    location = db.Column(db.String(100))
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

    def __repr__(self):
        return "<Event {}>".format(repr(self.title))

# events = db.Table('events',db.Column('event_id', db.Integer, db.ForeignKey('event.id'),primary_key=True),db.Column('staff_id', db.Integer, db.ForeignKey('staff.id'),primary_key=True))

db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
    db.drop_all()
    db.create_all()
    db.session.add(Owner(username = "owner", password="pass"))
    db.session.commit()
    print("Initialized the database")

@app.route("/")
def default():
    return redirect(url_for("login"))

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["role"] == "owner":
            if Owner.query.filter_by(username = request.form["user"], password = request.form["pass"]).first() != None: 
                return profile(role = request.form["role"])
            else:
                print("Invalid credentials, try again")
                return default()            
    return render_template("login.html")

@app.route("/<role>")
def profile(role = None):
    if role == "Owner":
        return redirect(url_for(owner))
        
@app.route("/owner/")
def owner():
    return render_template("owner.html")

# @app.route("/customer/")
# def customer():
#     return render_template("customer.html")

# @app.route("/staff/")

# def staff():
#     return render_template("staff.html")

# @app.route("/logout/")
# def unlogger():
#     if "username" in session:
#         session.clear()

if __name__ == '__main__':
    app.run(port=5000, host='localhost')    


#session.pop removes user for logout 