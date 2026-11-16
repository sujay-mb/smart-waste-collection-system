# Smart Waste Collection Management System

A web-based system to manage waste collection, built as a DBMS mini project.

## Features
- User login system
- [schedule pickups, manage collection areas, track collection status]
- [Admin/user dashboards, if any]

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python (Flask)
- **Database:** MySQL

## Project Structure
- `app.py` – backend server
- `db_config.example.py` – database settings template
- `schema.sql` – database tables
- `app.html`, `login.html`, `static/` – frontend

## How to Run
1. Install requirements: `pip install flask mysql-connector-python`
2. Create the database: open MySQL and run `schema.sql`
3. Copy `db_config.example.py` to `db_config.py` and enter your MySQL username and password
4. Run the app: `python app.py`
5. Open `http://localhost:5000` in your browser

## Screenshots
(Add screenshots here)

## Author
Sujay M B – CSE, BGS Institute of Technology