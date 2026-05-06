
import sympy as sp
import re

class MathVerifier:
    @staticmethod
    def extract_expression(text):
        """
        Trích xuất biểu thức toán học từ text (ví dụ: tìm trong LaTeX hoặc các con số).
        """
        # Tìm các biểu thức trong \( ... \) hoặc \[ ... \]
        matches = re.findall(r'\\\( (.*?) \\\)|\\\[ (.*?) \\\]', text)
        if matches:
            # Lấy group không rỗng
            expr = [m[0] or m[1] for m in matches][-1]
            return expr
        
        # Nếu không có LaTeX, tìm các con số/phép tính đơn giản
        num_match = re.search(r'(\d+[\/\*\-\+]\d+|\d+)', text)
        return num_match.group(0) if num_match else None

    @staticmethod
    def verify_step(student_input, expected_value):
        """
        So sánh kết quả của học sinh với kết quả mong đợi bằng SymPy.
        """
        try:
            student_expr = MathVerifier.extract_expression(student_input)
            if not student_expr:
                return False, "Không tìm thấy biểu thức toán học."

            # Chuyển đổi LaTeX sang SymPy (Cần xử lý thêm nếu LaTeX phức tạp)
            # Ở đây ta giả lập so sánh đơn giản trước
            student_val = sp.sympify(student_expr.replace('\\', ''))
            expected_val = sp.sympify(str(expected_value).replace('\\', ''))

            if sp.simplify(student_val - expected_val) == 0:
                return True, "Chính xác!"
            else:
                return False, f"Kết quả chưa đúng. Em hãy kiểm tra lại phép tính."
        except Exception as e:
            return False, f"Lỗi xử lý toán học: {str(e)}"
