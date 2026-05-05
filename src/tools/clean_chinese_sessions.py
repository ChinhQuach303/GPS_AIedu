import csv
import re
import os

INPUT_FILE = "GPS_AIedu/data/processed/augmented_conversations_final.csv"
OUTPUT_FILE = "GPS_AIedu/data/processed/augmented_conversations_clean.csv"
LOG_FILE = "GPS_AIedu/data/processed/cleaning_log.txt"

CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff]')

def clean_csv():
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} not found.")
        return

    sessions_kept = 0
    sessions_removed = 0
    
    # We'll use a custom parser to handle potentially malformed CSV or just use csv module correctly
    with open(INPUT_FILE, 'r', encoding='utf-8') as fin, \
         open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as fout, \
         open(LOG_FILE, 'w', encoding='utf-8') as flog:
        
        reader = csv.reader(fin)
        writer = csv.writer(fout)
        
        # Read header
        try:
            header = next(reader)
            writer.writerow(header)
        except StopIteration:
            return

        for row in reader:
            if len(row) < 5:
                continue
            
            group, student_id, level, qid, dialogue = row[0], row[1], row[2], row[3], row[4]
            
            # Check for Chinese characters in dialogue
            if CHINESE_PATTERN.search(dialogue):
                sessions_removed += 1
                flog.write(f"REMOVED: Group={group}, ID={student_id}, QID={qid}\n")
                flog.write(f"REASON: Chinese detected in dialogue\n")
                # flog.write(f"CONTENT: {dialogue[:100]}...\n\n")
            else:
                writer.writerow(row)
                sessions_kept += 1

    print(f"Cleaning complete!")
    print(f"Sessions kept: {sessions_kept}")
    print(f"Sessions removed: {sessions_removed}")
    print(f"Details saved to {LOG_FILE}")

    # Swap files
    os.replace(OUTPUT_FILE, INPUT_FILE)
    print(f"Original file updated.")

if __name__ == "__main__":
    clean_csv()
