import json
import re
import os

def parse_exam_v4(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tìm vị trí thực sự của phần LỜI GIẢI (dòng chỉ có chữ LỜI GIẢI)
    # Hoặc tìm phần xuất hiện sau phần ĐÁP ÁN
    parts = re.split(r'\nLỜI GIẢI\n', content)
    if len(parts) < 2:
        # Thử lại với trường hợp không có xuống dòng chuẩn
        parts = content.split("ĐÁP ÁN")
        if len(parts) < 2: return []
        solution_section = parts[-1]
    else:
        solution_section = parts[-1]
    
    lines = solution_section.split('\n')
    questions = []
    current_q = None
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean: continue
        
        # Nhận diện Câu hỏi mới
        if re.match(r'^Câu \d+:', line_clean):
            if current_q: questions.append(current_q)
            
            parts = line_clean.split(":", 1)
            q_text = parts[1].strip()
            current_q = {
                "id": len(questions) + 1,
                "question": q_text,
                "options": [],
                "answer": "",
                "solution": ""
            }
            continue
            
        if not current_q: continue
        
        # Nhận diện Lựa chọn (A, B, C, D)
        if re.search(r'^[A-D]\.', line_clean) or "A." in line_clean:
            opts = re.split(r'\t|(?=[A-D]\.)', line_clean)
            current_q["options"].extend([o.strip() for o in opts if o.strip()])
            
        # Nhận diện Lời giải
        elif "Lời giải." in line_clean:
            current_q["solution"] = line_clean.replace("Lời giải.", "").strip()
            
        # Nhận diện Đáp án chốt
        elif "Chọn" in line_clean:
            ans_match = re.search(r'Chọn\s*([A-D])', line_clean)
            if ans_match:
                current_q["answer"] = ans_match.group(1)
            current_q["solution"] += " " + line_clean
            
        else:
            if not current_q["solution"]:
                current_q["question"] += " " + line_clean
            else:
                current_q["solution"] += " " + line_clean

    if current_q: questions.append(current_q)
    
    # Làm sạch lần cuối
    for q in questions:
        q["solution"] = re.sub(r'Chọn\s*[A-D]\.?$', '', q["solution"]).strip()
        # Loại bỏ các dấu chấm vô nghĩa nếu options bị lỗi
        q["options"] = [opt for opt in q["options"] if len(opt) > 3 or opt.startswith(('A.', 'B.', 'C.', 'D.'))]

    return questions

if __name__ == "__main__":
    input_txt = "/home/chinh303/code/gpsaiedu/GPS_AIedu/data/raw/exam_text.txt"
    output_json = "/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/probabilities_questions.json"
    
    data = parse_exam_v4(input_txt)
    if data:
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Thành công! Đã khôi phục {len(data)} câu hỏi đầy đủ đáp án.")
    else:
        print("Không parse được dữ liệu.")
