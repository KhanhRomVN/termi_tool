import os
import subprocess
from typing import Optional, Tuple, List
import requests
from huggingface_hub import HfApi, Repository
from pathlib import Path

class HuggingFaceManager:
    def __init__(self, token: Optional[str] = None):
        """
        Initialize HuggingFace manager
        
        Args:
            token (str, optional): HuggingFace API token
        """
        self.token = token or os.getenv("HF_TOKEN")
        self.api = HfApi(token=self.token)

    def clone_repository(self, repo_id: str, local_dir: str, 
                        branch: Optional[str] = None) -> Tuple[bool, str]:
        """
        Clone a model repository from HuggingFace
        
        Args:
            repo_id (str): Repository ID (e.g., 'username/model-name')
            local_dir (str): Local directory to clone to
            branch (str, optional): Branch to clone
            
        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            repo = Repository(
                local_dir=local_dir,
                clone_from=repo_id,
                token=self.token,
                git_user="HF CLI",
                revision=branch
            )
            
            print(f"Cloning repository {repo_id}...")
            repo.git_pull()
            
            return True, f"Successfully cloned {repo_id} to {local_dir}"
            
        except Exception as e:
            return False, f"Error cloning repository: {str(e)}"

    def list_models(self, author: Optional[str] = None, 
                   search: Optional[str] = None, 
                   task: Optional[str] = None) -> Tuple[bool, List[dict]]:
        """
        List models from HuggingFace
        
        Args:
            author (str, optional): Filter by author
            search (str, optional): Search term
            task (str, optional): Filter by task
            
        Returns:
            Tuple[bool, List[dict]]: Success status and list of models
        """
        try:
            models = self.api.list_models(
                author=author,
                search=search,
                filter=task
            )
            
            model_list = []
            for model in models:
                model_info = {
                    'id': model.modelId,
                    'downloads': model.downloads,
                    'likes': model.likes,
                    'task': model.pipeline_tag,
                    'tags': model.tags,
                    'last_modified': model.lastModified
                }
                model_list.append(model_info)
            
            return True, model_list
            
        except Exception as e:
            return False, f"Error listing models: {str(e)}"

    def get_model_info(self, repo_id: str) -> Tuple[bool, dict]:
        """
        Get detailed information about a model
        
        Args:
            repo_id (str): Repository ID
            
        Returns:
            Tuple[bool, dict]: Success status and model information
        """
        try:
            model_info = self.api.model_info(repo_id)
            
            info = {
                'id': model_info.modelId,
                'author': model_info.author,
                'downloads': model_info.downloads,
                'likes': model_info.likes,
                'task': model_info.pipeline_tag,
                'tags': model_info.tags,
                'last_modified': model_info.lastModified,
                'description': model_info.description
            }
            
            return True, info
            
        except Exception as e:
            return False, f"Error getting model info: {str(e)}"

def main():
    """CLI interface for HuggingFace tools"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HuggingFace Model Management Tools")
    parser.add_argument("--token", help="HuggingFace API token")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Clone repository command
    clone_parser = subparsers.add_parser("clone", help="Clone a model repository")
    clone_parser.add_argument("repo_id", help="Repository ID (e.g., 'username/model-name')")
    clone_parser.add_argument("local_dir", help="Local directory to clone to")
    clone_parser.add_argument("--branch", help="Branch to clone")
    
    # List models command
    list_parser = subparsers.add_parser("list", help="List models")
    list_parser.add_argument("--author", help="Filter by author")
    list_parser.add_argument("--search", help="Search term")
    list_parser.add_argument("--task", help="Filter by task")
    
    # Get model info command
    info_parser = subparsers.add_parser("info", help="Get model information")
    info_parser.add_argument("repo_id", help="Repository ID")
    
    args = parser.parse_args()
    manager = HuggingFaceManager(args.token)
    
    if args.command == "clone":
        success, message = manager.clone_repository(args.repo_id, args.local_dir, args.branch)
        print(message)
        
    elif args.command == "list":
        success, models = manager.list_models(args.author, args.search, args.task)
        if success:
            print("\nFound Models:")
            for model in models:
                print(f"\nID: {model['id']}")
                print(f"Task: {model['task']}")
                print(f"Downloads: {model['downloads']}")
                print(f"Likes: {model['likes']}")
                if model['tags']:
                    print(f"Tags: {', '.join(model['tags'])}")
        else:
            print(f"Error: {models}")
            
    elif args.command == "info":
        success, info = manager.get_model_info(args.repo_id)
        if success:
            print("\nModel Information:")
            for key, value in info.items():
                if value:
                    print(f"{key.replace('_', ' ').title()}: {value}")
        else:
            print(f"Error: {info}")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 