from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Simulated users database (replace with your real DB)
users_db = {
    "student123": {
        "password_hash": generate_password_hash("password123"),
        "blocked": False
    },
    "student_blocked": {
        "password_hash": generate_password_hash("password456"),
        "blocked": True
    }
}


# Login route (Login API)
@app.route('/login', methods=['POST'])
def login():
    # read the json file and extract id and password
    data = request.get_json()
    student_id = data.get('student_id')
    password = data.get('password')

    # Logic for incorrect user, password, exhausted and active student
    user = users_db.get(student_id)
    if not user:
        return jsonify({"success": False, "message": "Invalid ID or password"}), 401

    if user["blocked"]:
        return jsonify({"success": False, "message": "Account blocked. Monthly data cap exceeded."}), 403

    if not check_password_hash(user['password_hash'], password):
        return jsonify({"success": False, "message": "Invalid ID or password"}), 401

    # If using sessions or JWT, generate token here
    return jsonify({"success": True, "message": "Login successful!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
