
import re
import pandas as pd

class DataCleaner:
    @staticmethod
    def remove_chinese_characters(text):
        if not isinstance(text, str): return text
        # Regex loại bỏ các ký tự trong dải tiếng Trung
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        return chinese_pattern.sub('', text)

    @staticmethod
    def standardize_latex(text):
        if not isinstance(text, str): return text
        # Thay thế $...$ bằng \(...\)
        text = re.sub(r'(?<!\$)\$(?!\$)(.*?)\$', r'\\(\1\\)', text)
        # Thay thế $$...$$ bằng \[...\]
        text = re.sub(r'\$\$(.*?)\$\$', r'\\[\1\\]', text)
        return text

    @staticmethod
    def clean_dialogue(text):
        if not isinstance(text, str): return text
        # Loại bỏ các khoảng trắng thừa và dòng trống liên tiếp
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()

    def process_dataframe(self, df, columns=['Dialogue']):
        for col in columns:
            if col in df.columns:
                df[col] = df[col].apply(self.remove_chinese_characters)
                df[col] = df[col].apply(self.standardize_latex)
                df[col] = df[col].apply(self.clean_dialogue)
        return df
