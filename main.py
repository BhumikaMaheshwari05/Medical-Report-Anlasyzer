from flask import Flask,render_template,redirect,request,session
from flask_sqlalchemy import SQLAlchemy
<<<<<<< HEAD
import os
from datetime import date
=======

from datetime import datetime
>>>>>>> a4162b5599d2e740851d6c89aedbd7568bcf4947

from flask_bcrypt import Bcrypt
app = Flask(__name__)

app.secret_key = 'super-secret-key'


app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///MedRep.db"

db = SQLAlchemy(app) 

bcrypt=Bcrypt(app)

<<<<<<< HEAD

app.config['UPLOAD_FOLDER'] = 'uploads'  # Directory to store uploaded files
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size: 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Prevreports(db.Model):
    __tablename__ = 'prevreports'  # Fix: Table name should be double-underscored.
    Sno = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(80), db.ForeignKey('login.Email'),nullable=False)  # Fix: Correct foreign key table name 'login.Email'.
    Name = db.Column(db.String(80), nullable=False) 
    Report = db.Column(db.String(150), nullable=False)
    File=db.Column(db.String(200),nullable=False)
    Date = db.Column(db.String(80), nullable=True)
    
    # Relationship to Login model
    
=======
class Prevreports(db.Model):
    __tablename__ = 'prevreports'  # Fix: Table name should be double-underscored.
    Sno = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(80), db.ForeignKey('login.Email'))  # Fix: Correct foreign key table name 'login.Email'.
    Name = db.Column(db.String(80), nullable=False)
    Report = db.Column(db.String(150), nullable=False)
    Date = db.Column(db.String(80), nullable=True)
    
    # Relationship to Login model
    login_cred = db.relationship('Login', back_populates='user_reports')
>>>>>>> a4162b5599d2e740851d6c89aedbd7568bcf4947


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
<<<<<<< HEAD
      # Not primary key.
    Username = db.Column(db.String(80), nullable=False,unique=True)
=======
    Sno = db.Column(db.Integer)  # Not primary key.
    Username = db.Column(db.String(80), nullable=False)
>>>>>>> a4162b5599d2e740851d6c89aedbd7568bcf4947
    Email = db.Column(db.String(80), primary_key=True)  # Fix: This should be primary key, as defined.
    Password = db.Column(db.String(150), nullable=False)
    
    # Relationship to Prevreports model
<<<<<<< HEAD
    reports = db.relationship('Prevreports', backref='user_email',lazy=True)
=======
    user_reports = db.relationship('Prevreports', back_populates='login_cred',lazy=True)
>>>>>>> a4162b5599d2e740851d6c89aedbd7568bcf4947


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
<<<<<<< HEAD
        entry=Contact(Name=name,Email=email,PhoneNo=phone,Subject=subject,Message=msg,Date=date.today())
=======
        entry=Contact(Name=name,Email=email,PhoneNo=phone,Subject=subject,Message=msg,Date=datetime.now())
>>>>>>> a4162b5599d2e740851d6c89aedbd7568bcf4947
        db.session.add(entry)
        db.session.commit()
        return redirect("/")
    return render_template("contact.html")

@app.route("/dashboard")
def dash():
    if('user' in session):
        user=Login.query.filter_by(Username=session['user']).first()
        if user:
<<<<<<< HEAD
            data=Prevreports.query.filter_by(Email=user.Email).all()
=======
            data=Prevreports.query.filter_by().all()
>>>>>>> a4162b5599d2e740851d6c89aedbd7568bcf4947
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
<<<<<<< HEAD
    if 'user' in session:
        user = Login.query.filter_by(Username=session['user']).first()
        if user:
            if request.method == "POST":
                name = request.form.get('name')
                report = request.form.get('reportof')
                email = user.Email
                file = request.files['file']  # Fetch the file from the form
                
                if file and allowed_file(file.filename):#filename is the name of the file becoz file as a whole is poori file having bohut sari chheze and all..!!
                    filename = file.filename
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)  # Save file to the uploads folder
                    
                    # Store file path in database
                    entry = Prevreports(Name=name, Email=email, Report=report, File=filename, Date=date.today())
                    db.session.add(entry)
                    db.session.commit()
                    return redirect("/dashboard/rpt/analyze")
                else:
                    return "Invalid file type. Only images and PDFs are allowed."
    return render_template("reportsub.html")


@app.route("/dashboard/rpt/analyze")
def report():
    return render_template("report.html")

=======
    if request=="POST":
        name=request.form.get('name')
        report=request.form.get('reportof')
        
    return render_template("reportsub.html")

>>>>>>> a4162b5599d2e740851d6c89aedbd7568bcf4947
if __name__ == "__main__":
    app.run(debug=True)


