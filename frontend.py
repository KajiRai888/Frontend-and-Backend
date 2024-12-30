import streamlit as st
import requests

# Backend URL
backend_url = "http://127.0.0.1:5000"

st.title("Student Admission Form - TU")

# Manual Form Submission
st.header("Enter Student Information")
with st.form("admission_form"):
    name = st.text_input("Full Name:")
    age = st.number_input("Age:", min_value=1, step=1)
    email = st.text_input("Email:")
    course = st.selectbox("Select Course:", ["", "Computer Science", "Management", "Arts", "Law"])
    submitted = st.form_submit_button("Submit")

if submitted:
    if not all([name, age, email, course]):
        st.error("All fields are required!")
    else:
        response = requests.post(
            f"{backend_url}/submit_form",
            json={"name": name, "age": age, "email": email, "course": course},
        )
        if response.status_code == 200:
            st.success(response.json().get("message"))
        else:
            st.error(response.json().get("error"))

# File Upload
st.header("Upload Student Data (CSV or Excel)")
uploaded_file = st.file_uploader("Choose a file (CSV or Excel)", type=["csv", "xlsx"])
if st.button("Upload"):
    if uploaded_file:
        files = {"file": uploaded_file}
        response = requests.post(f"{backend_url}/upload", files=files)
        if response.status_code == 200:
            st.success(response.json().get("message"))
        else:
            st.error(response.json().get("error"))
    else:
        st.error("Please upload a file first!")

# View Students
if st.button("View Students"):
    response = requests.get(f"{backend_url}/students")
    if response.status_code == 200:
        students = response.json()
        if students:
            st.subheader("Admitted Students")
            for student in students:
                st.write(f"Name: {student['name']}, Age: {student['age']}, Email: {student['email']}, Course: {student['course']}")
        else:
            st.info("No students admitted yet.")

# Clear All Students
if st.button("Clear All Students"):
    response = requests.delete(f"{backend_url}/clear_students")
    if response.status_code == 200:
        st.success(response.json().get("message"))
    else:
        st.error("Failed to clear student data.")

# Download Data
st.header("Download Student Data")
download_format = st.selectbox("Choose download format:", ["CSV", "Excel"])
if st.button("Download"):
    if download_format == "CSV":
        download_url = f"{backend_url}/download?format=csv"
    else:
        download_url = f"{backend_url}/download?format=excel"
    st.markdown(f"[Download {download_format}]({download_url})", unsafe_allow_html=True)
