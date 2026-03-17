from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# -------- DATABASE --------
def get_db():
    db_path = os.path.join(os.getcwd(), "database.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# -------- CREATE TABLES --------
def create_tables():
    db = get_db()

    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT,
        age TEXT,
        gender TEXT,
        phone TEXT,
        blood_group TEXT,
        doctor TEXT,
        visit_type TEXT,
        uhid TEXT
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        medicine_name TEXT,
        dosage TEXT,
        reminder_time TEXT
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        doctor_name TEXT,
        date TEXT,
        time TEXT,
        problem TEXT
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS medical_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        condition_name TEXT,
        diagnosis_date TEXT,
        treatment TEXT,
        notes TEXT
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        file_name TEXT
    )''')

    db.commit()


# ✅ RUN TABLE CREATION
with app.app_context():
    create_tables()


# -------- ROUTES --------
@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/register_user', methods=['POST'])
def register_user():
    db = get_db()

    db.execute(
        "INSERT INTO users (name,email,password,age,gender,phone,blood_group,doctor,visit_type,uhid) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            request.form['name'],
            request.form['email'],
            request.form['password'],
            request.form['age'],
            request.form['gender'],
            request.form['phone'],
            request.form['blood_group'],
            request.form['doctor'],
            request.form['visit_type'],
            request.form['uhid']
        )
    )

    db.commit()
    return redirect('/login')


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/login_user', methods=['POST'])
def login_user():
    db = get_db()

    user = db.execute(
        "SELECT name FROM users WHERE email=? AND password=?",
        (request.form['email'], request.form['password'])
    ).fetchone()

    if user:
        return redirect('/dashboard/' + user["name"])

    return "Invalid Login"


# ✅ FIXED DASHBOARD (IMPORTANT)
@app.route('/dashboard/<username>')
def dashboard(username):
    db = get_db()

    medicines = db.execute(
        "SELECT * FROM medicines WHERE user_name=?",
        (username,)
    ).fetchall()

    # 🔥 FIX: Convert Row → dict
    medicines = [dict(row) for row in medicines]

    return render_template("dashboard.html", medicines=medicines, username=username)


# -------- MEDICINES --------
@app.route('/add_medicine/<username>')
def add_medicine(username):
    return render_template("add_medicine.html", username=username)


@app.route('/save_medicine', methods=['POST'])
def save_medicine():
    db = get_db()

    db.execute(
        "INSERT INTO medicines (user_name,medicine_name,dosage,reminder_time) VALUES (?,?,?,?)",
        (
            request.form['user_name'],
            request.form['medicine_name'],
            request.form['dosage'],
            request.form['reminder_time']
        )
    )

    db.commit()
    return redirect('/dashboard/' + request.form['user_name'])


# -------- HEALTH RECORD --------
@app.route('/health_record/<username>')
def health_record(username):
    return render_template("health_record.html", username=username)


# -------- MEDICAL HISTORY --------
@app.route('/medical_history/<username>')
def medical_history(username):
    db = get_db()

    history = db.execute(
        "SELECT * FROM medical_history WHERE user_name=?",
        (username,)
    ).fetchall()

    history = [dict(row) for row in history]

    return render_template("medical_history.html", history=history, username=username)


@app.route('/save_history', methods=['POST'])
def save_history():
    db = get_db()

    db.execute(
        "INSERT INTO medical_history (user_name,condition_name,diagnosis_date,treatment,notes) VALUES (?,?,?,?,?)",
        (
            request.form['user_name'],
            request.form['condition_name'],
            request.form['diagnosis_date'],
            request.form['treatment'],
            request.form['notes']
        )
    )

    db.commit()
    return redirect('/medical_history/' + request.form['user_name'])


# -------- REPORTS --------
@app.route('/upload_report/<username>')
def upload_report(username):
    return render_template("upload_report.html", username=username)


@app.route('/save_report', methods=['POST'])
def save_report():
    db = get_db()

    username = request.form['user_name']
    file = request.files['report']

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    db.execute(
        "INSERT INTO reports (user_name,file_name) VALUES (?,?)",
        (username, filename)
    )

    db.commit()
    return redirect('/dashboard/' + username)


@app.route('/view_reports/<username>')
def view_reports(username):
    db = get_db()

    reports = db.execute(
        "SELECT * FROM reports WHERE user_name=?",
        (username,)
    ).fetchall()

    reports = [dict(row) for row in reports]

    return render_template("view_reports.html", reports=reports, username=username)


# -------- CHATBOT --------
@app.route('/chatbot/<username>')
def chatbot(username):
    return render_template("chatbot.html", username=username)


@app.route('/get_response', methods=['POST'])
def get_response():
    message = request.json['message'].lower()

    if "fever" in message:
        reply = "Symptoms include fever, headache and body pain."
    elif "headache" in message:
        reply = "Headaches may occur due to stress or dehydration."
    else:
        reply = "Please consult a doctor."

    return jsonify({"response": reply})


# -------- VIDEO CALL --------
@app.route('/video_call')
def video_call():
    return render_template("video_call.html")


# -------- APPOINTMENTS --------
@app.route('/book_appointment/<username>', methods=['GET', 'POST'])
def book_appointment(username):
    if request.method == 'POST':
        db = get_db()

        db.execute(
            "INSERT INTO appointments (patient_name,doctor_name,date,time,problem) VALUES (?,?,?,?,?)",
            (
                username,
                request.form['doctor'],
                request.form['date'],
                request.form['time'],
                request.form['problem']
            )
        )

        db.commit()
        return redirect('/dashboard/' + username)

    return render_template("book_appointment.html", username=username)


@app.route('/my_appointments/<username>')
def my_appointments(username):
    db = get_db()

    appointments = db.execute(
        "SELECT doctor_name,date,time,problem FROM appointments WHERE patient_name=?",
        (username,)
    ).fetchall()

    appointments = [dict(row) for row in appointments]

    return render_template("my_appointments.html", username=username, appointments=appointments)
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)