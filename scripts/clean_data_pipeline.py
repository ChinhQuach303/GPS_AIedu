import pandas as pd
import re
import os

def is_chinese(text):
    # Regex phát hiện ký tự Trung Quốc
    return re.search(r'[\u4e00-\u9fff]', text)

def clean_dialogue(text):
    if not isinstance(text, str):
        return text
    
    # 0. Loại bỏ triệt để ký tự tiếng Trung
    text = re.sub(r'[\u4e00-\u9fff]', '', text)
    
    # 1. Chuẩn hóa nhãn xưng hô (Sửa lỗi Double Label)
    # Tìm bất kỳ cụm nhãn nào bị lặp lại hoặc có chứa từ khóa AI/Student
    text = re.sub(r'^.*(AI|Tutor|Thầy giáo|Thầy|Teacher):\s*', 'Thầy: ', text, flags=re.MULTILINE)
    text = re.sub(r'^.*(Student|Học sinh|Hội thoại|Em):\s*', 'Em: ', text, flags=re.MULTILINE)
    
    # Xử lý trường hợp bị lặp lại sau khi đã sub (ví dụ: Thầy: Thầy:)
    text = re.sub(r'^Thầy:\s*Thầy:', 'Thầy:', text, flags=re.MULTILINE)
    text = re.sub(r'^Em:\s*Em:', 'Em:', text, flags=re.MULTILINE)
    
    # 2. Tách hội thoại thành các lượt (turns)
    turns = text.split('\n')
    cleaned_turns = []
    
    seen_greetings = False
    
    for i, turn in enumerate(turns):
        turn = turn.strip()
        if not turn: continue
        
        # Loại bỏ nhãn GPS [G], [P], [S] để trông giống người thật
        turn = re.sub(r'\[[GPS]\]', '', turn).strip()
        
        # Loại bỏ các đoạn văn bản thừa phổ biến của AI ở cuối câu
        turn = re.sub(r'Câu hỏi:.*$', '', turn)
        turn = re.sub(r'Em có thắc mắc gì không\?.*$', '', turn)
        turn = re.sub(r'Hãy cùng thực hiện.*$', '', turn)
        
        # Xử lý lặp lời chào
        greetings = ["Thầy chào em!", "Chào em!", "Chào bạn!", "Xin chào!"]
        for g in greetings:
            if turn.startswith(f"Thầy: {g}"):
                if seen_greetings:
                    turn = turn.replace(f"Thầy: {g}", "Thầy:").strip()
                else:
                    seen_greetings = True
        
        # Xóa các nhãn rỗng sau khi đã strip hết nội dung
        if turn == "Thầy:" or turn == "Em:":
            continue
            
        cleaned_turns.append(turn)
    
    return "\n".join(cleaned_turns)

def process_file(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"⚠️ Không tìm thấy file: {input_path}")
        return
    
    print(f"🧹 Đang làm sạch: {input_path}...")
    df = pd.read_csv(input_path)
    
    # Áp dụng hàm làm sạch
    df['dialogue'] = df['dialogue'].apply(clean_dialogue)
    
    # Lọc bỏ các phiên hội thoại:
    # 1. Quá ngắn (< 3 lượt)
    # 2. Vẫn còn sót tiếng Trung (nếu có lỗi logic nào đó)
    original_len = len(df)
    df = df[df['dialogue'].str.count('\n') >= 3]
    
    # Kiểm tra lại một lần nữa để chắc chắn không còn ký tự Trung Quốc nào
    df = df[~df['dialogue'].apply(lambda x: bool(re.search(r'[\u4e00-\u9fff]', x)))]
    
    print(f"  > Đã lọc bỏ {original_len - len(df)} phiên hội thoại không đạt chuẩn hoặc lỗi tiếng Trung.")
    
    df.to_csv(output_path, index=False)
    print(f"✅ Đã lưu file sạch tại: {output_path}")

def main():
    # Danh sách các file cần làm sạch
    files_to_clean = [
        ("data/outputs/massive_simulation_results.csv", "data/outputs/cleaned_massive_results.csv"),
        ("data/outputs/baseline_conversations.csv", "data/outputs/cleaned_baseline_results.csv"),
        ("data/outputs/cross_model_conversations.csv", "data/outputs/cleaned_cross_model_results.csv")
    ]
    
    for inp, outp in files_to_clean:
        process_file(inp, outp)

if __name__ == "__main__":
    main()
