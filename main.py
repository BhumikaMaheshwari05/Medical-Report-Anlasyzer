from flask import Flask, render_template, redirect, request, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import date
from flask_bcrypt import Bcrypt
from PyPDF2 import PdfReader
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key')  # Set in Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///MedRep.db').replace("postgres://", "postgresql://", 1)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Gemini AI Setup
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("API key is not set. Please set the 'GOOGLE_API_KEY' environment variable.")
genai.configure(api_key=api_key)

# Database Models
class Login(db.Model):
    __tablename__ = 'login'
    Username = db.Column(db.String(80), nullable=False, unique=True)
    Email = db.Column(db.String(80), primary_key=True)
    Password = db.Column(db.String(150), nullable=False)
    reports = db.relationship('Prevreports', backref='user_email', lazy=True)

class Prevreports(db.Model):
    __tablename__ = 'prevreports'
    Sno = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(80), db.ForeignKey('login.Email'), nullable=False)
    Name = db.Column(db.String(80), nullable=False)
    Report = db.Column(db.String(150), nullable=False)
    File = db.Column(db.String(200), nullable=False)
    Date = db.Column(db.String(80), nullable=True)

class Contact(db.Model):
    __tablename__ = 'contact'
    Sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(10), nullable=False)
    Email = db.Column(db.String(80), nullable=False)
    PhoneNo = db.Column(db.String(10), nullable=False)
    Subject = db.Column(db.String(150), nullable=False)
    Message = db.Column(db.String(500), nullable=False)
    Date = db.Column(db.String(80), nullable=True)

# Helper Functions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages[:1]:  # Only first page
        if (page_text := page.extract_text()):
            text += page_text + "\n\n"
    return text.strip()

# Initialize Database
with app.app_context():
    db.create_all()

# Routes
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login", methods=["GET", "POST"])
def log():
    if request.method == "POST":
        usr = request.form.get("usr")
        passw = request.form.get("password")
        if user := Login.query.filter_by(Username=usr).first():
            if bcrypt.check_password_hash(user.Password, passw):
                session['user'] = usr
                return redirect("/dashboard")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def reg():
    if request.method == "POST":
        usr = request.form.get("usr")
        email = request.form.get("email")
        passw = bcrypt.generate_password_hash(request.form.get("password"))
        db.session.add(Login(Username=usr, Email=email, Password=passw))
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/dashboard")
def dash():
    if 'user' in session:
        if user := Login.query.filter_by(Username=session['user']).first():
            data = Prevreports.query.filter_by(Email=user.Email).all()
            return render_template("dashboard.html", data=data)
    return redirect("/login")

@app.route("/dashboard/rpt", methods=["GET", "POST"])
def rept():
    if request.method == "POST" and (file := request.files.get('file')):
        if allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # For Render: Either comment out save() or use cloud storage
            file.save(file_path)  # Temporary - will disappear on redeploy
            
            if 'user' in session:
                if user := Login.query.filter_by(Username=session['user']).first():
                    db.session.add(Prevreports(
                        Name=request.form.get('name'),
                        Email=user.Email,
                        Report=request.form.get('reportof'),
                        File=filename,
                        Date=date.today()
                    ))
                    db.session.commit()
            
            return redirect(f"/dashboard/rpt/analyze?filename={filename}")
    return render_template("reportsub.html")

@app.route("/dashboard/rpt/analyze")
def report():
    if not (filename := request.args.get('filename')):
        return render_template("report.html", error="No file specified")
    
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        prompt = extract_text_from_pdf(file_path)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt + "Analyze this medical report. Explain all terms and compare with normal values. Provide a summary."
        )
        
        return render_template('report.html', text=response.text)
    except Exception as e:
        return render_template("report.html", error=f"Error processing file: {str(e)}")

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)