from flask import Flask, redirect, url_for, session, request, render_template
import os
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import google.oauth2.id_token
from pymongo import MongoClient


MONGO_URI = "mongodb+srv://diary_user:pQhvvswaxHnv7zhd@cluster0.qn2r9me.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)

try:
    # เรียกดูชื่อ databases
    print("Databases:", client.list_database_names())
    print("MongoDB connected successfully ✅")
except Exception as e:
    print("MongoDB connection error ❌", e)
    
# ---------------------------
# Flask setup
# ---------------------------
app = Flask(__name__)
app.secret_key = "1234567890"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # HTTP สำหรับ localhost

# ---------------------------
# Google OAuth setup
# ---------------------------
GOOGLE_CLIENT_SECRETS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'client_secret.json'))
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
REDIRECT_URI = "http://localhost:5000/callback"

# ---------------------------
# MongoDB setup
# ---------------------------
MONGO_URI = "mongodb+srv://diary_user:pQhvvswaxHnv7zhd@cluster0.qn2r9me.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["diary_app"]            # database
users_collection = db["user"]       # collection สำหรับเก็บผู้ใช้
diary_collection = db["diary"]      # collection สำหรับเก็บโน้ตรายวัน
bouquet_collection = db["bouquet"]  # collection สำหรับเก็บช่อดอกไม้

# ---------------------------
# Routes
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/loginWeb')
def loginWeb():
    return render_template("login.html")

@app.route('/signup_success')
def signup_success():
    return render_template("signup_success.html")

@app.route('/mood')
def mood():
    return render_template("mood.html")

@app.route('/quiz')
def quiz():
    return render_template("quiz.html")

@app.route("/login")
def login():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(auth_url)

@app.route("/callback")
def callback():
    saved_state = session.get("state")
    if not saved_state:
        return "Session expired or invalid state", 400

    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=saved_state
    )

    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    request_session = google.auth.transport.requests.Request()
    
    # ✅ เพิ่ม clock_skew_in_seconds
    id_info = google.oauth2.id_token.verify_oauth2_token(
        credentials.id_token,
        request_session,
        clock_skew_in_seconds=60
    )


    # ดึงข้อมูลผู้ใช้
    email = id_info.get("email")
    name = id_info.get("name", "")

    # บันทึก MongoDB ถ้าไม่มีผู้ใช้นี้
    if not users_collection.find_one({"email": email}):
        users_collection.insert_one({
            "email": email,
            "name": name,
            "quiz_answers": [],
            "flower_personal": None,
            "daily_logs": []
        })

    return redirect(url_for('dashboard'))


@app.route("/dashboard")
def dashboard():
    # ดึงผู้ใช้ตัวอย่างทั้งหมด
    users = list(users_collection.find())
    return render_template("home.html", users=users)

# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="localhost", port=5000)



