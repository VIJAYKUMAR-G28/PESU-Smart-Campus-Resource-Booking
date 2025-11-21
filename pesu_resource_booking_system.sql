DROP DATABASE IF EXISTS pesu_resource_booking_system;

CREATE DATABASE pesu_resource_booking_system;

USE pesu_resource_booking_system;



DROP USER IF EXISTS 'db_admin'@'localhost';

DROP USER IF EXISTS 'general_user'@'localhost';

FLUSH PRIVILEGES;



CREATE USER 'db_admin'@'localhost' IDENTIFIED BY 'admin_password';

GRANT ALL PRIVILEGES ON pesu_resource_booking_system.* TO 'db_admin'@'localhost';



CREATE USER 'general_user'@'localhost' IDENTIFIED BY 'user_password';

GRANT SELECT ON pesu_resource_booking_system.* TO 'general_user'@'localhost';

GRANT INSERT, UPDATE ON pesu_resource_booking_system.tb_Booking TO 'general_user'@'localhost';

GRANT EXECUTE ON PROCEDURE pesu_resource_booking_system.sp_insert_booking TO 'general_user'@'localhost';

GRANT EXECUTE ON FUNCTION pesu_resource_booking_system.fn_booking_duration TO 'general_user'@'localhost';

FLUSH PRIVILEGES;



CREATE TABLE tb_Student (

    SRN VARCHAR(20) PRIMARY KEY,

    Name VARCHAR(100) NOT NULL,

    Email_id VARCHAR(100) UNIQUE NOT NULL,

    P_No VARCHAR(15) NOT NULL,

    CONSTRAINT chk_email CHECK (Email_id LIKE '%@%.%')

);



CREATE TABLE tb_Faculty (

    Fid INT PRIMARY KEY,

    FName VARCHAR(100) NOT NULL,

    Email_id VARCHAR(100) UNIQUE NOT NULL,

    CONSTRAINT chk_email_faculty CHECK (Email_id LIKE '%@%.%')

);



CREATE TABLE tb_Department (

    D_id INT PRIMARY KEY,

    DName VARCHAR(100) NOT NULL UNIQUE,

    HOD_Name VARCHAR(100) NOT NULL

);



CREATE TABLE tb_Resource (

    R_id INT PRIMARY KEY,

    RName VARCHAR(100) NOT NULL,

    Type VARCHAR(50) NOT NULL,

    Location VARCHAR(100) NOT NULL,

    Availability BOOLEAN DEFAULT TRUE,

    D_id INT NOT NULL,

    CONSTRAINT fk_resource_dept FOREIGN KEY (D_id) REFERENCES tb_Department(D_id) ON DELETE CASCADE ON UPDATE CASCADE

);



CREATE TABLE tb_Booking (

    B_id INT PRIMARY KEY,

    B_date DATE NOT NULL,

    B_Time TIME NOT NULL,

    Purpose VARCHAR(255) NOT NULL,

    status VARCHAR(50) DEFAULT 'pending',

    From_time TIME NOT NULL,

    To_time TIME NOT NULL,

    SRN VARCHAR(20) NULL,

    Fid INT NULL,

    R_id INT NOT NULL,

    CONSTRAINT fk_booking_student FOREIGN KEY (SRN) REFERENCES tb_Student(SRN) ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_booking_faculty FOREIGN KEY (Fid) REFERENCES tb_Faculty(Fid) ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_booking_resource FOREIGN KEY (R_id) REFERENCES tb_Resource(R_id) ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT chk_time CHECK (From_time < To_time)

);



INSERT INTO tb_Student VALUES

('PES2UG23CS687', 'Vijay Kumar G', 'pes2ug23cs687@pesu.pes.edu', '9876543210'),

('PES2UG23CS656', 'Trigun Gurumurti Tamragouri', 'pes2ug23cs656@pesu.pes.edu', '9876543123'),

('PES2UG23CS555', 'Ananya Singh', 'pes2ug23cs555@pesu.pes.edu', '9876543212'),

('PES2UG23CS556', 'Rahul Verma', 'pes2ug23cs556@pesu.pes.edu', '9876543213'),

('PES2UG23CS557', 'Sneha Patel', 'pes2ug23cs557@pesu.pes.edu', '9876543214');



