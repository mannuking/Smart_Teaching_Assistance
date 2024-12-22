import bcrypt

def hash_password(password):
  """Hashes a password using bcrypt."""
  hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
  return hashed.decode('utf-8')  # Decode to store as string in YAML

# Get hashed passwords for your users
print("Hashed Passwords:")
print(f"  john_doe: {hash_password('password123')}")  # Replace 'password123' with the actual password
print(f"  jane_smith: {hash_password('securepassword')}")  # Replace 'securepassword' with the actual password
