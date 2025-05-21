import os
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
import shutil
import uuid


class GitHubService:
    """Service for interacting with GitHub repositories"""

    def __init__(self, base_dir: str = None):
        """Initialize the GitHub service

        Args:
            base_dir: Base directory for cloning repositories, defaults to 'uploads/github'
        """
        if base_dir is None:
            project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            base_dir = project_root / "uploads" / "github"

        self.base_dir = Path(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    async def clone_repository(self,
                               repo_url: str,
                               branch: str = "main",
                               depth: int = 1) -> Dict[str, Any]:
        """Clone a GitHub repository

        Args:
            repo_url: URL of the repository to clone
            branch: Branch to clone, defaults to "main"
            depth: Depth of the repository to clone, defaults to 1

        Returns:
            Dictionary with clone information
        """
        try:
            # Create unique ID and directory
            clone_id = str(uuid.uuid4())
            repo_dir = self.base_dir / clone_id

            # Ensure directory exists
            os.makedirs(repo_dir, exist_ok=True)

            # Run git clone command
            process = subprocess.run(
                ["git", "clone", "--branch", branch, "--depth", str(depth), repo_url, str(repo_dir)],
                capture_output=True,
                text=True
            )

            # Check for errors
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to clone repository: {process.stderr}",
                    "clone_id": clone_id
                }

            return {
                "success": True,
                "clone_id": clone_id,
                "repo_dir": str(repo_dir),
                "repo_url": repo_url,
                "branch": branch
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error cloning repository: {str(e)}",
                "clone_id": clone_id if 'clone_id' in locals() else None
            }

    def find_solidity_files(self, repo_dir: str, specific_path: Optional[str] = None) -> List[str]:
        """Find Solidity files in a repository

        Args:
            repo_dir: Path to the repository directory
            specific_path: Specific path within the repository to search

        Returns:
            List of paths to Solidity files
        """
        repo_path = Path(repo_dir)

        if not repo_path.exists():
            return []

        if specific_path:
            target_path = repo_path / specific_path
            if target_path.exists() and target_path.suffix == '.sol':
                return [str(target_path)]
            elif target_path.is_dir():
                return [str(f) for f in target_path.glob("**/*.sol")]
            else:
                return []
        else:
            # Find all Solidity files
            return [str(f) for f in repo_path.glob("**/*.sol")]

    def get_file_content(self, file_path: str) -> Dict[str, Any]:
        """Get the content of a file

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file content information
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }

            with open(path, 'r') as f:
                content = f.read()

            return {
                "success": True,
                "file_path": file_path,
                "file_name": path.name,
                "content": content
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}"
            }

    def cleanup_repository(self, clone_id: str) -> Dict[str, Any]:
        """Clean up a cloned repository

        Args:
            clone_id: ID of the cloned repository

        Returns:
            Dictionary with cleanup information
        """
        try:
            repo_dir = self.base_dir / clone_id

            if not repo_dir.exists():
                return {
                    "success": False,
                    "error": f"Repository not found: {clone_id}"
                }

            # Remove directory
            shutil.rmtree(repo_dir)

            return {
                "success": True,
                "message": f"Repository {clone_id} cleaned up successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error cleaning up repository: {str(e)}"
            }