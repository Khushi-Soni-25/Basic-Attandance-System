# 📅 Basic Attendance System

A simple and user-friendly **Office Attendance Tracking System** built using Flask and SQLite. This web application allows users to register, log in, manage daily attendance records, and export attendance data.

## 🚀 Features

- 🔐 User Registration and Login
- 📅 Daily Attendance Management
- ✅ Multiple Attendance Statuses:
  - Present
  - First Half Leave
  - Second Half Leave
  - Holiday
  - Absent
- 📝 Add Notes to Attendance Records
- 📊 Attendance Summary Dashboard
- 📋 View Recent and All Attendance Records
- 📥 Export Attendance Data to CSV
- 📊 Export Attendance Data to Excel
- 🔒 Password Hashing for Secure Storage
- 📱 Responsive and User-Friendly Interface

## 🛠️ Technologies Used

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Database:** SQLite
- **Authentication:** Flask Sessions
- **Deployment:** Render
- **Server:** Gunicorn

## 📂 Project Structure

```text
Basic-Attendance-System/
│
├── app.py
├── requirements.txt
├── render.yaml
├── users.json
│
├── data/
│   └── Khushi_2506.json
│
├── static/
│   ├── script.js
│   └── style.css
│
└── templates/
    ├── index.html
    ├── login.html
    └── register.html
```

## ⚙️ Installation and Setup

1. Clone the Repository
git clone https://github.com/Khushi-Soni-25/Basic-Attandance-System.git
2. Navigate to the Project Directory
cd Basic-Attandance-System
3. Create a Virtual Environment
python -m venv venv
4. Activate the Virtual Environment

Windows:
venv\Scripts\activate

Linux / macOS:
source venv/bin/activate

5. Install Dependencies
pip install -r requirements.txt

7. Run the Application
python app.py

9. Open in Browser
http://127.0.0.1:5000

## 📌 How It Works
Create a new account using the registration page.
Log in using your credentials.
Access the attendance dashboard.
Add daily attendance records.
View and manage attendance history.
Export attendance records as CSV or Excel files.

## 🔐 Security
Passwords are stored using password hashing.
User sessions are used for authentication.
Attendance records are associated with individual users.
Input validation is applied to attendance records.

##🌐 Deployment

The application can be deployed using Render with Gunicorn.

The project includes a render.yaml configuration file for deployment.

## 🔮 Future Improvements
Monthly and yearly attendance reports
Attendance percentage calculation
Admin dashboard
Email notifications
Improved database management
Attendance analytics and charts

### 👩‍💻 Author

*Khushi B. Soni*

B.E. Information Technology Student
