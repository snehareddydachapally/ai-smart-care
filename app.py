from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/register_user', methods=['POST'])
def register_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    age = request.form['age']
    gender = request.form['gender']
    phone = request.form['phone']
    blood_group = request.form['blood_group']
    doctor = request.form['doctor']
    visit_type = request.form['visit_type']
    uhid = request.form['uhid']

    db = get_db()
    db.execute(
        "INSERT INTO users (name,email,password,age,gender,phone,blood_group,doctor,visit_type,uhid) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (name,email,password,age,gender,phone,blood_group,doctor,visit_type,uhid)
    )
    db.commit()

    return redirect('/login')


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/login_user', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    db = get_db()
    user = db.execute(
        "SELECT name FROM users WHERE email=? AND password=?",
        (email,password)
    ).fetchone()

    if user:
        username = user["name"]
        return redirect('/dashboard/' + username)

    return "Invalid Login"


@app.route('/dashboard/<username>')
def dashboard(username):
    db = get_db()

    medicines = db.execute(
        "SELECT * FROM medicines WHERE user_name=?",
        (username,)
    ).fetchall()

    return render_template(
        "dashboard.html",
        medicines=medicines,
        username=username
    )


@app.route('/add_medicine/<username>')
def add_medicine(username):
    return render_template("add_medicine.html", username=username)


@app.route('/save_medicine', methods=['POST'])
def save_medicine():
    user_name = request.form['user_name']
    medicine_name = request.form['medicine_name']
    dosage = request.form['dosage']
    reminder_time = request.form['reminder_time']

    db = get_db()
    db.execute(
        "INSERT INTO medicines (user_name,medicine_name,dosage,reminder_time) VALUES (?,?,?,?)",
        (user_name,medicine_name,dosage,reminder_time)
    )
    db.commit()

    return redirect('/dashboard/' + user_name)


@app.route('/health_record/<username>')
def health_record(username):
    return render_template("health_record.html", username=username)


@app.route('/medical_history/<username>')
def medical_history(username):
    db = get_db()

    history = db.execute(
        "SELECT * FROM medical_history WHERE user_name=?",
        (username,)
    ).fetchall()

    return render_template(
        "medical_history.html",
        history=history,
        username=username
    )


@app.route('/save_history', methods=['POST'])
def save_history():
    username = request.form['user_name']
    condition = request.form['condition_name']
    diagnosis_date = request.form['diagnosis_date']
    treatment = request.form['treatment']
    notes = request.form['notes']

    db = get_db()
    db.execute(
        "INSERT INTO medical_history (user_name,condition_name,diagnosis_date,treatment,notes) VALUES (?,?,?,?,?)",
        (username,condition,diagnosis_date,treatment,notes)
    )
    db.commit()

    return redirect('/medical_history/' + username)


@app.route('/upload_report/<username>')
def upload_report(username):
    return render_template("upload_report.html", username=username)


@app.route('/save_report', methods=['POST'])
def save_report():
    username = request.form['user_name']
    file = request.files['report']

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    db = get_db()
    db.execute(
        "INSERT INTO reports (user_name,file_name) VALUES (?,?)",
        (username,filename)
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

    return render_template(
        "view_reports.html",
        reports=reports,
        username=username
    )


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
    elif "cold" in message:
        reply = "Common cold symptoms include sneezing and sore throat."
    else:
        reply = "Please consult a doctor for serious medical issues."

    return jsonify({"response": reply})


@app.route('/consult/<username>')
def consult(username):
    db = get_db()

    doctors = db.execute(
        "SELECT doctor_name,specialization,experience,location FROM doctors"
    ).fetchall()

    return render_template(
        "consult.html",
        username=username,
        doctors=doctors
    )


@app.route('/video_call')
def video_call():
    return render_template("video_call.html")


@app.route('/book_appointment/<username>', methods=['GET','POST'])
def book_appointment(username):
    if request.method == 'POST':
        doctor = request.form['doctor']
        date = request.form['date']
        time = request.form['time']
        problem = request.form['problem']

        db = get_db()
        db.execute(
            "INSERT INTO appointments (patient_name,doctor_name,date,time,problem) VALUES (?,?,?,?,?)",
            (username,doctor,date,time,problem)
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

    return render_template(
        "my_appointments.html",
        username=username,
        appointments=appointments
    )
def create_tables():
    db = get_db()

    # USERS TABLE
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

    # MEDICINES TABLE
    db.execute('''CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        medicine_name TEXT,
        dosage TEXT,
        reminder_time TEXT
    )''')

    # APPOINTMENTS TABLE
    db.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        doctor_name TEXT,
        date TEXT,
        time TEXT,
        problem TEXT
    )''')

    # 👉 ADD HERE 👇 (NEW TABLES)

    # MEDICAL HISTORY TABLE
    db.execute('''CREATE TABLE IF NOT EXISTS medical_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        condition_name TEXT,
        diagnosis_date TEXT,
        treatment TEXT,
        notes TEXT
    )''')

    # REPORTS TABLE
    db.execute('''CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        file_name TEXT
    )''')

    # SAVE CHANGES
    db.commit()


if __name__ == '__main__':
    create_tables()
    app.run(host="0.0.0.0", port=5000, debug=True)
