from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL connection
import sqlite3

db = sqlite3.connect("database.db", check_same_thread=False)
cursor = db.cursor()


# HOME PAGE
@app.route('/')
def home():
    return render_template("index.html")


# REGISTER PAGE
@app.route('/register')
def register():
    return render_template("register.html")


# SAVE USER
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

    sql = """INSERT INTO users
    (name,email,password,age,gender,phone,blood_group,doctor,visit_type,uhid)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    cursor.execute(sql,(name,email,password,age,gender,phone,blood_group,doctor,visit_type,uhid))
    db.commit()

    return redirect('/login')


# LOGIN PAGE
@app.route('/login')
def login():
    return render_template("login.html")


# LOGIN USER
@app.route('/login_user', methods=['POST'])
def login_user():

    email = request.form['email']
    password = request.form['password']

    sql = "SELECT name FROM users WHERE email=%s AND password=%s"
    cursor.execute(sql,(email,password))
    user = cursor.fetchone()

    if user:
        username = user[0]
        return redirect('/dashboard/' + username)

    return "Invalid Login"


# DASHBOARD
@app.route('/dashboard/<username>')
def dashboard(username):

    cursor.execute("SELECT * FROM medicines WHERE user_name=%s",(username,))
    medicines = cursor.fetchall()

    medicines_list = []

    for m in medicines:
        m = list(m)
        m[4] = str(m[4])
        medicines_list.append(m)

    return render_template("dashboard.html", medicines=medicines_list, username=username)


# ADD MEDICINE PAGE
@app.route('/add_medicine/<username>')
def add_medicine(username):
    return render_template("add_medicine.html", username=username)


# SAVE MEDICINE
@app.route('/save_medicine', methods=['POST'])
def save_medicine():

    user_name = request.form['user_name']
    medicine_name = request.form['medicine_name']
    dosage = request.form['dosage']
    reminder_time = request.form['reminder_time']

    sql = """INSERT INTO medicines
    (user_name,medicine_name,dosage,reminder_time)
    VALUES (%s,%s,%s,%s)"""

    cursor.execute(sql,(user_name,medicine_name,dosage,reminder_time))
    db.commit()

    return redirect('/dashboard/' + user_name)


# HEALTH RECORD PAGE
@app.route('/health_record/<username>')
def health_record(username):
    return render_template("health_record.html", username=username)


# MEDICAL HISTORY
@app.route('/medical_history/<username>')
def medical_history(username):

    cursor.execute("SELECT * FROM medical_history WHERE user_name=%s",(username,))
    history = cursor.fetchall()

    return render_template("medical_history.html", history=history, username=username)


# SAVE MEDICAL HISTORY
@app.route('/save_history', methods=['POST'])
def save_history():

    username = request.form['user_name']
    condition = request.form['condition_name']
    diagnosis_date = request.form['diagnosis_date']
    treatment = request.form['treatment']
    notes = request.form['notes']

    cursor.execute(
        "INSERT INTO medical_history (user_name,condition_name,diagnosis_date,treatment,notes) VALUES (%s,%s,%s,%s,%s)",
        (username,condition,diagnosis_date,treatment,notes)
    )

    db.commit()

    return redirect('/medical_history/' + username)


# UPLOAD REPORT PAGE
@app.route('/upload_report/<username>')
def upload_report(username):
    return render_template("upload_report.html", username=username)


# SAVE REPORT
@app.route('/save_report', methods=['POST'])
def save_report():

    username = request.form['user_name']
    file = request.files['report']

    filename = secure_filename(file.filename)

    file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

    cursor.execute(
        "INSERT INTO reports (user_name,file_name) VALUES (%s,%s)",
        (username,filename)
    )

    db.commit()

    return redirect('/dashboard/' + username)


# VIEW REPORTS
@app.route('/view_reports/<username>')
def view_reports(username):

    cursor.execute("SELECT * FROM reports WHERE user_name=%s",(username,))
    reports = cursor.fetchall()

    return render_template("view_reports.html", reports=reports, username=username)


# AI CHATBOT PAGE
@app.route('/chatbot/<username>')
def chatbot(username):
    return render_template("chatbot.html", username=username)


# CHATBOT RESPONSE
@app.route('/get_response', methods=['POST'])
def get_response():

    user_message = request.json['message'].lower()

    if "viral fever" in user_message:
        reply = "Symptoms include fever, headache, body pain and fatigue."

    elif "headache" in user_message:
        reply = "Headaches may occur due to stress or dehydration."

    elif "cold" in user_message:
        reply = "Common cold symptoms include sneezing and sore throat."

    else:
        reply = "Please consult a doctor for serious medical conditions."

    return jsonify({"response": reply})


# CONSULT PAGE (CONNECTED TO DOCTOR DATASET)
@app.route('/consult/<username>')
def consult(username):

    cursor.execute("SELECT doctor_name, specialization, experience, location FROM doctors")
    doctors = cursor.fetchall()

    return render_template("consult.html", username=username, doctors=doctors)


# SAVE CONSULT
@app.route('/save_consult', methods=['POST'])
def save_consult():

    username = request.form['user_name']
    doctor = request.form['doctor']
    problem = request.form['problem']

    cursor.execute(
        "INSERT INTO consultations (user_name,doctor_name,problem,status) VALUES (%s,%s,%s,'Pending')",
        (username,doctor,problem)
    )

    db.commit()

    return redirect('/dashboard/' + username)

@app.route('/video_call')
def video_call():
    return render_template('video_call.html')

@app.route('/book_appointment/<username>', methods=['GET','POST'])
def book_appointment(username):

    if request.method == 'POST':

        doctor = request.form['doctor']
        date = request.form['date']
        time = request.form['time']
        problem = request.form['problem']

        cursor.execute(
        "INSERT INTO appointments(patient_name,doctor_name,date,time,problem) VALUES(%s,%s,%s,%s,%s)",
        (username,doctor,date,time,problem)
        )

        db.commit()

        return redirect('/dashboard/' + username)

    return render_template("book_appointment.html", username=username)

    @app.route('/my_appointments/<username>')
    def my_appointments(username):

     cursor.execute(
    "SELECT doctor_name,date,time,problem FROM appointments WHERE patient_name=%s",
    (username,)
    )

    appointments = cursor.fetchall()

    return render_template(
        "my_appointments.html",
        username=username,
        appointments=appointments
    )
@app.route('/my_appointments/<username>')
def my_appointments(username):

    cursor.execute(
        "SELECT doctor_name, date, time, problem FROM appointments WHERE patient_name=%s",
        (username,)
    )

    appointments = cursor.fetchall()

    return render_template(
        "my_appointments.html",
        username=username,
        appointments=appointments
    )
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)