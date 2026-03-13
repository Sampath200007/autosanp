from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import subprocess
from datetime import datetime


app = Flask(__name__)
#Database Setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db = SQLAlchemy(app)

#Database Model for logs
class AuditLog(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    action = db.Column(db.String(100))
    status = db.Column(db.String(20))
    output = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
	logs=AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
	return render_template('index.html',logs=logs)

@app.route('/run-policies')
def deploy_policies():
	command = [
		"ansible-playbook",
		"-i" , "inventory.ini",
		"site.yml",
		"--become",
		"--extra-vars",
		"ansible_sudo_pass=sunil ansible_password=sunil ansible_become_pass=sunil"
		]

	try:
		result = subprocess.run(command, capture_output=True, text=True)


		status = "Success" if result.returncode == 0 else "Failed" 
		full_output = result.stdout + "\n" + result.stderr

	except Execution as e:
		status = "Failed"
		full_output = str(e)

	new_log = AuditLog(
		action="Deploy SIte Policies",
		status=status,
		output=full_output)

	db.session.add(new_log)
	db.session.commit()

	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000 , debug=True)


