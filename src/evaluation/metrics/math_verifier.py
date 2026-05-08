import re
from sympy import simplify, Eq, sympify
from sympy.parsing.latex import parse_latex
import traceback

class MathVerifier:
    def __init__(self):
        # Regex to match both inline \(...\) and display \[...\] LaTeX math blocks
        self.latex_pattern = re.compile(r'\\\[(.*?)\\\]|\\\((.*?)\\\)', re.DOTALL)
        
    def _clean_latex(self, latex_str):
        """Clean common LLM LaTeX artifacts before parsing."""
        if not latex_str:
            return ""
        latex_str = latex_str.strip()
        # Replace non-standard or unsupported operators
        latex_str = latex_str.replace(r'\times', r'*')
        latex_str = latex_str.replace(r'\div', r'/')
        latex_str = latex_str.replace(r'\,', '')
        latex_str = latex_str.replace(r'\;', '')
        latex_str = latex_str.replace(r'\ ', '')
        latex_str = latex_str.replace(r'\text{', r'\mathrm{')
        return latex_str

    def is_valid_math(self, latex_str):
        """
        Attempt to parse and validate a LaTeX mathematical string.
        Returns True if it represents a valid mathematical structure or equation.
        """
        cleaned_latex = self._clean_latex(latex_str)
        if not cleaned_latex.strip():
            return False
            
        try:
            # Handle equations containing '='
            if '=' in cleaned_latex:
                parts = cleaned_latex.split('=', 1)
                lhs_str, rhs_str = parts[0].strip(), parts[1].strip()
                
                try:
                    lhs_expr = parse_latex(lhs_str)
                    rhs_expr = parse_latex(rhs_str)
                    
                    # If both sides parse successfully, it's a valid mathematical statement.
                    # We can also strictly check if they are mathematically equal:
                    # diff = simplify(lhs_expr - rhs_expr)
                    # return diff == 0
                    # However, for VAI, we primarily care if the student wrote a *parsable* equation.
                    return True
                except Exception:
                    return False
            
            # Handle standard expressions
            else:
                expr = parse_latex(cleaned_latex)
                # If it successfully parses into a SymPy object, it's valid.
                return True
                
        except Exception as e:
            # Parsing failed
            return False

    def extract_math_blocks(self, text):
        """Extract all LaTeX math blocks from a given text."""
        blocks = []
        matches = self.latex_pattern.findall(text)
        for match in matches:
            # match is a tuple like ('display_math', '') or ('', 'inline_math')
            latex_content = match[0] if match[0] else match[1]
            if latex_content:
                blocks.append(latex_content)
        return blocks

    def calculate_vai(self, dialogue_text):
        """
        Calculate Verifiable Autonomy Index for a given dialogue session.
        VAI = (Valid Math by Student) / (Valid Math by Student + Valid Math by Tutor)
        """
        if not isinstance(dialogue_text, str):
            return 0.0
            
        lines = dialogue_text.split('\n')
        
        tutor_math_count = 0
        student_math_count = 0
        
        current_speaker = None
        current_buffer = []
        
        def process_buffer(speaker, content):
            nonlocal tutor_math_count, student_math_count
            text = "\n".join(content)
            math_blocks = self.extract_math_blocks(text)
            valid_count = sum(1 for block in math_blocks if self.is_valid_math(block))
            
            if speaker == "Thầy":
                tutor_math_count += valid_count
            elif speaker == "Em":
                student_math_count += valid_count
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith("Thầy:"):
                if current_speaker:
                    process_buffer(current_speaker, current_buffer)
                current_speaker = "Thầy"
                current_buffer = [line_stripped.replace("Thầy:", "", 1)]
            elif line_stripped.startswith("Em:"):
                if current_speaker:
                    process_buffer(current_speaker, current_buffer)
                current_speaker = "Em"
                current_buffer = [line_stripped.replace("Em:", "", 1)]
            else:
                current_buffer.append(line_stripped)
                
        # Process the last buffer
        if current_speaker:
            process_buffer(current_speaker, current_buffer)
            
        total_valid_math = student_math_count + tutor_math_count
        if total_valid_math == 0:
            return {"vai": 0.0, "student_valid_math": 0, "tutor_valid_math": 0, "total_valid_math": 0}
            
        vai = student_math_count / total_valid_math
        
        return {
            "vai": vai,
            "student_valid_math": student_math_count,
            "tutor_valid_math": tutor_math_count,
            "total_valid_math": total_valid_math
        }

if __name__ == "__main__":
    # Test script locally
    verifier = MathVerifier()
    
    sample_dialogue = '''
Thầy: [G] Chào em, chúng ta sẽ bắt đầu nhé. Xác suất mặt sấp là \( P(S) = \frac{1}{2} \).
Em: Dạ. Vậy mặt ngửa là \( P(N) = 1 - \frac{1}{2} = \frac{1}{2} \).
Thầy: [P] Đúng rồi. Hãy tính xác suất 2 mặt sấp: \( P(S) \times P(S) = ? \).
Em: Dạ là \( \frac{1}{2} * \frac{1}{2} = \frac{1}{4} \). Còn đây là lỗi cú pháp \( \frac{1{2} \).
Thầy: [S] Rất tốt, kết quả là \( \frac{1}{4} \).
    '''
    
    result = verifier.calculate_vai(sample_dialogue)
    print(f"Test Result: {result}")
