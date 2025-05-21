import os
from pathlib import Path
from typing import Dict, Any, List
import shutil
import uuid
from fastapi import UploadFile


class FileUploadService:
    """Service for handling file uploads"""

    def __init__(self, upload_dir: str = None):
        """Initialize the file upload service

        Args:
            upload_dir: Directory for storing uploaded files, defaults to 'uploads/contracts'
        """
        if upload_dir is None:
            project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            upload_dir = project_root / "uploads" / "contracts"

        self.upload_dir = Path(upload_dir)
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_uploaded_file(self, file: UploadFile) -> Dict[str, Any]:
        """Save an uploaded file

        Args:
            file: Uploaded file

        Returns:
            Dictionary with file information
        """
        try:
            # Create unique ID and filename
            file_id = str(uuid.uuid4())
            safe_filename = self._sanitize_filename(file.filename)
            filename = f"{file_id}_{safe_filename}"
            file_path = self.upload_dir / filename

            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            return {
                "success": True,
                "file_id": file_id,
                "original_filename": file.filename,
                "saved_filename": filename,
                "file_path": str(file_path)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error saving file: {str(e)}"
            }

    def get_file_content(self, file_id: str) -> Dict[str, Any]:
        """Get the content of a file by ID

        Args:
            file_id: ID of the file

        Returns:
            Dictionary with file content information
        """
        try:
            # Find file by ID
            files = list(self.upload_dir.glob(f"{file_id}_*"))

            if not files:
                return {
                    "success": False,
                    "error": f"File not found: {file_id}"
                }

            file_path = files[0]

            with open(file_path, 'r') as f:
                content = f.read()

            return {
                "success": True,
                "file_id": file_id,
                "file_path": str(file_path),
                "file_name": file_path.name.replace(f"{file_id}_", ""),
                "content": content
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}"
            }

    def get_file_path(self, file_id: str) -> Dict[str, Any]:
        """Get the path of a file by ID

        Args:
            file_id: ID of the file

        Returns:
            Dictionary with file path information
        """
        try:
            # Find file by ID
            files = list(self.upload_dir.glob(f"{file_id}_*"))

            if not files:
                return {
                    "success": False,
                    "error": f"File not found: {file_id}"
                }

            file_path = files[0]

            return {
                "success": True,
                "file_id": file_id,
                "file_path": str(file_path),
                "file_name": file_path.name.replace(f"{file_id}_", "")
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting file path: {str(e)}"
            }

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Delete a file by ID

        Args:
            file_id: ID of the file

        Returns:
            Dictionary with deletion information
        """
        try:
            # Find file by ID
            files = list(self.upload_dir.glob(f"{file_id}_*"))

            if not files:
                return {
                    "success": False,
                    "error": f"File not found: {file_id}"
                }

            file_path = files[0]

            # Remove file
            os.remove(file_path)

            return {
                "success": True,
                "message": f"File {file_id} deleted successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error deleting file: {str(e)}"
            }

    def list_files(self) -> List[Dict[str, Any]]:
        """List all uploaded files

        Returns:
            List of dictionaries with file information
        """
        try:
            files = []

            for file_path in self.upload_dir.glob("*"):
                if file_path.is_file():
                    file_id = file_path.name.split("_")[0]
                    file_name = file_path.name.replace(f"{file_id}_", "")

                    files.append({
                        "file_id": file_id,
                        "file_name": file_name,
                        "file_path": str(file_path),
                        "size": file_path.stat().st_size
                    })

            return files

        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename to ensure it's safe to use

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Replace potentially problematic characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."

        return "".join(c if c in safe_chars else "_" for c in filename)