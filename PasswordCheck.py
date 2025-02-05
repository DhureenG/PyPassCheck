from collections import deque
import re
import hashlib
import sqlite3
import string
from typing import List, Tuple

admin_username="admin"
admin_password="Today$$232028"

class PasswordDatabase:
    def __init__(self, db_name="passwords.db"):
        self.db_path = db_name  # Removed redundant path assignment
        self._initialize_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        return conn, conn.cursor()

    def _initialize_db(self):
        conn, cursor = self._get_connection()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password_hash TEXT UNIQUE
            )
        """)
        conn.commit()
        conn.close()

    def add_password(self, password: str) -> bool:
        conn, cursor = self._get_connection()
        password_hash = self.hash_password(password)
        try:
            cursor.execute("INSERT INTO passwords (password_hash) VALUES (?)", (password_hash,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def check_password_exists(self, password: str) -> bool:
        conn, cursor = self._get_connection()
        password_hash = self.hash_password(password)
        cursor.execute("SELECT COUNT(*) FROM passwords WHERE password_hash = ?", (password_hash,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def get_all_passwords(self) -> List[Tuple[int, str]]:
        conn, cursor = self._get_connection()
        cursor.execute("SELECT id, password_hash FROM passwords")
        data = cursor.fetchall()
        conn.close()
        return data


class PasswordChecker:
    def __init__(self, max_previous_passwords=3, db_name="passwords.db"):
        self.max_previous_passwords = max_previous_passwords
        self.password_history = deque(maxlen=max_previous_passwords)
        self.db = PasswordDatabase(db_name)  # Use the imported PasswordDatabase
        self.admin_username = "admin"
        self.admin_password = "Today$$232028"
        self._initialize_pattern_checks()

    def _initialize_pattern_checks(self):
        self.number_sequences = ["123", "234", "345", "456", "567", "678", "789", "890"]
        self.common_name_patterns = [
            r"(?:19|20)\d{2}",  # Matches years (e.g., 1999, 2023)
            r"password",        # Common weak password
            r"admin"            # Common username
        ]
        self.common_name_patterns = [re.compile(pattern) for pattern in self.common_name_patterns]

    def check_password_requirements(self, password: str) -> tuple:
        errors = []
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        if len(password) > 64:
            errors.append("Password must not exceed 64 characters")
        for sequence in self.number_sequences:
            if sequence in password:
                errors.append("Password contains simple number sequence")
                break
        if re.search(r'(.)\1{2,}', password):
            errors.append("Password contains too many repeated characters")
        for pattern in self.common_name_patterns:
            if re.search(pattern, password):
                errors.append("Password contains common pattern (year/special char placement)")
                break
        char_sets = [string.ascii_lowercase, string.ascii_uppercase, string.digits, string.punctuation]
        char_set_count = sum(1 for char_set in char_sets if any(char in password for char in char_set))
        if char_set_count < 3:
            errors.append("Password should use at least 3 different types of characters")
        if self.db.check_password_exists(password):
            errors.append("Password has been used before")
        return (len(errors) == 0, errors)

    def add_password(self, password: str):
        return self.db.add_password(password)

    def authenticate_terminal(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        if username == self.admin_username and password == self.admin_password:
            print("Access granted! Retrieving stored passwords...")
            return True
        else:
            print("Unauthorized access! Exiting...")
            exit(1)

    def show_stored_passwords(self):
        if self.authenticate_terminal():  # Ensure authentication before showing passwords
            print("\nStored Passwords (hashed):")
            print("----------------------------")
            stored_passwords = self.db.get_all_passwords()  # Fetch passwords from database
            for entry in stored_passwords:
                password_id, password_hash = entry  # Unpacking tuple values
                print(f"ID: {password_id}, Hash: {password_hash}")

    def calculate_password_strength(self, password: str) -> tuple:
        score = 0
        deductions = []
        if len(password) < 8:
            deductions.append("Could be longer (-1)")
        elif len(password) < 12:
            score += 1
        else:
            score += 2
        if re.search(r'(.)\1{2,}', password):
            deductions.append("Too many repeated characters (-1)")
        if len(set(password)) < 6:
            deductions.append("Too few unique characters (-1)")
        char_sets = [string.ascii_lowercase, string.ascii_uppercase, string.digits, string.punctuation]
        char_set_count = sum(1 for char_set in char_sets if any(char in password for char in char_set))
        if char_set_count < 3:
            deductions.append("Should use at least 3 different types of characters (-1)")
        elif char_set_count < 4:
            score += 1
        else:
            score += 2
        if self.db.check_password_exists(password):
            deductions.append("Password has been used before (-1)")
        strength = "Strong" if score >= 4 else "Weak"
        return (score, strength, deductions)

def main():
    checker = PasswordChecker()
    while True:
        print("\n" + "=" * 50)
        print("Password Strength Checker")
        print("=" * 50)
        print("1. Check password strength")
        print("2. View stored passwords")
        print("3. Exit")

        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            if choice == "1":
                password = input("\nEnter password to check: ")
                valid, errors = checker.check_password_requirements(password)
                score, strength, deductions = checker.calculate_password_strength(password)

                print("\nPassword Analysis:")
                print("-" * 20)
                print(f"Strength Score: {score}/10 ({strength})")

                if deductions:
                    print("\nAreas for improvement:")
                    for deduction in deductions:
                        print(f"• {deduction}")
                if not valid:
                    print("\nRequirement failures:")
                    for error in errors:
                        print(f"• {error}")

                store = input("\nWould you like to store this password? (y/n): ").lower()
                if store == 'y':
                    if checker.add_password(password):
                        print("Password stored successfully!")
                    else:
                        print("Password already exists in the database.")

            elif choice == "2":
                stored_passwords = checker.show_stored_passwords()

            elif choice == "3":
                print("\nGoodbye!")
                break
            else:
                print("\nInvalid choice. Please enter 1-3.")
        except KeyboardInterrupt:
            print("\n\nProgram terminated by user.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please try again.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

