from flask import Flask,render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

#app.secret_key = 'super-secret-key'


app.config['SQLALCHEMY_DATABASE_URI']="mysql+mysqlconnector://root:@localhost/medrep"

db = SQLAlchemy(app) 

class Prevreports(db.Model):
    table_name='prevreports'
    Sno=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(80),nullable=False)
    Report=db.Column(db.String(150),nullable=False)
    Date=db.Column(db.String(80),nullable=True)


class Contact(db.Model):
    table_name='contact'
    Sno=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(10),nullable=False)
    Email=db.Column(db.String(80),nullable=False)
    PhoneNo=db.Column(db.String(10),nullable=False)
    Subject=db.Column(db.String(150),nullable=False)
    Message=db.Column(db.String(500),nullable=False)
    Date=db.Column(db.String(80),nullable=True)
    


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/login")
def log():
    return render_template("login.html")

@app.route("/register")
def reg():
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
    data=Prevreports.query.filter_by().all()
    return render_template("indexdsh.html",data=data)

if __name__ == "__main__":
    app.run(debug=True)

