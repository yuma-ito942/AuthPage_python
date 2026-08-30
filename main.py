from flask import Flask,render_template,request,redirect,url_for,session,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)

# User database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


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
                flash("Login success")
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


if __name__ == "__main__":
    app.run(debug=True)