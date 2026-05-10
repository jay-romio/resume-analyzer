"""
Enhanced File Upload and Validation System for Resume Analyzer
"""
import os
import streamlit as st
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
import hashlib

# Try to import magic, but make it optional
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

class FileUploadValidator:
    """Enhanced file upload validation and processing system"""
    
    def __init__(self):
        # File configuration
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {'pdf', 'docx', 'doc'}
        self.allowed_mime_types = {
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword'
        }
        
        # File type detection patterns
        self.file_signatures = {
            'pdf': b'%PDF-',
            'docx': b'PK\x03\x04',
            'doc': b'\xd0\xcf\x11\xe0'
        }
    
    def validate_file_size(self, file) -> Tuple[bool, str]:
        """Validate file size"""
        try:
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset position
            
            if file_size > self.max_file_size:
                return False, f"File size ({file_size/1024/1024:.1f}MB) exceeds maximum allowed size (10MB)"
            return True, "File size valid"
        except Exception as e:
            return False, f"Error checking file size: {str(e)}"
    
    def validate_file_extension(self, filename: str) -> Tuple[bool, str]:
        """Validate file extension"""
        if not filename:
            return False, "No filename provided"
        
        extension = filename.split('.')[-1].lower()
        if extension not in self.allowed_extensions:
            return False, f"File type '.{extension}' is not allowed. Allowed types: {', '.join(self.allowed_extensions)}"
        return True, "File extension valid"
    
    def validate_file_signature(self, file) -> Tuple[bool, str, str]:
        """Validate file signature to detect file type"""
        try:
            # Read first few bytes to check file signature
            file.seek(0)
            header = file.read(8)
            file.seek(0)
            
            detected_type = None
            for file_type, signature in self.file_signatures.items():
                if header.startswith(signature):
                    detected_type = file_type
                    break
            
            if not detected_type:
                return False, "Unable to detect file type. File may be corrupted.", ""
            
            return True, "File signature valid", detected_type
        except Exception as e:
            return False, f"Error reading file signature: {str(e)}", ""
    
    def generate_file_hash(self, file) -> str:
        """Generate SHA-256 hash of file for duplicate detection"""
        file.seek(0)
        content = file.read()
        file.seek(0)
        return hashlib.sha256(content).hexdigest()
    
    def comprehensive_validation(self, file, filename: str) -> Dict[str, Any]:
        """Perform comprehensive file validation"""
        validation_results = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'file_info': {},
            'detected_type': None
        }
        
        # Store basic file info
        validation_results['file_info'] = {
            'filename': filename,
            'upload_time': datetime.now().isoformat()
        }
        
        # 1. Validate filename
        if not filename:
            validation_results['errors'].append("No filename provided")
            return validation_results
        
        # 2. Validate file size
        size_valid, size_msg = self.validate_file_size(file)
        if not size_valid:
            validation_results['errors'].append(size_msg)
            return validation_results
        validation_results['file_info']['size_valid'] = True
        validation_results['file_info']['size_msg'] = size_msg
        
        # 3. Validate file extension
        ext_valid, ext_msg = self.validate_file_extension(filename)
        if not ext_valid:
            validation_results['errors'].append(ext_msg)
            return validation_results
        validation_results['file_info']['extension_valid'] = True
        validation_results['file_info']['extension'] = filename.split('.')[-1].lower()
        
        # 4. Validate file signature
        sig_valid, sig_msg, detected_type = self.validate_file_signature(file)
        if not sig_valid:
            validation_results['errors'].append(sig_msg)
            return validation_results
        validation_results['file_info']['signature_valid'] = True
        validation_results['detected_type'] = detected_type
        
        # 5. Check for potential issues
        if detected_type != validation_results['file_info']['extension']:
            validation_results['warnings'].append(
                f"File extension (.{validation_results['file_info']['extension']}) doesn't match detected file type ({detected_type})"
            )
        
        # 6. Generate file hash
        try:
            file_hash = self.generate_file_hash(file)
            validation_results['file_info']['file_hash'] = file_hash
            
            # Check for duplicates in session state
            if 'uploaded_files' in st.session_state:
                for existing_file in st.session_state.uploaded_files:
                    if existing_file.get('file_hash') == file_hash:
                        validation_results['warnings'].append(
                            "This file appears to be a duplicate of a previously uploaded file"
                        )
        except Exception as e:
            validation_results['warnings'].append(f"Could not generate file hash: {str(e)}")
        
        # If no errors, file is valid
        if not validation_results['errors']:
            validation_results['is_valid'] = True
        
        return validation_results

def enhanced_file_uploader(
    label: str = "Upload your resume",
    key: str = "file_upload",
    help_text: Optional[str] = None,
    show_validation_details: bool = True
) -> Optional[Any]:
    """
    Enhanced file uploader with comprehensive validation
    
    Args:
        label: Upload label text
        key: Unique key for the uploader
        help_text: Optional help text to display
        show_validation_details: Whether to show detailed validation results
    
    Returns:
        Uploaded file object if valid, None otherwise
    """
    validator = FileUploadValidator()
    
    # Display upload requirements
    if help_text:
        st.info(help_text)
    
    st.markdown("""
    **📋 Upload Requirements:**
    - **File Types:** PDF, DOCX, DOC
    - **Maximum Size:** 10MB
    - **Quality:** Clear, readable text
    """)
    
    # File uploader
    uploaded_file = st.file_uploader(
        label=label,
        type=list(validator.allowed_extensions),
        key=key,
        help="Select a resume file to upload and analyze"
    )
    
    if uploaded_file is not None:
        # Perform comprehensive validation
        validation_results = validator.comprehensive_validation(uploaded_file, uploaded_file.name)
        
        if show_validation_details:
            # Display validation results
            if validation_results['is_valid']:
                st.success("✅ File validation passed!")
                
                # Show file info
                with st.expander("📄 File Information", expanded=False):
                    file_info = validation_results['file_info']
                    st.json(file_info)
                
                # Show warnings if any
                if validation_results['warnings']:
                    for warning in validation_results['warnings']:
                        st.warning(f"⚠️ {warning}")
                
                return uploaded_file
            else:
                st.error("❌ File validation failed!")
                for error in validation_results['errors']:
                    st.error(f"• {error}")
                return None
        else:
            return uploaded_file if validation_results['is_valid'] else None
    
    return None

def track_uploaded_file(file, validation_results: Dict[str, Any]):
    """Track uploaded file in session state"""
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    file_record = {
        'filename': file.name,
        'upload_time': validation_results['file_info']['upload_time'],
        'file_hash': validation_results['file_info'].get('file_hash'),
        'detected_type': validation_results['detected_type'],
        'size': file.size
    }
    
    st.session_state.uploaded_files.append(file_record)

def get_file_upload_history() -> list:
    """Get history of uploaded files"""
    return st.session_state.get('uploaded_files', [])

def clear_file_upload_history():
    """Clear file upload history"""
    if 'uploaded_files' in st.session_state:
        st.session_state.uploaded_files = []
