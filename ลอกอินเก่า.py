from flask import Flask, redirect, url_for, session, request, render_template, abort
import os
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import google.oauth2.id_token

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # คงที่ ไม่เปลี่ยนทุกครั้ง

# ใช้ HTTP บน localhost
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# กำหนดพฤติกรรม cookie ให้ชัดเจนสำหรับโลคัล
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
)

GOOGLE_CLIENT_SECRETS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'client_secret.json'))
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email"]
REDIRECT_URI = "http://localhost:5000/callback"  # ต้องตรงกับที่ขึ้นทะเบียนใน Google Cloud

@app.route("/")
def ipydex():
    return render_template("index.html")

@app.route("/login")
def login():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url()
    session["state"] = state  # เก็บ state ใน session (ฝั่งเบราว์เซอร์)
    return redirect(auth_url)

@app.route("/callback")
def callback():
    # 1) มี session state ไหม
    saved_state = session.get("state")
    if not saved_state:
        return "Session expired or invalid state (no session state)", 400

    # 2) state ที่ Google ส่งกลับมาตรงกันไหม
    returned_state = request.args.get("state")
    if not returned_state or returned_state != saved_state:
        return "Session expired or invalid state (state mismatch)", 400

    # 3) แลก token
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=saved_state
    )
    flow.fetch_token(authorization_response=request.url)

    # 4) ตรวจสอบ id_token และดึงข้อมูล
    credentials = flow.credentials
    request_session = google.auth.transport.requests.Request()
    id_info = google.oauth2.id_token.verify_oauth2_token(
        credentials.id_token, request_session
    )

    # 5) เก็บข้อมูลผู้ใช้ลง session (ทดสอบว่า session ใช้ได้)
    session["user_email"] = id_info.get("email")

    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    # ตัวอย่างการเช็คว่า session รอดไหม
    user_email = session.get("user_email")
    if not user_email:
        # ยังไม่ล็อกอิน (หรือ session หลุด)
        return redirect(url_for("index"))
    return render_template("index.html", email=user_email)

if __name__ == "__main__":
    app.run(debug=True)
