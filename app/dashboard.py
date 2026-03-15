from flask import Flask, render_template_string, request, redirect, url_for
import json
import os
import subprocess

app = Flask(__name__)

# Helper to find files in the new AutoSANP structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "data", "autosanp_logs.json")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AutoSANP Proactive Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0b0f19; color: white; padding: 20px; }
        .container { max-width: 900px; margin: auto; }
        .button-group { display: flex; gap: 10px; justify-content: center; margin-bottom: 30px; }
        button { padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; transition: 0.3s; }
        .btn-net { background: #3498db; } .btn-db { background: #f1c40f; color: black; }
        .btn-srv { background: #2ecc71; } .btn-sec { background: #e74c3c; }
        button:hover { opacity: 0.8; transform: scale(1.05); }
        .log-entry { background: #16213e; padding: 15px; margin-bottom: 12px; border-radius: 8px; border-left: 5px solid #4ecca3; }
        .REMEDIATED { border-left-color: #fca311; }
        .FAILED { border-left-color: #e94560; }
        h1 { text-align: center; color: #4ecca3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AutoSANP Control Center</h1>
        
        <div class="button-group">
            <form action="/run/network_policy.yml" method="POST"><button class="btn-net">Run Network Policy</button></form>
            <form action="/run/database_policy.yml" method="POST"><button class="btn-db">Run Database Policy</button></form>
            <form action="/run/server_policy.yml" method="POST"><button class="btn-srv">Run Server Policy</button></form>
            <form action="/run/security_policy.yml" method="POST"><button class="btn-sec">Run Security Policy</button></form>
        </div>

        <div class="log-container">
            <h3>Enforcement Logs</h3>
            {% for log in logs %}
            <div class="log-entry {{ log.status }}">
                <strong>{{ log.timestamp }}</strong><br>
                Policy: <b style="color:#4ecca3">{{ log.policy }}</b> | Status: <strong>{{ log.status }}</strong><br>
                <em>{{ log.details }}</em>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    logs = []
    try:
        # Looking in the 'data' folder
        with open(LOG_FILE, 'r') as f:
            for line in f:
                logs.append(json.loads(line))
    except FileNotFoundError:
        pass
    return render_template_string(HTML_TEMPLATE, logs=reversed(logs))

@app.route('/run/<policy_name>', methods=['POST'])
def run_policy(policy_name):
    # This route triggers the specific YML file
    policy_path = os.path.join(BASE_DIR, "policies", policy_name)
    inventory_path = os.path.join(BASE_DIR, "data", "hosts.ini")
    
    # Run the Ansible command
    subprocess.run(f"ansible-playbook -i {inventory_path} {policy_path}", shell=True)
    
    # After running, go back to the dashboard to see the new log
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
