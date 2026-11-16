from flask import Flask, request, jsonify
from db_config import get_connection
from flask_cors import CORS
from flask import send_from_directory

app = Flask(__name__)
CORS(app)

# --- Register a bin ---
@app.route('/api/bins', methods=['POST'])
def add_bin():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Bin (zone_id, location, capacity_kg, current_fill_level)
        VALUES (%s, %s, %s, %s)
    """, (data['zone_id'], data['location'], data.get('capacity_kg', 100), data.get('current_fill_level', 0)))
    conn.commit()
    bin_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"message": "Bin added", "bin_id": bin_id}), 201


# --- List all bins ---
@app.route('/api/bins', methods=['GET'])
def get_bins():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.*, z.name AS zone_name FROM Bin b
        JOIN Zone z ON b.zone_id = z.zone_id
    """)
    bins = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(bins)


# --- Update bin fill level (simulates a sensor reading / citizen report) ---
@app.route('/api/bins/<int:bin_id>/fill', methods=['PUT'])
def update_fill_level(bin_id):
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Bin SET current_fill_level=%s WHERE bin_id=%s",
                   (data['current_fill_level'], bin_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Fill level updated"})


# --- Get bins needing urgent collection (the "smart" logic) ---
@app.route('/api/bins/urgent', methods=['GET'])
def get_urgent_bins():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.bin_id, b.location, b.current_fill_level, z.name AS zone_name
        FROM Bin b
        JOIN Zone z ON b.zone_id = z.zone_id
        WHERE b.current_fill_level >= 80
        ORDER BY b.current_fill_level DESC
    """)
    urgent = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(urgent)


# --- Register a zone ---
@app.route('/api/zones', methods=['POST'])
def add_zone():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Zone (name, area) VALUES (%s, %s)",
                   (data['name'], data.get('area')))
    conn.commit()
    zone_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"message": "Zone added", "zone_id": zone_id}), 201


# --- List all zones ---
@app.route('/api/zones', methods=['GET'])
def get_zones():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Zone")
    zones = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(zones)


# --- File a complaint about a bin ---
@app.route('/api/complaints', methods=['POST'])
def add_complaint():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Complaint (bin_id, citizen_name, phone, issue_description)
        VALUES (%s, %s, %s, %s)
    """, (data['bin_id'], data.get('citizen_name'), data.get('phone'), data['issue_description']))
    conn.commit()
    complaint_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"message": "Complaint filed", "complaint_id": complaint_id}), 201


# --- Schedule a collection ---
@app.route('/api/schedules', methods=['POST'])
def add_schedule():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO CollectionSchedule (vehicle_id, staff_id, zone_id, scheduled_date)
        VALUES (%s, %s, %s, %s)
    """, (data['vehicle_id'], data['staff_id'], data['zone_id'], data['scheduled_date']))
    conn.commit()
    schedule_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"message": "Collection scheduled", "schedule_id": schedule_id}), 201


# --- Mark schedule completed (resets bin fill level to 0) ---
@app.route('/api/schedules/<int:schedule_id>/complete', methods=['PUT'])
def complete_schedule(schedule_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE CollectionSchedule SET status='Completed' WHERE schedule_id=%s", (schedule_id,))
    cursor.execute("""
        UPDATE Bin SET current_fill_level=0, last_collected_date=NOW()
        WHERE zone_id = (SELECT zone_id FROM CollectionSchedule WHERE schedule_id=%s)
    """, (schedule_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Schedule marked completed, bins reset"})

# --- Register a staff member ---
@app.route('/api/staff', methods=['POST'])
def add_staff():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Staff (name, phone, role) VALUES (%s, %s, %s)",
                   (data['name'], data.get('phone'), data.get('role', 'Collector')))
    conn.commit()
    staff_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"message": "Staff added", "staff_id": staff_id}), 201


@app.route('/api/staff', methods=['GET'])
def get_staff():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Staff")
    staff = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(staff)


# --- Register a vehicle ---
@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Vehicle (number_plate, capacity_kg) VALUES (%s, %s)",
                   (data['number_plate'], data.get('capacity_kg', 500)))
    conn.commit()
    vehicle_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"message": "Vehicle added", "vehicle_id": vehicle_id}), 201


@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Vehicle")
    vehicles = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(vehicles)


# --- List all complaints ---
@app.route('/api/complaints', methods=['GET'])
def get_complaints():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.*, b.location FROM Complaint c
        JOIN Bin b ON c.bin_id = b.bin_id
        ORDER BY c.date_reported DESC
    """)
    complaints = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(complaints)


# --- List all schedules ---
@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.*, z.name AS zone_name, v.number_plate, st.name AS staff_name
        FROM CollectionSchedule s
        JOIN Zone z ON s.zone_id = z.zone_id
        JOIN Vehicle v ON s.vehicle_id = v.vehicle_id
        JOIN Staff st ON s.staff_id = st.staff_id
        ORDER BY s.scheduled_date DESC
    """)
    schedules = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(schedules)


@app.route('/')
def serve_login():
    return send_from_directory('.', 'login.html')

@app.route('/app.html')
def serve_app():
    return send_from_directory('.', 'app.html')

if __name__ == '__main__':
    app.run(debug=True)