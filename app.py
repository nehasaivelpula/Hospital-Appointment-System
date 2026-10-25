
from flask import Flask, render_template, request
import sqlite3
from datetime import date

app = Flask(__name__)
DATABASE = "hospital.db"

doctors = [
    {"id": 1, "name": "Dr. Priya Sharma",
     "specialization": "Cardiologist"},
    {"id": 2, "name": "Dr. Rahul Verma",
     "specialization": "Dermatologist"},
    {"id": 3, "name": "Dr. Ananya Rao",
     "specialization": "Pediatrician"}
]


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                email TEXT NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


@app.route("/")
def home():
    return render_template(
        "index.html",
        doctors=doctors,
        today=date.today().isoformat()
    )


@app.route("/book", methods=["POST"])
def book_appointment():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    doctor_id = request.form.get("doctor", "")
    appointment_date = request.form.get("date", "")

    doctor = next(
        (d for d in doctors if str(d["id"]) == doctor_id),
        None
    )

    if not name or not email or not doctor or not appointment_date:
        return "Please fill in all details.", 400

    try:
        selected_date = date.fromisoformat(appointment_date)
    except ValueError:
        return "Invalid appointment date.", 400

    if selected_date < date.today():
        return "Please select today or a future date.", 400

    with get_db() as conn:
        conn.execute("""
            INSERT INTO appointments
            (patient_name, email, doctor_id, appointment_date)
            VALUES (?, ?, ?, ?)
        """, (name, email, doctor["id"], appointment_date))

    return render_template(
        "confirmation.html",
        name=name,
        email=email,
        doctor=doctor,
        date=appointment_date
    )


if __name__ == "__main__":
    create_table()
    app.run(debug=True)
