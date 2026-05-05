import re
import os

INPUT_FILE = "GPS_AIedu/data/processed/augmented_conversations_final.csv"
OUTPUT_FILE = "GPS_AIedu/data/processed/augmented_conversations_clean.csv"
LOG_FILE = "GPS_AIedu/data/processed/cleaning_log.txt"

CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff]')
SESSION_START_PATTERN = re.compile(r'^(GPS|Non-GPS),', re.MULTILINE)

def clean_brute_force():
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split content into sessions
    # We find all indices of "GPS," or "Non-GPS," at the beginning of a line
    matches = list(SESSION_START_PATTERN.finditer(content))
    
    sessions = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        sessions.append(content[start:end])

    header = content[:matches[0].start()] if matches else ""
    
    sessions_kept = 0
    sessions_removed = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as fout, \
         open(LOG_FILE, 'w', encoding='utf-8') as flog:
        
        fout.write(header)
        
        for session in sessions:
            if CHINESE_PATTERN.search(session):
                sessions_removed += 1
                flog.write(f"REMOVED SESSION STARTING WITH: {session[:100]}...\n\n")
            else:
                fout.write(session)
                sessions_kept += 1

    print(f"Brute-force cleaning complete!")
    print(f"Sessions kept: {sessions_kept}")
    print(f"Sessions removed: {sessions_removed}")
    
    os.replace(OUTPUT_FILE, INPUT_FILE)
    print(f"Original file updated.")

if __name__ == "__main__":
    clean_brute_force()
