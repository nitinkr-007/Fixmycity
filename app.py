from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "fixmycity_secret_key"   # Needed for sessions

DB_NAME = "complaints.db"
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------- Database ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS complaints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    coords TEXT,
                    state TEXT,
                    city TEXT,
                    address TEXT,
                    pincode TEXT,
                    description TEXT,
                    image_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Simple login check (use ADMIN as password)
        if password == "MIET":
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")

@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, coords, state, city, address, pincode, description, image_path, created_at FROM complaints ORDER BY created_at DESC")
    complaints = c.fetchall()
    conn.close()
    return render_template("gallery.html", complaints=complaints)

@app.route("/new")
def new_complaint():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit_complaint():
    if "user" not in session:
        return redirect(url_for("login"))

    name = request.form["name"]
    coords = request.form["coords"]
    state = request.form["state"]
    city = request.form["city"]
    address = request.form["address"]
    pincode = request.form["pincode"]
    description = request.form["description"]

    image_file = request.files["image"]
    image_path = None
    if image_file and image_file.filename != "":
        filename = secure_filename(image_file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image_file.save(file_path)
        image_path = f"uploads/{filename}"

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""INSERT INTO complaints 
                 (name, coords, state, city, address, pincode, description, image_path) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
              (name, coords, state, city, address, pincode, description, image_path))
    conn.commit()
    conn.close()

    return redirect(url_for("home", success=1))

@app.route("/delete/<int:complaint_id>", methods=["POST"])
def delete_complaint(complaint_id):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM complaints WHERE id=?", (complaint_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------- Run ----------
if __name__ == "__main__":  
    app.run(debug=True)