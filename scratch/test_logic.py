
import re

def clean_chinese(text):
    if not isinstance(text, str): return text
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    cleaned = chinese_pattern.sub('', text).strip()
    return cleaned

# TEST CASE 1: Tiếng Việt thuần túy
text1 = "Dạ thưa thầy em đã rõ"
# TEST CASE 2: Tiếng Trung trộn tiếng Việt
text2 = "Dạ thưa thầy 谢谢 em đã rõ"
# TEST CASE 3: Chỉ có tiếng Trung
text3 = "谢谢"

print(f"Test 1 (VN only): '{clean_chinese(text1)}' -> Success: {clean_chinese(text1) == text1}")
print(f"Test 2 (Mixed): '{clean_chinese(text2)}' -> Cleaned: {clean_chinese(text2)}")
print(f"Test 3 (CN only): '{clean_chinese(text3)}' -> Empty: '{clean_chinese(text3)}'")

# Kiểm tra fallback
def get_final_resp(raw_resp):
    cleaned = clean_chinese(raw_resp)
    if not cleaned or len(cleaned) < 2:
        return "Dạ thưa thầy, em vẫn chưa rõ lắm, thầy hướng dẫn thêm cho em được không ạ?"
    return cleaned

print(f"Test Fallback (Empty): '{get_final_resp(text3)}'")
print(f"Test Fallback (Normal): '{get_final_resp(text1)}'")
