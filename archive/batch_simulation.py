import subprocess
import time
import json
import os

# --- SETTINGS ---
PROGRESS_FILE = "data/processed/simulation_progress.json"
DATA_PATH = "data/processed/probabilities_questions.json"
PERSONAS = ["HS0001", "HS0002", "HS0003", "HS0004", "HS0005"]
SLEEP_BETWEEN_SESSIONS = 5 # Seconds to let GPU cool down
SLEEP_BETWEEN_QUESTIONS = 10

def load_questions():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"last_qid": 0, "completed_qids": []}

def save_progress(qid, completed_list):
    with object_open(PROGRESS_FILE, "w") as f:
        json.dump({"last_qid": qid, "completed_qids": completed_list}, f)

# Hack for non-standard open name if needed, but normally just open
def object_open(path, mode):
    return open(path, mode)

def run_batch():
    questions = load_questions()
    progress = get_progress()
    
    print(f"📦 Starting batch simulation for {len(questions)} questions.")
    print(f"📈 Progress: {len(progress['completed_qids'])}/{len(questions)} questions done.")
    
    for q in questions:
        qid = q['id']
        if qid in progress['completed_qids']:
            continue
            
        print(f"\n--- Processing Question ID: {qid} ---")
        for persona in PERSONAS:
            print(f"   - Running Persona: {persona}...")
            
            # Call the existing simulation script
            cmd = [
                "python", "src/ai/agent_to_agent_sim.py",
                "--qid", str(qid),
                "--persona", persona,
                "--auto"
            ]
            
            try:
                # We use check_call to ensure it finishes
                subprocess.check_call(cmd)
                print(f"   ✅ Done: {persona}")
            except Exception as e:
                print(f"   ❌ Error in {persona}: {e}")
            
            time.sleep(SLEEP_BETWEEN_SESSIONS)
            
        # Update progress after each full question
        progress['completed_qids'].append(qid)
        progress['last_qid'] = qid
        with open(PROGRESS_FILE, "w") as f:
            json.dump(progress, f)
            
        print(f"🏁 Finished Question {qid}. Taking a break.")
        time.sleep(SLEEP_BETWEEN_QUESTIONS)

if __name__ == "__main__":
    run_batch()
