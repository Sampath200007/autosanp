import os
import time
import subprocess
import json

# Path helper: points to the data folder relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "data", "autosanp_logs.json")
INVENTORY = os.path.join(BASE_DIR, "data", "hosts.ini")

def log_action(policy_name, status, message):
    log_entry = {
        "timestamp": time.ctime(),
        "host": "Managed Nodes",
        "policy": policy_name,
        "status": status,
        "details": message
    }
    # Using the absolute path to ensure logs save in the 'data' folder
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + "\n")

def enforce_policy(policy_file):
    policy_path = os.path.join(BASE_DIR, "policies", policy_file)
    print(f"[{time.ctime()}] AutoSANP: Enforcing {policy_file}...")
    
    # Updated command to use absolute paths
    command = f"ansible-playbook -i {INVENTORY} {policy_path}"
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if "changed=1" in result.stdout or "changed=2" in result.stdout:
            msg = f"Policy enforced! {policy_file} corrected issues."
            log_action(policy_file, "REMEDIATED", msg)
        elif "changed=0" in result.stdout:
            msg = f"Policy healthy. No changes needed for {policy_file}."
            log_action(policy_file, "SUCCESS", msg)
        else:
            msg = "Policy check failed. Check network or permissions."
            log_action(policy_file, "FAILED", msg)
            
        print(f"Status: {msg}")
    except Exception as e:
        log_action(policy_file, "ERROR", str(e))

# Example: Running specific policies in a loop
if __name__ == "__main__":
    while True:
        # You can now list all 4 policies here to automate them all!
        policies_to_run = [
            "server_policy.yml", 
            "network_policy.yml", 
            "security_policy.yml", 
            "database_policy.yml"
        ]
        
        for p in policies_to_run:
            enforce_policy(p)
            
        print("Waiting 60 seconds for next check-up...")
        time.sleep(60)
      
