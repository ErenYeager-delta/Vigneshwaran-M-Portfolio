"""
🔑 Admin Password Hashing CLI Tool
Purpose:
  Command-line utility to generate a secure scrypt hash of a password.
Connections:
  - .env: The generated hash is copied and pasted as ADMIN_PASSWORD configuration.
  - app/admin/auth.py: Compares submitted administrator password inputs against this secure hash string.
"""
import sys
from werkzeug.security import generate_password_hash

def main():
    """CLI utility to generate a secure scrypt hash of a password."""
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        # Prompt securely
        import getpass
        password = getpass.getpass("Enter password to hash: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("❌ Error: Passwords do not match!")
            sys.exit(1)
            
    if not password:
        print("❌ Error: Password cannot be empty!")
        sys.exit(1)
        
    hashed = generate_password_hash(password, method="scrypt")
    print("\nGenerated secure password hash:")
    print("-" * 60)
    print(hashed)
    print("-" * 60)
    print("Copy the entire hash string above and paste it into your .env file as:")
    print("ADMIN_PASSWORD=your_hash_here\n")

if __name__ == "__main__":
    main()
