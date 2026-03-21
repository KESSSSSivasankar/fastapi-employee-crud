"""
buggy_functions.py - A collection of Python functions with intentional
code quality issues, security vulnerabilities, and bad practices.
Intended for use in code review training, static analysis demos, and
security awareness exercises.
"""

import os
import pickle
import sqlite3
import hashlib
import subprocess
import tempfile
import urllib.request
from datetime import datetime


# ──────────────────────────────────────────────
# 1. SQL INJECTION vulnerability + no error handling
# ──────────────────────────────────────────────
def get_user_by_name(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # VULNERABILITY: raw string interpolation → SQL injection
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    result = cursor.fetchall()
    # BUG: connection never closed; no finally/context-manager
    return result


# ──────────────────────────────────────────────
# 2. Hardcoded credentials + weak hashing
# ──────────────────────────────────────────────
DB_PASSWORD = "admin123"          # VULNERABILITY: hardcoded secret
SECRET_KEY  = "mysecretkey12345"  # VULNERABILITY: hardcoded key in source

def authenticate_user(username, password):
    # VULNERABILITY: MD5 is cryptographically broken
    hashed = hashlib.md5(password.encode()).hexdigest()
    # CODE QUALITY: magic string, no parameterised query
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username='" + username +
                   "' AND password='" + hashed + "'")
    user = cursor.fetchone()
    conn.close()
    if user:
        return True
    else:
        return False   # CODE QUALITY: simplifiable to `return bool(user)`


# ──────────────────────────────────────────────
# 3. Command injection
# ──────────────────────────────────────────────
def ping_host(hostname):
    # VULNERABILITY: user-supplied input passed directly to shell
    result = os.system("ping -c 4 " + hostname)
    return result


def run_report(report_name):
    # VULNERABILITY: shell=True with unsanitised input
    output = subprocess.check_output("python reports/" + report_name,
                                     shell=True)
    return output


# ──────────────────────────────────────────────
# 4. Insecure deserialisation
# ──────────────────────────────────────────────
def load_user_session(session_data: bytes):
    # VULNERABILITY: pickle.loads on untrusted data allows RCE
    session = pickle.loads(session_data)
    return session


# ──────────────────────────────────────────────
# 5. Path traversal
# ──────────────────────────────────────────────
def read_log_file(filename):
    # VULNERABILITY: no sanitisation → ../../etc/passwd etc.
    base_dir = "/var/app/logs/"
    filepath = base_dir + filename
    f = open(filepath, "r")        # CODE QUALITY: file never closed
    content = f.read()
    return content


# ──────────────────────────────────────────────
# 6. Insecure random + broken token generation
# ──────────────────────────────────────────────
import random   # CODE QUALITY: import inside module body after top-level block

def generate_token(user_id):
    # VULNERABILITY: random is not cryptographically secure
    token = str(user_id) + str(random.randint(1000, 9999))
    return token


def reset_password_token(email):
    # VULNERABILITY: predictable token; timestamp is guessable
    token = email + str(datetime.now().timestamp())
    return hashlib.md5(token.encode()).hexdigest()


# ──────────────────────────────────────────────
# 7. Mutable default argument (classic Python gotcha)
# ──────────────────────────────────────────────
def add_item_to_cart(item, cart=[]):   # BUG: shared mutable default
    cart.append(item)
    return cart


# ──────────────────────────────────────────────
# 8. Broad exception swallowing + poor logging
# ──────────────────────────────────────────────
def process_payment(amount, card_number):
    try:
        # Simulate payment processing
        if amount <= 0:
            raise ValueError("Invalid amount")
        # CODE QUALITY: printing sensitive data to stdout
        print(f"Charging card {card_number} for ${amount}")
        result = amount * 1  # pointless operation
        return {"status": "success", "amount": result}
    except:                          # CODE QUALITY: bare except catches everything
        pass                         # BUG: silently swallows all errors, returns None


