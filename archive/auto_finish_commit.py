import json
import time
import subprocess
import os

PROGRESS_FILE = "data/processed/simulation_progress.json"
TARGET_COUNT = 45

def check_and_commit():
    print(f"🕵️ Monitoring progress... Target: {TARGET_COUNT} questions.")
    
    while True:
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, "r") as f:
                    progress = json.load(f)
                    completed = len(progress.get("completed_qids", []))
                    
                    print(f"📊 Current progress: {completed}/{TARGET_COUNT}")
                    
                    if completed >= TARGET_COUNT:
                        print("🎉 ALL QUESTIONS FINISHED! Running final analysis and commit...")
                        
                        # 1. Run final analysis
                        # We use the bridge script I created earlier
                        subprocess.run(["python", "src/analysis/bridge_sim_to_analysis.py"], cwd=".")
                        
                        # 2. Git Commit
                        print("💾 Committing results to Git...")
                        subprocess.run(["git", "add", "data/processed/", "reports/"])
                        subprocess.run(["git", "commit", "-m", "GPS-AIedu: Complete Agent-to-Agent Simulation Data & Analysis"])
                        
                        # Optional: Push
                        # subprocess.run(["git", "push"])
                        
                        print("✅ MISSION ACCOMPLISHED. SYSTEM SHUTTING DOWN.")
                        break
            except Exception as e:
                print(f"⚠️ Error reading progress: {e}")
        
        time.sleep(300) # Check every 5 minutes

if __name__ == "__main__":
    check_and_commit()
