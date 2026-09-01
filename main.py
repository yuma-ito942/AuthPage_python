from flask import Flask,render_template,request,redirect,url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png","jpg","jpeg","webp"}
def allowed_file(filename):
    return(
        "." in filename
        and filename.split(".",1)[1].lower() in ALLOWED_EXTENSIONS
    )


app = Flask(__name__)

app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path,
    "static",
    "uploads"
)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)

# User database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)


with app.app_context():
    db.create_all()

@app.route("/dashboard")
def dashboard():
    if session: 
        return render_template(
            "dashboard.html",
            session = session
        )
    else:
        return redirect(url_for('indexPage'))

@app.route("/")
def indexPage():
    return render_template("index.html")

@app.route("/login",methods = ['GET','POST'])
def loginAuth():
    if request.method == "POST":
        useremail = request.form.get("email")
        userpassword = request.form.get("password")
        if useremail != "" and userpassword != "":
            user = User.query.filter_by(email = useremail).first()
            if user and userpassword == user.password:
                session['user_id'] = user.id
                session['email'] = user.email
                session['name'] = user.name
                session['password'] = user.password
                session['avatar'] = user.avatar
                # flash("Login success")
                return redirect(url_for("dashboard"))
        flash("Invalid email or password.")

    return render_template("login.html")

@app.route("/register",methods = ['GET','POST'])
def registerAuth(): 
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password") 
    if request.method == 'POST':
        if name != '' and email != '' and password != '':
            new_user  = User(
                name  = name,
                email = email,
                password = password
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("loginAuth"))
            
    return render_template("register.html")

@app.route("/logout",methods = ['GET'])
def logout():
    session.clear() 
    return redirect(url_for("indexPage"))

@app.route("/profile",methods = ["POST"])
def updateProfile():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
 
    if request.method == 'POST':
        user = User.query.filter_by(email = email).first()
        if user:
            user.name = name
            user.password = password
            session['user_id'] = user.id
            session['email'] = user.email
            session['name'] = user.name
            session['password'] = user.password
            flash("Profile updated successfully")
            return redirect(url_for("dashboard")) 
    return render_template("dashboard.html")

@app.route("/avatar",methods = ['POST'])
def change_avatar():
    user = User.query.filter_by(email = session['email']).first()
        # print("user",user)
    file = request.files['avatar']
    if not allowed_file(file.filename):
        flash("not allowed")
        return redirect(url_for("dashboard"))
    
    
    extesion = file.filename.split(".",1)[1].lower()
    filename = f"user_{session['user_id']}.{extesion}"
    filepath = os.path.join(
        app.config['UPLOAD_FOLDER'],
        filename
    )
    if user.avatar:
        old_file = os.path.join(
            app.config['UPLOAD_FOLDER'],
            user.avatar
        ) 
        if os.path.exists(old_file):
            os.remove(old_file)
    file.save(filepath)
    user.avatar = filename
    session['avatar'] = user.avatar
    db.session.commit()
    flash("Upload success")
    return redirect(url_for("dashboard"))

@app.route("/avatar",methods = ['DELETE'])
def remove_avatar():
    session['avatar'] = None
    user = User.query.filter_by(email = session['email']).first()
    old_file = os.path.join(
        app.config['UPLOAD_FOLDER'],user.avatar
    )
    if os.path.exists(old_file):
        os.remove(old_file)
    user.avatar = None
    db.session.commit()
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)