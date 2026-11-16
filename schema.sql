CREATE DATABASE waste_management_system;
USE waste_management_system;

CREATE TABLE Zone (
    zone_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    area VARCHAR(100)
);

CREATE TABLE Bin (
    bin_id INT AUTO_INCREMENT PRIMARY KEY,
    zone_id INT NOT NULL,
    location VARCHAR(150) NOT NULL,
    capacity_kg INT DEFAULT 100,
    current_fill_level INT DEFAULT 0,
    last_collected_date DATETIME,
    FOREIGN KEY (zone_id) REFERENCES Zone(zone_id)
);

CREATE TABLE Vehicle (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    number_plate VARCHAR(20) NOT NULL,
    capacity_kg INT DEFAULT 500,
    status ENUM('Available','On Route','Under Maintenance') DEFAULT 'Available'
);

CREATE TABLE Staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    role VARCHAR(50) DEFAULT 'Collector'
);

CREATE TABLE CollectionSchedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    staff_id INT NOT NULL,
    zone_id INT NOT NULL,
    scheduled_date DATE NOT NULL,
    status ENUM('Pending','In Progress','Completed') DEFAULT 'Pending',
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id),
    FOREIGN KEY (staff_id) REFERENCES Staff(staff_id),
    FOREIGN KEY (zone_id) REFERENCES Zone(zone_id)
);

CREATE TABLE Complaint (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    bin_id INT NOT NULL,
    citizen_name VARCHAR(100),
    phone VARCHAR(15),
    issue_description TEXT,
    status ENUM('Reported','In Progress','Resolved') DEFAULT 'Reported',
    date_reported DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bin_id) REFERENCES Bin(bin_id)
);