INSERT INTO tb_Faculty VALUES

(1, 'Dr. Nivedita Kasturi', 'niveditakasturi@gmail.com'),

(2, 'Dr. Monika Goyal', 'monikagoyal@gmail.com'),

(3, 'Dr. Farida Begum', 'faridabegum@gmail.com'),

(4, 'Dr. RaviKumar', 'ravikumar@gmail.com'),

(5, 'Dr. Kundavai', 'kundavai@gmail.com');



INSERT INTO tb_Department VALUES

(101, 'Computer Science', 'Dr. Sandesh'),

(102, 'Electronics', 'Dr. Subhash Kulkarni'),

(103, 'AIML', 'Dr. Arti Arya');



INSERT INTO tb_Resource VALUES

(201, 'Seminar Hall 1', 'Hall', 'Hall 101', TRUE, 101),

(202, 'Computer Lab 1', 'Computer', 'Lab 201', TRUE, 101),

(203, 'MRD', 'Auditorium', 'MRD 1', TRUE, 102),

(204, 'Seminar Hall 2', 'Hall', 'Hall 401', TRUE, 102),

(205, 'Quadrangle', 'Assembly', 'Open court 1', TRUE, 103);



INSERT INTO tb_Booking (B_id, B_date, B_Time, Purpose, status, From_time, To_time, SRN, Fid, R_id) VALUES

(301, '2025-09-10', '09:00:00', 'Project Presentation', 'approved', '09:00:00', '11:00:00', 'PES2UG23CS687', NULL, 201),

(302, '2025-09-11', '13:00:00', 'Lab Work', 'pending', '13:00:00', '15:00:00', 'PES2UG23CS656', NULL, 202),

(303, '2025-09-12', '10:00:00', 'Guest Speech', 'approved', '10:00:00', '12:00:00', NULL, 3, 203),

(304, '2025-09-13', '14:00:00', 'Audition', 'pending', '14:00:00', '16:00:00', NULL, 4, 204),

(305, '2025-09-14', '11:00:00', 'Dance', 'approved', '11:00:00', '13:00:00', 'PES2UG23CS557', NULL, 205);



DELIMITER $$

CREATE PROCEDURE sp_insert_booking(

    IN p_B_id INT, IN p_B_date DATE, IN p_B_Time TIME, IN p_Purpose VARCHAR(255),

    IN p_status VARCHAR(50), IN p_From_time TIME, IN p_To_time TIME,

    IN p_SRN VARCHAR(20), IN p_Fid INT, IN p_R_id INT

)

BEGIN

    INSERT INTO tb_Booking (B_id, B_date, B_Time, Purpose, status, From_time, To_time, SRN, Fid, R_id)

    VALUES (p_B_id, p_B_date, p_B_Time, p_Purpose, p_status, p_From_time, p_To_time, p_SRN, p_Fid, p_R_id);

END$$

DELIMITER ;



DELIMITER $$

CREATE TRIGGER trg_after_booking_insert

AFTER INSERT ON tb_Booking

FOR EACH ROW

BEGIN

    UPDATE tb_Resource SET Availability = FALSE WHERE R_id = NEW.R_id;

END$$

DELIMITER ;



DELIMITER $$

CREATE TRIGGER trg_before_booking_insert

BEFORE INSERT ON tb_Booking

FOR EACH ROW

BEGIN

    IF (NEW.SRN IS NULL AND NEW.Fid IS NULL) THEN

        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Booking must be made by either a Student (SRN) or a Faculty (Fid).';

    END IF;

    IF (NEW.SRN IS NOT NULL AND NEW.Fid IS NOT NULL) THEN

        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Booking cannot be made by both a Student (SRN) and a Faculty (Fid).';

    END IF;

END$$

DELIMITER ;



DELIMITER $$

CREATE FUNCTION fn_booking_duration(p_From TIME, p_To TIME)

RETURNS DECIMAL(5,2)

DETERMINISTIC

BEGIN

    DECLARE duration DECIMAL(5,2);

    SET duration = TIME_TO_SEC(TIMEDIFF(p_To, p_From)) / 3600;

    RETURN duration;

END$$

DELIMITER ;
