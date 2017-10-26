from flask import Flask, flash, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config.update(dict(
    DEBUG= True,
    SECRET_KEY= 'development key',
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'catering.db')
))

db = SQLAlchemy()
# catering_events = db.Table('cateringEvents', db.Column('event_id', db.Integer, db.ForeignKey('event.id')), db.Column('staff_id', db.Integer, db.ForeignKey('staff.id')))

class Owner(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique = True)
    password = db.Column(db.String(80), unique = True)
    events = db.relationship("Event", backref = "owner", lazy = "dynamic")

    def __repr__(self):
        return "<Owner {}>".format(repr(self.username))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique = True)
    password = db.Column(db.String(80), unique = True)
    # event = db.relationship('Event', secondary = 'events', backref= 'customer', lazy = 'dynamic')

    def __repr__(self):
        return "<Customer {}>".format(repr(self.username))

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), unique=True)
    events = db.relationship("Event", backref = "staff", lazy = "dynamic")
    # event_signed_up = db.relationship('Event', backref='staff', lazy ='dynamic')
    # event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    # events = db.relationship('Event', secondary=catering_events, backref=db.backref('staffID'), lazy = 'dynamic')

    def __repr__(self):
        return "<Staff {}>".format(repr(self.username))


class Event(db.Model):
    id=db.Column(db.Integer, primary_key = True)
    #d ate = db.Column(db.Date, nullable = False)
    title = db.Column(db.String(80))
    # staff = db.relationship("Staff", backref = "event", lazy = "dynamic")
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'))
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

    def __repr__(self):
        return "<Event {}>".format(repr(self.title))


db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
    db.drop_all()
    db.create_all()
    o = Owner(username = "owner", password="pass")
    db.session.add(o)
    s1 = Staff(username = "twesha", password = "mitra" )
    s2 = Staff(username = "jane", password = "password")
    s3 = Staff(username = "jack", password = "hello")
    db.session.add(Event(title ="Lunch", owner = o, staff = s1))
    db.session.add(Event(title = "Wedding", owner = o, staff = s2))
    db.session.add(Event(title = "Funeral", owner = o, staff = s1))
    db.session.add(Event(title = "Birthday", owner = o, staff = s3))
    print(o.events)
    db.session.commit()
    print("Initialized the database")

@app.route("/")
def default():
    return redirect(url_for("login"))

@app.route("/login", methods = ["GET", "POST"])
def login():
    session['logged_in'] = False
    if request.method == "POST":
        if request.form["role"] == "owner":
            if Owner.query.filter_by(username = request.form["user"], password = request.form["pass"]).first() != None: 
                session['logged_in'] = True
                return redirect(url_for("owner"))
            else:
                print("Invalid credentials, try again")
                return default()      
        elif request.form["role"] == "staff":
            if Staff.query.filter_by(username = request.form["user"], password = request.form["pass"]).first() != None:
                print ("profile exists")
            else:
                print("no profile found. Ask owner to create a profile for you")      
        elif request.form["role"] == "customer":
            if Customer.query.filter_by(username = request.form["user"], password = request.form["pass"]).first() != None:
                return redirect(url_for("customer"))
            else:
                print("No profile found. register new account below")
    return render_template("login.html")

@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    session['logged_in'] = False
    return redirect(url_for('login'))     

@app.route("/owner", methods = ["GET", "POST"])
def owner():
    events = Event.query.all()
    staff_members = Staff.query.all()
    if request.method == 'POST':
        s = Staff(username = request.form["username"], password = request.form["password"])
        db.session.add(s)
        db.session.commit()
    return render_template("owner.html", events = events, staff_members = staff_members)

    
@app.route("/customer", methods = ["GET", "POST"])
def customer():
    if request.method == "POST":
        c = Customer(username = request.form["username"], password = request.form["password"])
        db.session.add(c)
        db.session.commit()
    session['logged_in'] = True 
    return render_template("customer.html")

@app.route("/add", methods = ['POST'])
def create_event():
    if request.method == "POST":
        e = Event(title = request.form["event_title"])
        db.session.add(e)
        db.session.commit()
        flash('event request created')
    return redirect(url_for('customer'))



if __name__ == '__main__':
    app.run(port=5000, host='localhost')    