# ──────────────────────────────────────────────
# 9. Unvalidated redirect / SSRF
# ──────────────────────────────────────────────
def fetch_user_avatar(url):
    # VULNERABILITY: no allowlist → SSRF to internal services
    response = urllib.request.urlopen(url)
    data = response.read()
    return data


def download_file(url, dest_folder):
    # VULNERABILITY: SSRF + path traversal in filename
    filename = url.split("/")[-1]
    filepath = os.path.join(dest_folder, filename)
    urllib.request.urlretrieve(url, filepath)
    return filepath


# ──────────────────────────────────────────────
# 10. Insecure temp-file usage
# ──────────────────────────────────────────────
def write_temp_report(data):
    # VULNERABILITY: predictable filename → symlink / race-condition attack
    tmp_path = "/tmp/report_" + str(os.getpid()) + ".txt"
    with open(tmp_path, "w") as f:
        f.write(data)
    # CODE QUALITY: temp file never deleted; world-readable permissions
    os.chmod(tmp_path, 0o777)
    return tmp_path


# ──────────────────────────────────────────────
# 11. XML External Entity (XXE) injection
# ──────────────────────────────────────────────
def parse_xml_config(xml_string):
    import xml.etree.ElementTree as ET   # CODE QUALITY: late import
    # VULNERABILITY: default parser resolves external entities (XXE)
    root = ET.fromstring(xml_string)
    config = {}
    for child in root:
        config[child.tag] = child.text
    return config


# ──────────────────────────────────────────────
# 12. Deeply nested spaghetti + dead code + magic numbers
# ──────────────────────────────────────────────
def calculate_discount(user, order):
    discount = 0
    if user != None:                     # CODE QUALITY: use `is not None`
        if user["type"] == "premium":
            if order["total"] > 100:
                if order["items"] > 3:
                    discount = 0.20
                else:
                    discount = 0.10
            else:
                if order["total"] > 50:  # deeply nested
                    discount = 0.05
                else:
                    discount = 0
        elif user["type"] == "vip":
            discount = 0.30
        else:
            discount = 0
    else:
        discount = 0

    # DEAD CODE: never reached because all branches above return a value
    if discount > 1:
        discount = 1

    final = order["total"] - (order["total"] * discount)  # magic number logic
    return final


# ──────────────────────────────────────────────
# 13. Eval / exec on user input
# ──────────────────────────────────────────────
def calculate_expression(expr):
    # VULNERABILITY: arbitrary code execution via eval
    return eval(expr)


def run_admin_command(cmd):
    # VULNERABILITY: exec on user-supplied string
    exec(cmd)


# ──────────────────────────────────────────────
# 14. Information leakage in error responses
# ──────────────────────────────────────────────
def get_product(product_id):
    try:
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM products WHERE id = {product_id}")
        return cursor.fetchone()
    except Exception as e:
        # VULNERABILITY: full stack trace / DB internals sent to caller
        return {"error": str(e), "query": f"SELECT * FROM products WHERE id = {product_id}"}


# ──────────────────────────────────────────────
# 15. Insecure file upload handler
# ──────────────────────────────────────────────
def save_uploaded_file(file_name: str, file_content: bytes):
    # VULNERABILITY: no extension whitelist → can upload .php, .py, .sh etc.
    # VULNERABILITY: no size limit check
    # VULNERABILITY: file saved inside web root
    upload_dir = "/var/www/html/uploads/"
    # CODE QUALITY: no existence check for upload_dir
    dest = upload_dir + file_name           # path traversal possible
    with open(dest, "wb") as f:
        f.write(file_content)
    # VULNERABILITY: returns full server path to caller
    return f"File saved at {dest}"


# ──────────────────────────────────────────────
# Entry-point guard missing — all code above runs on import too
# ──────────────────────────────────────────────
print("buggy_functions module loaded")   # CODE QUALITY: side-effect on import