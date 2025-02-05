from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PasswordCheck import PasswordChecker, PasswordDatabase

app = Flask(__name__)
CORS(app)

checker = PasswordChecker()  # This now includes database functionality

#AdminCredentials
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="Today$$232028"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/check_password", methods=["POST"])
def check_password():
    data = request.json
    password = data.get("password", "")
    
    valid, errors = checker.check_password_requirements(password)
    score, strength, deductions = checker.calculate_password_strength(password)
    
    return jsonify({
        "valid": valid,
        "errors": errors,
        "score": score,
        "strength": strength,
        "deductions": deductions
    })

@app.route("/get_passwords", methods=["POST"])
def get_passwords():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        return jsonify({"message": "Unauthorized access"}), 401
    stored_passwords = checker.db.get_all_passwords()  # Fetch stored passwords from DB
    formatted_passwords = [{"id": entry[0], "hash": entry[1]} for entry in stored_passwords]
    return jsonify(formatted_passwords)

@app.route("/store_password", methods=["POST"])
def store_password():
    data = request.json
    password = data.get("password", "")

    if not password:
        return jsonify({"message": "Password cannot be empty"}), 400

    success = checker.db.add_password(password)  

    if success:
        return jsonify({"message": "Password stored successfully"})
    else:
        return jsonify({"message": "Password already exists"}), 409  # Handle duplicates properly

if __name__ == "__main__":
    app.run(debug=True, port=5000)