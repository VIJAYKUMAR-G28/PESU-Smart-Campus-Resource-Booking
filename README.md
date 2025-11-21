PESU Smart Campus Resource Booking System 🏫📅

A robust, backend-focused application designed to manage and book campus resources (Auditoriums, Labs, Seminar Halls) at PES University. This project utilizes Python for application logic and MySQL for persistent data storage, operating via a Command Line Interface (CLI).

📖 Table of Contents

About the Project

Features

Database Schema

Prerequisites

Installation & Setup

Usage

Future Scope

🧐 About the Project

This system replaces manual ledger entries with a relational database approach. It handles user authentication, resource management, and conflict detection for bookings directly through the terminal.

Key capabilities:

Admin Mode: Full control over adding rooms, viewing all bookings, and managing users.

User Mode: Faculty/Students can check availability and book slots.

Conflict Resolution: The SQL logic prevents double-booking of the same room at the same time.

✨ Features

🖥️ Interface (CLI)

Interactive Menu: Text-based navigation for login, booking, and viewing history.

Input Validation: Python logic ensures dates and times are entered correctly.

🗄️ Backend (MySQL)

Authentication: Secure login verification against the users table.

Resource Catalog: distinct storage for different venue types (Auditoriums, Classrooms).

Booking Logic: SQL queries to check for OVERLAPS before confirming a slot.

History & Logs: persistent storage of past and upcoming bookings.

🗃 Database Schema

The system relies on the following core tables:

users: Stores Student/Faculty details and login credentials (SRN/Employee ID, Password, Role).

resources: Stores venue details (Resource ID, Name, Type, Capacity, Location).

bookings: Links Users to Resources (Booking ID, User ID, Resource ID, Start Time, End Time, Status).

⚙ Prerequisites

Ensure you have the following installed on your machine:

Python 3.x: Download Here

MySQL Server: Download Here

MySQL Connector: The Python driver for communicating with the database.

🚀 Installation & Setup

1. Clone the Repository

git clone [https://github.com/your-username/pesu-resource-booking.git](https://github.com/your-username/pesu-resource-booking.git)
cd pesu-resource-booking


2. Install Python Dependencies

You need the MySQL connector to allow Python to talk to your database.

pip install mysql-connector-python
# or
pip3 install mysql-connector-python


3. Database Configuration

Open your MySQL Command Line Client or Workbench.

Create the database and tables using the provided SQL script (or manually):

CREATE DATABASE pesu_booking;
USE pesu_booking;

-- Example Table Creation
CREATE TABLE resources (
    r_id INT PRIMARY KEY AUTO_INCREMENT,
    r_name VARCHAR(50),
    capacity INT,
    type VARCHAR(30)
);
-- (Import the rest of your schema here)


Update Database Credentials: Open main.py (or your database connection file) and update the connection parameters:

db = mysql.connector.connect(
    host="localhost",
    user="root",        # Your MySQL username
    password="password", # Your MySQL password
    database="pesu_booking"
)


🎮 Usage

To run the application, execute the main Python script from your terminal:

python main.py


Sample Workflow:

Login/Register: Select Option 1 to Login as Admin or Student.

View Resources: Select "View All Resources" to see IDs of rooms like "MRD Auditorium".

Book: Enter the Resource ID and your desired Time Slot (YYYY-MM-DD HH:MM).

Confirmation: If the slot is free, the system confirms the booking and saves it to MySQL.

🔮 Future Scope

GUI Integration: Adding a Tkinter or PyQt5 interface for a windowed experience.

Web API: Converting the Python logic into a Flask/FastAPI backend to support a web frontend.

Email Notifications: Using Python's smtplib to send booking confirmations via email.

👥 Contributors

VIJAY KUMAR G - Backend Logic  
TRIGUN GURUMURTI - Database Design

📄 License

This project is open-source and available under the MIT License.
