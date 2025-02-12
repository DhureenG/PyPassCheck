# 🔐 Password Strength Checker

A web-based password strength checker with a backend for evaluating password security and storing encrypted passwords.

## 🚀 Features
- **Real-time password strength evaluation** based on common security criteria
- **Password visibility toggle** for better user experience
- **Secure password storage and retrieval** using hashing
- **Interactive UI** for checking and storing passwords

## 📂 Project Structure
```
├── index.html           # Frontend UI
├── app.py              # Backend API server (Flask)
├── PasswordCheck.py    # Password validation logic
```

## 🛠️ Installation

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/yourusername/password-checker.git
cd password-checker
```

### 2️⃣ Install Dependencies
Ensure you have Python installed. Then run:
```sh
pip install -r requirements.txt
```

### 3️⃣ Run the Server
```sh
python app.py
```

### 4️⃣ Open in Browser
Visit: `http://127.0.0.1:5000/`

## 📜 API Endpoints
| Method | Endpoint          | Description |
|--------|------------------|-------------|
| POST   | `/check_password` | Checks password strength |
| POST   | `/store_password` | Stores hashed password |
| POST   | `/get_passwords`  | Retrieves stored passwords |

## 📸 Preview
![Screenshot](screenshot.png)

## 🔒 Security Best Practices
- Do **not** store plaintext passwords
- Always hash passwords before storing
- Use HTTPS in production

## 🤝 Contributing
Pull requests are welcome! Please follow best coding practices.

## 📜 License
This project is licensed under the MIT License.

---



