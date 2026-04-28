import docx
import json
import os

def extract_text_from_docx(path):
    doc = docx.Document(path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

if __name__ == "__main__":
    docx_path = "/home/chinh303/code/gpsaiedu/GPS_AIedu/data/raw/thuvienhoclieu.com-Trac-nghiem-xac-Suat-hay-co-dap-an.docx"
    output_text_path = "/home/chinh303/code/gpsaiedu/GPS_AIedu/data/raw/exam_text.txt"
    
    if os.path.exists(docx_path):
        text = extract_text_from_docx(docx_path)
        with open(output_text_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Đã trích xuất văn bản thành công vào {output_text_path}")
    else:
        print("Không tìm thấy file docx.")
