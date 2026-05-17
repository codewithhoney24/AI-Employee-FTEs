import os
import time
import subprocess
import uuid
import json
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# --- CONFIGURATION ---
VAULT_ROOT = "D:/AI-Employee-FTEs/KE_AI_Vault"
NEEDS_ACTION = os.path.join(VAULT_ROOT, "Needs_Action")
APPROVED_DIR = os.path.join(VAULT_ROOT, "Approved")
PLANS = os.path.join(VAULT_ROOT, "Plans")
HANDBOOK = os.path.join(VAULT_ROOT, "Company_Handbook.md")
BRIEFINGS_DIR = os.path.join(VAULT_ROOT, "Briefings")
LOGS_DIR = os.path.join(VAULT_ROOT, "Logs")
DONE_DIR = os.path.join(VAULT_ROOT, "Done")
STATE_FILE = os.path.join(LOGS_DIR, "orchestrator_state.json")

# Ensure directories exist
for d in [PLANS, BRIEFINGS_DIR, LOGS_DIR, DONE_DIR, APPROVED_DIR]:
    os.makedirs(d, exist_ok=True)

# MCP Simulation Logs
COMMS_LOG = os.path.join(LOGS_DIR, "comms.log")

# --- TASK MANAGEMENT ---
class Task:
    def __init__(self, file_path, data=None):
        if data:
            self.__dict__.update(data)
        else:
            self.id = str(uuid.uuid4())
            self.file_path = file_path
            self.filename = os.path.basename(file_path)
            self.status = "pending"  # pending, planning, in_progress, completed, failed
            self.plan = []
            self.current_step_index = 0
            self.created_at = time.time()
            self.last_updated = time.time()
            self.history = []

    def to_dict(self):
        return self.__dict__

    def add_history(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append(f"[{timestamp}] {message}")
        print(f"[{self.filename}] {message}")

active_tasks = []
last_audit_day = -1

def save_state():
    state = {
        "tasks": [t.to_dict() for t in active_tasks],
        "last_audit_day": last_audit_day
    }
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def load_state():
    global active_tasks, last_audit_day
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                active_tasks = [Task(None, data=t) for t in state.get("tasks", [])]
                last_audit_day = state.get("last_audit_day", -1)
                print(f"📜 State loaded: {len(active_tasks)} active tasks.")
        except Exception as e:
            print(f"❌ Failed to load state: {e}")

# --- AI INTERACTION ---
def ask_gemini(prompt, system_context=""):
    full_prompt = f"{system_context}\n\nUSER REQUEST:\n{prompt}"
    try:
        result = subprocess.run(
            ["gemini"], 
            input=full_prompt, 
            text=True, 
            capture_output=True, 
            encoding='utf-8'
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ Gemini Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"🔥 Subprocess Error: {e}")
        return None

# --- ORCHESTRATOR LOGIC ---
class GeminiHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            # Avoid processing files already in task list
            if any(t.file_path == event.src_path for t in active_tasks):
                return
            new_task = Task(event.src_path)
            active_tasks.append(new_task)
            new_task.add_history("New task detected and added to queue.")
            save_state()

class ApprovedHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".md"):
            filename = os.path.basename(event.src_path)
            print(f"✅ Approval detected: {filename}")
            # In a real system, this would trigger the actual action linked to the approval
            # For simulation, we log it and move to Done
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_comm("approval", "execute_approved", {"file": filename}, {"status": "success", "time": timestamp})
            
            # Move to Done folder
            done_path = os.path.join(DONE_DIR, filename)
            try:
                os.rename(event.src_path, done_path)
                print(f"🚀 Action executed for {filename}. Archived in Done.")
            except Exception as e:
                print(f"❌ Error moving approved file: {e}")

def log_comm(mcp, action, payload, response):
    with open(COMMS_LOG, 'a', encoding='utf-8') as f:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "mcp": mcp,
            "action": action,
            "payload": payload,
            "response": response
        }
        f.write(json.dumps(entry) + "\n")

def execute_step(task, step):
    desc = step.get("description", "")
    mcp_type = step.get("mcp", "general")
    action = step.get("action", "execute")
    params = step.get("params", {})
    
    task.add_history(f"Executing step: {desc}")
    
    if mcp_type == "odoo":
        # Call the real Odoo MCP server
        try:
            mcp_script = os.path.join(VAULT_ROOT, "scripts", "odoo_mcp_server.py")
            request = json.dumps({"id": task.id, "method": action, "params": params})
            result = subprocess.run(
                ["python", mcp_script],
                input=request,
                text=True,
                capture_output=True,
                encoding='utf-8'
            )
            if result.returncode == 0:
                response = json.loads(result.stdout.strip())
            else:
                response = {"status": "error", "message": f"MCP Error: {result.stderr}"}
        except Exception as e:
            response = {"status": "error", "message": str(e)}
    elif mcp_type in ["facebook", "instagram", "twitter"]:
        # Call the real Social MCP server
        try:
            mcp_script = os.path.join(VAULT_ROOT, "scripts", "social_mcp_server.py")
            # Map platform mcp_type to the specific method
            method = f"{mcp_type}_post" if action == "post" else action
            request = json.dumps({"id": task.id, "method": method, "params": params})
            result = subprocess.run(
                ["python", mcp_script],
                input=request,
                text=True,
                capture_output=True,
                encoding='utf-8'
            )
            if result.returncode == 0:
                response = json.loads(result.stdout.strip())
            else:
                response = {"status": "error", "message": f"MCP Error: {result.stderr}"}
        except Exception as e:
            response = {"status": "error", "message": str(e)}
    else:
        # Simulate other MCP calls
        payload = {"task_id": task.id, "description": desc}
        response = {"status": "success", "data": f"Executed {action} via {mcp_type}"}
    
    log_comm(mcp_type, action, params, response)
    return True

