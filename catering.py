from flask import Flask, flash, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os

app = Flask(__name__)
app.config.update(dict(
    DEBUG= True,
    SECRET_KEY= 'development key',
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'catering.db')
))

db = SQLAlchemy()

staff_members = db.Table('staff_members',db.Column('event_id', db.Integer, db.ForeignKey('event.id')),db.Column('staff_id', db.Integer, db.ForeignKey('staff.id')))

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
    event_requested = db.Column(db.Integer, db.ForeignKey('event.id'))

    def __repr__(self):
        return "<Customer {}>".format(repr(self.username))

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), unique=True)
    staffs = db.relationship('Event', secondary = staff_members, backref= db.backref('staffMembers', lazy = 'dynamic'))
    # event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    def __repr__(self):
        return "<Staff {}>".format(repr(self.username))


class Event(db.Model):
    id=db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80))
    date = db.Column(db.Date())
    customer_id = db.relationship("Customer", backref = "event", lazy = "dynamic")
    #staff = db.relationship("Staff", backref = "event", lazy = "dynamic")
    events = db.relationship('Staff', secondary = staff_members, backref = db.backref('events', lazy = 'dynamic'))
    def __repr__(self):
        return "<Event {}>".format(repr(self.title))


db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
    db.drop_all()
    db.create_all()
    o = Owner(username = "owner", password="pass")
    db.session.add(o)
    e1 = Event(title ="Lunch", date = date(2017,11,1))
    e2 = Event(title = "Wedding", date = date(2017,11,15))
    e3 = Event(title = "Birthday", date = date(2017,12,15))
    db.session.add(e1)
    db.session.add(e2)
    db.session.add(e3)
    s1 = Staff(username = "twesha", password = "mitra")
    s2 = Staff(username = "jane", password = "doe")
    s3 = Staff(username = "jack", password = "hello")
    # s1.events.append(e1)
    # s1.events.append(e2)
    # s2.events.append(e2)
    # s3.events.append(e3)
    e1.staffMembers.append(s1)
    e2.staffMembers.append(s1)
    e2.staffMembers.append(s2)
    e3.staffMembers.append(s3)
   
    db.session.commit()
    print("Initialized the database")

@app.route("/")
def default():
    return redirect(url_for("login"))

@app.route("/login", methods = ["GET", "POST"])
def login():
    session['logged_in'] = False
    if request.method == "POST":
        if Owner.query.filter_by(username = request.form["user"], password = request.form["pass"]).first() != None: 
            session['logged_in'] = True
            return redirect(url_for("owner"))
        elif Staff.query.filter_by(username = request.form["user"], password = request.form["pass"]).first() != None:
            session['logged_in'] = True
            return redirect(url_for("staff", username= request.form["user"]))
        elif Customer.query.filter_by(username = request.form["user"], password = request.form["pass"]).first() != None:
            session['logged_in'] = True
            return redirect(url_for("customer", username = request.form["user"]))
        else:
            flash("No profile found! Register a new customer account below")
    return render_template("login.html")

@app.route('/staff/<username>')
def staff(username = None):
    staff = Staff.query.filter_by(username = username).first()
    events = Event.query.all()
    return render_template("staff.html", staff=staff, events = events)

@app.route('/new_customer', methods = ["GET", "POST"])
def create_customer():
    if request.method == "POST":
        c = Customer(username = request.form["username"], password = request.form["password"])
        db.session.add(c)
        db.session.commit()
        flash("New customer account created")
        return redirect(url_for("login"))
    return render_template("create_customer.html")
    
@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    session['logged_in'] = False
    return redirect(url_for('login'))     

@app.route("/owner", methods = ["GET", "POST"])
def owner():
    events = Event.query.all()
    return render_template("owner.html", events = events)

    
@app.route("/customer/<username>", methods = ["GET", "POST"])
def customer(username = None):
    if request.method == "POST":
        c = Customer(username = request.form["username"], password = request.form["password"])
        db.session.add(c)
        db.session.commit()
    session['logged_in'] = True 
    return render_template("customer.html")
    
@app.route("/request-event", methods = ["GET", "POST"])
def request_event():
    if request.method == "POST":
        curr_date = request.form['event_date']
        year,month,day = curr_date.split('-')
        event_date = date(int(year),int(month),int(day))
        e = Event(title = request.form["event_title"], date = event_date)
        db.session.add(e)
        db.session.commit()
        flash('event request created')
    return render_template("request.html")

@app.route('/create-staff', methods = ["GET", "POST"])
def create_staff():
    if request.method == "POST":
        s = Staff(username = request.form["username"], password = request.form["password"])
        db.session.add(s)
        db.session.commit()
        flash("New staff account created")
        return redirect(url_for("owner"))
    session['logged_in'] = True
    return render_template("create_staff.html")


if __name__ == '__main__':
    app.run(port=5000, host='localhost')    


