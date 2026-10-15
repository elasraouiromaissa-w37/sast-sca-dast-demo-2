import os
import secrets
import subprocess

from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

# Secret lu dans l'environnement (valeur aléatoire si absent)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

# Liste blanche de commandes autorisées
ALLOWED_COMMANDS = {
    "date": ["date"],
    "uptime": ["uptime"],
    "whoami": ["whoami"],
}


@app.after_request
def security_headers(resp):
    resp.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'; form-action 'self'; base-uri 'self'"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Server"] = "webserver"
    return resp


@app.route('/')
def index():
    return """
    <h1>Welcome to our secured Flask App</h1>
    <p>Explore the different pages:</p>
    <ul>
        <li><a href="/hello?name=World">Hello Page</a></li>
        <li><a href="/execute?cmd=date">Execute Command Page (date, uptime, whoami)</a></li>
    </ul>
    """


@app.route('/hello')
def hello():
    name = request.args.get('name', 'Guest')
    return f"""
    <h1>Hello Page</h1>
    <p>Hello, {escape(name)}!</p>
    <p><a href="/">Back to Homepage</a></p>
    """


@app.route('/execute')
def execute():
    key = request.args.get('cmd', 'date')
    if key not in ALLOWED_COMMANDS:
        return "Command not allowed", 400
    result = subprocess.run(ALLOWED_COMMANDS[key], capture_output=True, text=True)
    return f"""
    <h1>Execute Command Page</h1>
    <p>Executing command: <code>{escape(key)}</code></p>
    <pre>{escape(result.stdout)}</pre>
    <p><a href="/">Back to Homepage</a></p>
    """


if __name__ == '__main__':
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", host='0.0.0.0')
