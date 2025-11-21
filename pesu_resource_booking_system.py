import mysql.connector
import re
import getpass  
import datetime

def get_db_connection(user, password):
    """Establishes a database connection for the given user."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user=user,
            password=password,
            database="pesu_resource_booking_system"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"🚫 Database Connection Error: {err}")
        print("Please check username/password or if the MySQL server is running.")
        return None

# CRUD Operations
def list_students(cursor):
    print("\n--- Students ---")
    cursor.execute("SELECT * FROM tb_Student")
    for row in cursor.fetchall():
        print(row)

def list_faculty(cursor):
    print("\n--- Faculty ---")
    cursor.execute("SELECT * FROM tb_Faculty")
    for row in cursor.fetchall():
        print(row)

def list_departments(cursor):
    print("\n--- Departments ---")
    cursor.execute("SELECT * FROM tb_Department")
    for row in cursor.fetchall():
        print(row)

def list_resources(cursor):
    print("\n--- Resources ---")
    
    query = """
        SELECT 
            r.R_id, 
            r.RName, 
            r.Type, 
            r.Location, 
            IF(EXISTS (
                SELECT 1 
                FROM tb_Booking b
                WHERE b.R_id = r.R_id
                  AND b.status = 'approved'
                  AND b.B_date = CURDATE()  -- Check if the booking is for today
                  AND NOW() BETWEEN b.From_time AND b.To_time -- Check if it's active now
            ), 'Booked', 'Available') AS Current_Status,
            r.D_id
        FROM tb_Resource r;
    """
    
    cursor.execute(query)
    for row in cursor.fetchall():
        print(row)

def list_bookings(cursor):
    print("\n--- Bookings ---")
    # Join Query
    cursor.execute("""
        SELECT b.B_id, 
               COALESCE(s.Name, f.FName) AS Booker, 
               IF(s.Name IS NOT NULL, 'Student', 'Faculty') AS Booker_Type,
               r.RName, b.B_date, b.From_time, b.To_time, b.Purpose, b.status
        FROM tb_Booking b
        LEFT JOIN tb_Student s ON b.SRN = s.SRN
        LEFT JOIN tb_Faculty f ON b.Fid = f.Fid
        JOIN tb_Resource r ON b.R_id = r.R_id
    """)
    for row in cursor.fetchall():
        print(f"BookingID: {row[0]}, Booker: {row[1]} ({row[2]}), Resource: {row[3]}, "
              f"Date: {row[4]}, Time: {row[5]}-{row[6]}, Purpose: {row[7]}, Status: {row[8]}")

# Insert Operations
def insert_student(conn, cursor):
    srn = input("Enter SRN: ").strip()
    srn_pattern = r"^PES[0-9]UG[0-9]{2}[A-Z]{2}[0-9]{3}$"
    if not re.match(srn_pattern, srn):
        print("⚠  Invalid SRN format!")
        return
    
    name = input("Enter Name: ").strip()
    if not name.replace(" ", "").isalpha():
        print("⚠  Invalid Name! (Must be alphabetic)")
        return 
    
    email = input("Enter Email ID: ").strip()
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_pattern, email, re.IGNORECASE):
        print("⚠  Invalid Email! Expected format: example@domain.com")
        return
    
    phone = input("Enter Phone No: ").strip()
    if not(phone.isdigit() and len(phone) == 10):
        print("⚠  Phone number must be exactly 10 digits!")
        return

    try:
        cursor.execute("INSERT INTO tb_Student VALUES (%s, %s, %s, %s)", (srn, name, email, phone))
        conn.commit()
        print("✅  Student added successfully!")
    except mysql.connector.Error as err:
        print("⚠  Database Error:", err)
        conn.rollback()

def insert_faculty(conn, cursor):
    try:
        fid = int(input("Enter Faculty ID: "))
        
        name = input("Enter Faculty Name: ").strip()
        if not name.replace(" ", "").isalpha():
            print("⚠  Invalid Name! (Must be alphabetic)")
            return 

        email = input("Enter Email ID: ").strip()
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, email, re.IGNORECASE):
            print("⚠  Invalid Email! Expected format: example@domain.com")
            return

        cursor.execute("INSERT INTO tb_Faculty VALUES (%s, %s, %s)", (fid, name, email))
        conn.commit()
        print("✅  Faculty added successfully!")
    except (ValueError, mysql.connector.Error) as err:
        print("⚠  Error:", err)
        conn.rollback()

def insert_resource(conn, cursor):
    try:
        rid = int(input("Enter Resource ID: "))
        name = input("Enter Resource Name: ")
        rtype = input("Enter Type: ")
        location = input("Enter Location: ")
        did = int(input("Enter Department ID: "))
        # 3NF Schema
        cursor.execute("INSERT INTO tb_Resource (R_id, RName, Type, Location, D_id) VALUES (%s, %s, %s, %s, %s)",
                       (rid, name, rtype, location, did))
        conn.commit()
        print("✅  Resource added successfully!")
    except (ValueError, mysql.connector.Error) as err:
        print("⚠  Error:", err)
        conn.rollback()

def insert_booking(conn, cursor):
    try:
        cursor.execute("SELECT MAX(B_id) FROM tb_Booking")
        max_id = cursor.fetchone()[0]
        bid = (max_id or 300) + 1 

        now = datetime.datetime.now()
        bdate = now.strftime('%Y-%m-%d')
        btime = now.strftime('%H:%M:%S')

        status = "pending"

        srn = None  
        fid = None 

        while True:
            booker_type = input("Who is booking?\n1. Student\n2. Faculty\nEnter choice: ")
            if booker_type == '1':
                srn = input("Enter Student SRN: ")
                break
            elif booker_type == '2':
                fid = int(input("Enter Faculty ID: "))
                break
            else:
                print("⚠ Invalid choice, please enter 1 or 2.")
       
        purpose = input("Enter Purpose: ")
        from_t = input("Enter From Time (HH:MM): ") + ":00"
        to_t = input("Enter To Time (HH:MM): ") + ":00"
        rid = int(input("Enter Resource ID to book: "))

        
        # Stored Procedure
        cursor.callproc('sp_insert_booking', 
                       (bid, bdate, btime, purpose, status, from_t, to_t, srn, fid, rid))
        conn.commit()
      
        print(f"\n✅  Booking request submitted successfully!")
        print(f"   Your Booking ID is: {bid}")
        print(f"   Booked on (Date): {bdate}")
        print(f"   Booked at (Time): {btime}")
        print("\n(This booking is 'pending' until an admin approves it.)")

    except (ValueError, mysql.connector.Error) as err:
        print("⚠  Error:", err)
        conn.rollback()

def update_booking_status(conn, cursor):
    try:
        bid = int(input("Enter Booking ID: "))
        new_status = input("Enter new status (approved/pending/cancelled): ")
        if new_status not in ['approved', 'pending', 'cancelled']:
            print("⚠ Invalid status! Please choose 'approved', 'pending', or 'cancelled'.")
            return
            
        cursor.execute("UPDATE tb_Booking SET status = %s WHERE B_id = %s", (new_status, bid))
        conn.commit()
        print("✅  Booking status updated!")
    except (ValueError, mysql.connector.Error) as err:
        print("⚠  Error:", err)
        conn.rollback()

def delete_booking(conn, cursor):
    try:
        bid = int(input("Enter Booking ID to delete: "))
        cursor.execute("DELETE FROM tb_Booking WHERE B_id = %s", (bid,))
        conn.commit()
        print("✅  Booking deleted successfully!")
    except (ValueError, mysql.connector.Error) as err:
        print("⚠  Error:", err)
        conn.rollback()

def aggregate_approved_bookings(cursor):
    print("\n--- Approved Bookings per Department (Aggregate Query) ---")
    cursor.execute("""
        SELECT d.DName, COUNT(b.B_id) AS Approved_Bookings
        FROM tb_Booking b
        JOIN tb_Resource r ON b.R_id = r.R_id
        JOIN tb_Department d ON r.D_id = d.D_id
        WHERE b.status = 'approved'
        GROUP BY d.DName;
    """)
    for row in cursor.fetchall():
        print(f"Department: {row[0]}, Approved Bookings: {row[1]}")

def nested_query_students_all_departments(cursor):
    print("\n--- Students Who Booked Resources by Department (Nested Query) ---")
    dept_name = input("Enter Department Name (e.g., Computer Science): ").strip()

    query = """
        SELECT Name 
        FROM tb_Student 
        WHERE SRN IN (
            SELECT b.SRN 
            FROM tb_Booking b
            WHERE b.R_id IN (
                SELECT r.R_id 
                FROM tb_Resource r 
                JOIN tb_Department d ON r.D_id = d.D_id 
                WHERE d.DName = %s
            )
            AND b.SRN IS NOT NULL
        );
    """
    cursor.execute(query, (dept_name,))
    rows = cursor.fetchall()
    if rows:
        print(f"Students who booked in '{dept_name}':")
        for row in rows:
            print(f" - {row[0]}")
    else:
        print(f"No students found for department '{dept_name}'.")

# Function call
def show_booking_durations(cursor):
    print("\n--- Booking Durations (in hours) (Function Call) ---")
    try:
        cursor.execute("""
            SELECT b.B_id, b.Purpose, fn_booking_duration(b.From_time, b.To_time) AS Duration
            FROM tb_Booking b;
        """)
        for row in cursor.fetchall():
            print(f"BookingID: {row[0]}, Purpose: {row[1]}, Duration: {row[2]} hours")
    except mysql.connector.Error as err:
        print("⚠  Error:", err)


def admin_menu(conn, cursor):
    while True:
        print("\n========= ADMIN MENU =========")
        print("1. Insert Student")
        print("2. Insert Faculty")
        print("3. Insert Resource")
        print("4. Insert Booking")
        print("5. Update Booking Status")
        print("6. Delete Booking")
        print("7. List Students")
        print("8. List Faculty")
        print("9. List Departments")
        print("10. List Resources")
        print("11. List Bookings")
        print("12. Aggregate Query (Approved Bookings per Department)")
        print("13. Nested Query (Students by Department)")
        print("14. Show Booking Durations (SQL Function)")
        print("0. Logout")

        choice = input("\nEnter your choice: ")

        if choice == "1": insert_student(conn, cursor)
        elif choice == "2": insert_faculty(conn, cursor)
        elif choice == "3": insert_resource(conn, cursor)
        elif choice == "4": insert_booking(conn, cursor)
        elif choice == "5": update_booking_status(conn, cursor)
        elif choice == "6": delete_booking(conn, cursor)
        elif choice == "7": list_students(cursor)
        elif choice == "8": list_faculty(cursor)
        elif choice == "9": list_departments(cursor)
        elif choice == "10": list_resources(cursor)
        elif choice == "11": list_bookings(cursor)
        elif choice == "12": aggregate_approved_bookings(cursor)
        elif choice == "13": nested_query_students_all_departments(cursor)
        elif choice == "14": show_booking_durations(cursor)
        elif choice == "0":
            print("🛑  Logging out...")
            break
        else:
            print("🚫  Invalid choice! Try again")

def general_user_menu(conn, cursor):
    while True:
        print("\n========= GENERAL USER MENU =========")
        print("1. Insert Booking")
        print("2. List Resources")
        print("3. List Departments")
        print("4. List Bookings")
        print("5. Approved Bookings per Department (Aggregate Query)")
        print("6. Students by Department (Nested Query)")
        print("7. Show Booking Durations (SQL Function)")
        print("0. Logout")

        choice = input("\nEnter your choice: ")
        
        if choice == "1": insert_booking(conn, cursor)
        elif choice == "2": list_resources(cursor)
        elif choice == "3": list_departments(cursor)
        elif choice == "4": list_bookings(cursor)
        elif choice == "5": aggregate_approved_bookings(cursor)
        elif choice == "6": nested_query_students_all_departments(cursor)
        elif choice == "7": show_booking_durations(cursor)
        elif choice == "0":
            print("🛑  Logging out...")
            break
        else:
            print("🚫  Invalid choice! Try again")


def main():
    while True:
        print("\n========= PESU SMART CAMPUS RESOURCE BOOKING SYSTEM =========")
        print("1. Login as Admin")
        print("2. Login as General User")
        print("0. Exit System")
        login_choice = input("Enter your choice: ")

        if login_choice == "1":
            password = getpass.getpass("Enter Admin Password: ") 
            conn = get_db_connection('db_admin', password)
            if conn:
                print("✅  Admin login successful!")
                cursor = conn.cursor()
                admin_menu(conn, cursor)
                cursor.close()
                conn.close()

        elif login_choice == "2":
            password = getpass.getpass("Enter General User Password: ")
            conn = get_db_connection('general_user', password)
            if conn:
                print("✅  User login successful!")
                cursor = conn.cursor()
                general_user_menu(conn, cursor)
                cursor.close()
                conn.close()

        elif login_choice == "0":
            print("🛑  Exiting system...")
            break
        else:
            print("🚫  Invalid choice! Try again")

if __name__ == "__main__":
    main()
