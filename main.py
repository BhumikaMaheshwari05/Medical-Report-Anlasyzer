from flask import Flask,render_template,redirect,request,session,send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import date

from flask_bcrypt import Bcrypt

from PyPDF2 import PdfReader

import os
import google.generativeai as genai


api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("API key is not set. Please set the 'GOOGLE_API_KEY' environment variable.")

genai.configure(api_key=api_key)




app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'fallback-key-for-dev')


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///MedRep.db').replace("postgres://", "postgresql://", 1)

db = SQLAlchemy(app) 

bcrypt=Bcrypt(app)


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
      # Not primary key.
    Username = db.Column(db.String(80), nullable=False,unique=True)
    Email = db.Column(db.String(80), primary_key=True)  # Fix: This should be primary key, as defined.
    Password = db.Column(db.String(150), nullable=False)
    
    # Relationship to Prevreports model
    reports = db.relationship('Prevreports', backref='user_email',lazy=True)


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    

    for page_num in range(0,1):
        page = reader.pages[page_num]
        page_text = page.extract_text()
        

        if page_text:  
            text += page_text + "\n\n"
    
    return text.strip()  # Strip any leading or trailing whitespace





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
        entry=Contact(Name=name,Email=email,PhoneNo=phone,Subject=subject,Message=msg,Date=date.today())
        db.session.add(entry)
        db.session.commit()
        return redirect("/")
    return render_template("contact.html")

@app.route("/dashboard")
def dash():
    if('user' in session):
        user=Login.query.filter_by(Username=session['user']).first()
        if user:
            x=Prevreports.query.filter_by(Email=user.Email).first()
            data=Prevreports.query.filter_by(Email=user.Email).all()
            return render_template("dashboard.html",data=data,x=x)
    else:
        return render_template('dashboard.html',x='user')
    #return render_template("indexdsh.html",data=data)
    
@app.route("/logout")
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route("/dashboard/rpt",methods=["GET","POST"])
def rept():
    if 'user' in session:
        user = Login.query.filter_by(Username=session['user']).first()
        if user:
            if request.method == "POST":
                name = request.form.get('name')
                report = request.form.get('reportof')
                email = user.Email
                file = request.files['file']  
                if file and allowed_file(file.filename):
                    filename = file.filename
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)  
                    
                    entry = Prevreports(Name=name, Email=email, Report=report, File=filename, Date=date.today())
                    db.session.add(entry)
                    db.session.commit()
                    return redirect(f"/dashboard/rpt/analyze?filename={filename}")
                
    else:
        if request.method == "POST":
                
                file = request.files['file']  
                
                if file and allowed_file(file.filename):
                    filename = file.filename
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)   
        
                    
                    return redirect(f"/dashboard/rpt/analyze?filename={filename}")
                
    
    return render_template("reportsub.html")



generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)
chat_session = model.start_chat(
  history=[
  ]
)


@app.route("/dashboard/rpt/analyze")
def report():
    
    filename = request.args.get('filename')  # Get the filename from the query parameter
    if filename:
        # Serve the file directly
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        prmpt=extract_text_from_pdf(file_path)
        texts = chat_session.send_message(prmpt+"Give full information about the test and the teminologies used and also tellwhat should be the condition for the normal person for the same test and at the end summarize whole report")
        #texts=format_report_text(texts)
        #print(f"Extracted Text: {texts}")
        return render_template('report.html',text=texts.text)
    # Pass filename to the templatec
    return render_template("report.html", error="No report found or you are not logged in.")
        #return render_template("report.html")





@app.route("/dashboard/yourpdf<string:filename>")
def yrrpt(filename):

    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render provides PORT
    app.run(host='0.0.0.0', port=port)

