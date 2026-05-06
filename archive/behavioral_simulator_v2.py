
import random

class StudentSimulatorV2:
    def __init__(self, level):
        self.level = level
        self.frustration = 0.0 # 0.0 to 1.0
        self.understanding = 0.0
        
    def respond_to_ai(self, ai_response):
        # Spec 5: Frustration Modeling
        response_len = len(ai_response)
        
        # If AI is too short (unhelpful) or too long (overwhelming)
        if response_len < 50:
            self.frustration += 0.2
        elif response_len > 1000:
            self.frustration += 0.1
            
        # If AI gives direct answer [S] without [G] or [P]
        if "[S]" in ai_response and self.understanding < 0.5:
            # Student is happy but learning is low (The "Lười" effect)
            self.frustration -= 0.1
            return "Em cảm ơn thầy, đáp án đúng rồi ạ."
            
        if self.frustration > 0.7:
            return "Thầy ơi em vẫn chưa hiểu, thầy giải thích kỹ hơn được không ạ? Em thấy hơi rối."
            
        return "Dạ em hiểu rồi, em sẽ thử tính tiếp ạ."

def main():
    print("Testing Behavioral Simulation (Spec 5: Frustration Modeling)...")
    student = StudentSimulatorV2("Trung bình")
    
    # Test unhelpful AI
    print(f"Initial frustration: {student.frustration}")
    msg = student.respond_to_ai("Đáp án là 1/16.")
    print(f"Response to short AI: {msg} | Frustration: {student.frustration}")
    
    # Test another unhelpful turn
    msg = student.respond_to_ai("Cố lên em.")
    print(f"Response to short AI: {msg} | Frustration: {student.frustration}")
    
    # Test overwhelmed turn
    msg = student.respond_to_ai("A" * 1200)
    print(f"Response to long AI: {msg} | Frustration: {student.frustration}")

if __name__ == "__main__":
    main()
