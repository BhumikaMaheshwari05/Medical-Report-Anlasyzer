from flask import Flask,render_template,redirect,request,session
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

from flask_bcrypt import Bcrypt
app = Flask(__name__)

app.secret_key = 'super-secret-key'


app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///MedRep.db"

db = SQLAlchemy(app) 

bcrypt=Bcrypt(app)

class Prevreports(db.Model):
    __tablename__ = 'prevreports'  # Fix: Table name should be double-underscored.
    Sno = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(80), db.ForeignKey('login.Email'))  # Fix: Correct foreign key table name 'login.Email'.
    Name = db.Column(db.String(80), nullable=False)
    Report = db.Column(db.String(150), nullable=False)
    Date = db.Column(db.String(80), nullable=True)
    
    # Relationship to Login model
    login_cred = db.relationship('Login', back_populates='user_reports')


class Contact(db.Model):
    table_name='contact'
    Sno=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(10),nullable=False)
    Email=db.Column(db.String(80),nullable=False)
    PhoneNo=db.Column(db.String(10),nullable=False)
    Subject=db.Column(db.String(150),nullable=False)
    Message=db.Column(db.String(500),nullable=False)
    Date=db.Column(db.String(80),nullable=True)
    


class Login(db.Model):
    __tablename__ = 'login'
    Sno = db.Column(db.Integer)  # Not primary key.
    Username = db.Column(db.String(80), nullable=False)
    Email = db.Column(db.String(80), primary_key=True)  # Fix: This should be primary key, as defined.
    Password = db.Column(db.String(150), nullable=False)
    
    # Relationship to Prevreports model
    user_reports = db.relationship('Prevreports', back_populates='login_cred',lazy=True)


with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template('index.html')


@app.route("/login",methods=["GET","POST"])
def log():
    if request.method=="POST":
        usr=request.form.get("usr")
        passw=request.form.get("password")
        user=Login.query.filter_by(Username=usr).first()
        if user:
            if bcrypt.check_password_hash(user.Password,passw):
                session['user']=usr
                return redirect("/dashboard") 
    return render_template("login.html")

@app.route("/register",methods=["GET","POST"])
def reg():
    if request.method=="POST":
        usr=request.form.get("usr")
        email=request.form.get("email")
        passw=bcrypt.generate_password_hash(request.form.get("password"))
        entry=Login(Username=usr,Email=email,Password=passw)
        db.session.add(entry)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")


@app.route("/forget")
def hui():
    
    return render_template("forget.html")

@app.route("/contact",methods=["GET","POST"])
def contact():
    if request.method=="POST":
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        subject=request.form.get('subject')
        msg=request.form.get('message')
        entry=Contact(Name=name,Email=email,PhoneNo=phone,Subject=subject,Message=msg,Date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        return redirect("/")
    return render_template("contact.html")

@app.route("/dashboard")
def dash():
    if('user' in session):
        user=Login.query.filter_by(Username=session['user']).first()
        if user:
            data=Prevreports.query.filter_by().all()
            return render_template("dashboard.html",data=data)
    else:
        return redirect('/login')
    #return render_template("indexdsh.html",data=data)
    
@app.route("/logout")
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route("/dashboard/rpt",methods=["GET","POST"])
def rept():
    if request=="POST":
        name=request.form.get('name')
        report=request.form.get('reportof')
        
    return render_template("reportsub.html")

if __name__ == "__main__":
    app.run(debug=True)


