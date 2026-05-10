import pypdf
import docx
import re
from io import BytesIO

from utils.resume_analyzer import ResumeAnalyzer


class ResumeParser:
    def __init__(self):
        pass
        
    def extract_text_from_pdf(self, pdf_file):
        try:
            # Handle different file input types
            if hasattr(pdf_file, 'read'):
                # If it's a file-like object
                file_content = pdf_file.read()
                pdf_file.seek(0)  # Reset file pointer
            else:
                # If it's already bytes
                file_content = pdf_file
                
            pdf_reader = pypdf.PdfReader(BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                else:
                    # Handle empty page text
                    text += "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
            
    def extract_text_from_docx(self, docx_file):
        try:
            doc = docx.Document(BytesIO(docx_file.read()))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""
            
    def extract_text(self, file):
        # Reset file pointer to beginning
        file.seek(0)
        
        if file.name.endswith('.pdf'):
            return self.extract_text_from_pdf(file)
        elif file.name.endswith('.docx'):
            return self.extract_text_from_docx(file)
        else:
            return ""
            
    def parse(self, file):
        text = self.extract_text(file)
        ra = ResumeAnalyzer()
        personal = ra.extract_personal_info(text)
        return {
            "name": personal.get("name", ""),
            "email": personal.get("email", ""),
            "phone": personal.get("phone", ""),
            "linkedin": personal.get("linkedin", ""),
            "github": personal.get("github", ""),
            "portfolio": personal.get("portfolio", ""),
            "summary": ra.extract_summary(text),
            "skills": list(ra.extract_skills(text)),
            "education": ra.extract_education(text),
            "experience": ra.extract_experience(text),
            "qualifications": ra.extract_qualifications(text),
            "raw_text": text,
        }