print("RUNNING PRJ FILE ✅")

import random
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# OTP storage
otp_store = {}

# ================= MODELS =================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(10))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    status = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

# ================= ROUTES =================

@app.route('/')
def home():
    return "Server running"

# ✅ TEST ROUTE
@app.route('/check')
def check():
    return "OK"

# Signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    user = User(
        username=data['username'],
        password=generate_password_hash(data['password']),
        role=data['role']
    )

    db.session.add(user)
    db.session.commit()

    return {"msg": "User created"}

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(username=data['username']).first()

    if user and check_password_hash(user.password, data['password']):
        return {"msg": "Login success", "role": user.role}

    return {"msg": "Invalid credentials"}

# Send OTP
@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    username = data['username']

    otp = str(random.randint(1000, 9999))
    otp_store[username] = otp

    print("OTP:", otp)

    return {"msg": "OTP sent"}

# Verify OTP
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()

    if otp_store.get(data['username']) == data['otp']:
        return {"msg": "OTP verified"}

    return {"msg": "Invalid OTP"}

# ✅ CREATE PROJECT
@app.route('/create_project', methods=['POST'])
def create_project():
    data = request.get_json()

    project = Project(
        name=data['name'],
        user_id=1
    )

    db.session.add(project)
    db.session.commit()

    return {"msg": "Project created"}

# ✅ CREATE TASK
@app.route('/create_task', methods=['POST'])
def create_task():
    data = request.get_json()

    task = Task(
        title=data['title'],
        status="pending",
        user_id=1,
        project_id=data['project_id']
    )

    db.session.add(task)
    db.session.commit()

    return {"msg": "Task created"}

# ✅ GET TASKS (Dashboard)
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()

    result = []
    for t in tasks:
        result.append({
            "title": t.title,
            "status": t.status
        })

    return jsonify(result)

# ================= RUN =================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)