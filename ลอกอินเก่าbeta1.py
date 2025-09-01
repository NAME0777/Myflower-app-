from flask import Flask, redirect, url_for, session, request, render_template
import os
import pathlib
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import google.oauth2.id_token

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # เปลี่ยนเป็นอะไรก็ได้

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # ใช้ HTTP ได้สำหรับ localhost

import os
GOOGLE_CLIENT_SECRETS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'client_secret.json'))
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email"]
REDIRECT_URI = "http://localhost:5000/callback"

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
    state = session["state"]
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    request_session = google.auth.transport.requests.Request()
    id_info = google.oauth2.id_token.verify_oauth2_token(
        credentials.id_token, request_session
    )

    email = id_info.get("email")
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)