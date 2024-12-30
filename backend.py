from flask import Flask, request, jsonify, Response
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io

app = Flask(__name__)

# Mock database to store student data
students = []

# Function to send an email
def send_email(student):
    sender_email = "raikajijp@gmail.com"  # Replace with your email address
    sender_password = "Kai123JP"         # Replace with your email password or app-specific password
    receiver_email = "hellonepal017@gmail.com"

    subject = "New Student Submission Notification"
    body = f"""
    A new student has been submitted:

    Name: {student['name']}
    Age: {student['age']}
    Email: {student['email']}
    Course: {student['course']}
    """

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/')
def home():
    html_content = """
    <html>
    <head>
        <title>Admitted Students</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Admitted Students</h1>
    """

    if students:
        html_content += """
        <table>
            <tr>
                <th>Name</th>
                <th>Age</th>
                <th>Email</th>
                <th>Course</th>
            </tr>
        """
        for student in students:
            html_content += f"""
            <tr>
                <td>{student['name']}</td>
                <td>{student['age']}</td>
                <td>{student['email']}</td>
                <td>{student['course']}</td>
            </tr>
            """
        html_content += "</table>"
    else:
        html_content += "<p>No students admitted yet.</p>"

    html_content += """
    <br>
    <a href="/download?format=csv" target="_blank">
        <button>Download CSV</button>
    </a>
    <a href="/download?format=excel" target="_blank">
        <button>Download Excel</button>
    </a>
    <br><br>
    <h3>Send a Manual Email</h3>
    <form action="/send-email" method="POST">
        <input type="email" name="recipient" placeholder="Recipient Email" required>
        <input type="text" name="subject" placeholder="Subject" required>
        <textarea name="message" placeholder="Message" required></textarea>
        <button type="submit">Send Email</button>
    </form>
    </body>
    </html>
    """
    return html_content

@app.route('/send-email', methods=['POST'])
def send_manual_email():
    recipient = request.form.get('recipient')
    subject = request.form.get('subject')
    message_body = request.form.get('message')

    sender_email = "raikajijp@gmail.com"  # Replace with your email address
    sender_password = "Kaji123JP"         # Replace with your email password or app-specific password

    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(message_body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, message.as_string())

        return jsonify({"status": "success", "message": "Email sent successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/submit_form', methods=['POST'])
def submit_form():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    email = data.get('email')
    course = data.get('course')

    if not all([name, age, email, course]):
        return jsonify({"error": "All fields are required!"}), 400

    for student in students:
        if student['name'] == name and student['email'] == email:
            return jsonify({"error": "This student has already been submitted!"}), 400

    student = {"name": name, "age": age, "email": email, "course": course}
    students.append(student)

    send_email(student)

    return jsonify({"message": "Student admitted successfully!", "student": student}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided!"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file!"}), 400

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return jsonify({"error": "Invalid file format. Only CSV or Excel files are allowed!"}), 400

        new_students = df.to_dict(orient='records')
        added_count = 0
        for student in new_students:
            if all(key in student for key in ['name', 'age', 'email', 'course']):
                if not any(s['name'] == student['name'] and s['email'] == student['email'] for s in students):
                    students.append(student)
                    send_email(student)
                    added_count += 1

        return jsonify({"message": f"File uploaded successfully! {added_count} new students added."}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

@app.route('/download', methods=['GET'])
def download_data():
    file_format = request.args.get('format', 'csv').lower()

    if not students:
        return jsonify({"error": "No data available to download!"}), 400

    df = pd.DataFrame(students)

    if file_format == 'csv':
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=students.csv"}
        )
    elif file_format == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Students')
        output.seek(0)
        return Response(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment;filename=students.xlsx"}
        )
    else:
        return jsonify({"error": "Invalid format. Please choose 'csv' or 'excel'."}), 400

@app.route('/clear_students', methods=['DELETE'])
def clear_students():
    global students
    students.clear()
    return jsonify({"message": "All student data has been cleared!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