def process_task(task: Task):
    if task.status == "pending":
        task.status = "planning"
        task.add_history("Generating execution plan...")
        
        try:
            with open(task.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(HANDBOOK, 'r', encoding='utf-8') as f:
                rules = f.read()
            
            prompt = f"TASK:\n{content}\n\nRULES:\n{rules}\n\nCreate a JSON plan with a list of steps. Format: {{\"steps\": [ {{\"description\": \"...\", \"mcp\": \"email/odoo/browser/general\", \"action\": \"...\"}} ]}}"
            
            response = ask_gemini(prompt)
            if response:
                # Try to extract JSON from response
                try:
                    # Basic JSON extraction in case Gemini wraps it in code blocks
                    json_str = response
                    if "```json" in response:
                        json_str = response.split("```json")[1].split("```")[0].strip()
                    elif "```" in response:
                        json_str = response.split("```")[1].split("```")[0].strip()
                    
                    plan_data = json.loads(json_str)
                    task.plan = plan_data.get("steps", [])
                    task.status = "in_progress"
                    task.add_history(f"Plan generated with {len(task.plan)} steps.")
                    
                    # Save plan to file for reference
                    plan_path = os.path.join(PLANS, f"PLAN_{task.filename}")
                    with open(plan_path, 'w', encoding='utf-8') as f:
                        f.write(response)
                except Exception as e:
                    task.add_history(f"Failed to parse plan JSON: {e}")
                    task.status = "failed"
            else:
                task.status = "failed"
        except Exception as e:
            task.add_history(f"Error during planning: {e}")
            task.status = "failed"
        save_state()

    if task.status == "in_progress":
        if task.current_step_index < len(task.plan):
            step = task.plan[task.current_step_index]
            success = execute_step(task, step)
            if success:
                task.current_step_index += 1
                task.add_history(f"Step {task.current_step_index} completed.")
                if task.current_step_index >= len(task.plan):
                    task.status = "completed"
                    task.add_history("Task completed successfully.")
                    # Move file to Done
                    done_path = os.path.join(DONE_DIR, task.filename)
                    if os.path.exists(task.file_path):
                        os.rename(task.file_path, done_path)
            else:
                task.add_history(f"Step {task.current_step_index + 1} failed. Retrying...")
                # Could add retry logic here
        else:
            task.status = "completed"
        save_state()

def trigger_business_audit():
    print("📈 Initiating Autonomous Business Audit...")
    
    # 1. Gather context
    audit_context = "Data for Weekly Audit:\n"
    # Read comms logs
    if os.path.exists(COMMS_LOG):
        with open(COMMS_LOG, 'r', encoding='utf-8') as f:
            comms = f.readlines()[-50:] # Last 50 actions
            audit_context += "Recent Comms:\n" + "".join(comms) + "\n"
    
    # Check Done tasks
    done_files = os.listdir(DONE_DIR)
    audit_context += f"Completed Tasks this week: {len(done_files)}\n"
    
    prompt = "Based on the provided data, generate a CEO Briefing for Monday morning. Highlight key achievements, financial status (simulated), and items requiring attention. Use a professional, executive tone."
    
    briefing_content = ask_gemini(prompt, system_context=audit_context)
    if briefing_content:
        briefing_file = os.path.join(BRIEFINGS_DIR, f"CEO_Briefing_{datetime.now().strftime('%Y%m%d')}.md")
        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write(briefing_content)
        print(f"📊 CEO Briefing generated: {briefing_file}")
    else:
        print("❌ Failed to generate CEO Briefing.")

def orchestrator_loop():
    global last_audit_day
    print("🔄 Orchestrator loop started.")
    while True:
        # Process pending tasks
        for task in list(active_tasks):
            if task.status in ["pending", "planning", "in_progress"]:
                process_task(task)
            
            if task.status in ["completed", "failed"]:
                active_tasks.remove(task)
                save_state()
        
        # Check for scheduled events - Autonomous Business Audit
        now = datetime.now()
        # Trigger audit on Sunday evening (6 is Sunday)
        if now.weekday() == 6 and now.hour >= 23 and now.day != last_audit_day:
            trigger_business_audit()
            last_audit_day = now.day
            save_state()

        time.sleep(10) # 10 second loop

if __name__ == "__main__":
    load_state()
    
    # Scan for existing tasks on startup
    for f in os.listdir(NEEDS_ACTION):
        if f.endswith(".md"):
            full_path = os.path.join(NEEDS_ACTION, f)
            if not any(t.file_path == full_path for t in active_tasks):
                new_task = Task(full_path)
                active_tasks.append(new_task)
                new_task.add_history("Existing task identified on startup.")
    save_state()

    observer = Observer()
    observer.schedule(GeminiHandler(), NEEDS_ACTION, recursive=False)
    observer.schedule(ApprovedHandler(), APPROVED_DIR, recursive=False)
    observer.start()
    print("🚀 K-Electric AI Brain is LIVE. Monitoring Needs_Action and Approved...")

    orchestrator_thread = Thread(target=orchestrator_loop)
    orchestrator_thread.daemon = True 
    orchestrator_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("🛑 Orchestrator shutting down...")
    observer.join()

