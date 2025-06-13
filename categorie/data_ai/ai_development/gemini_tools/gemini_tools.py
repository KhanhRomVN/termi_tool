import os
import google.generativeai as genai
from typing import Optional, List, Tuple
import subprocess
from pathlib import Path
from .account_manager import GeminiAccountManager

class GeminiTools:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini tools
        
        Args:
            api_key (str, optional): Gemini API key
        """
        self.account_manager = GeminiAccountManager()
        
        # Try to get credentials from account manager if no API key provided
        if not api_key:
            credentials = self.account_manager.get_current_credentials()
            if credentials:
                self.current_email, api_key = credentials
            else:
                raise ValueError("No Gemini account configured. Please add an account first.")
                
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])

    def chat_with_ai(self, message: str) -> Tuple[bool, str]:
        """
        Chat with Gemini AI
        
        Args:
            message (str): User message
            
        Returns:
            Tuple[bool, str]: Success status and AI response
        """
        try:
            response = self.chat.send_message(message)
            return True, response.text
            
        except Exception as e:
            return False, f"Error in chat: {str(e)}"

    def generate_commit_message(self, diff: str) -> Tuple[bool, str]:
        """
        Generate a commit message using Gemini AI
        
        Args:
            diff (str): Git diff content
            
        Returns:
            Tuple[bool, str]: Success status and generated commit message
        """
        try:
            prompt = f"""Generate a concise and descriptive git commit message for the following changes:

{diff}

The commit message should:
1. Start with a type (feat, fix, docs, style, refactor, test, chore)
2. Be in the present tense
3. Be clear and specific
4. Not exceed 72 characters for the first line
5. Include a brief description after the first line if needed

Example format:
feat: add user authentication system

Implement JWT-based authentication with refresh tokens"""

            response = self.model.generate_content(prompt)
            return True, response.text
            
        except Exception as e:
            return False, f"Error generating commit message: {str(e)}"

    def get_git_diff(self) -> Tuple[bool, str]:
        """Get the current git diff"""
        try:
            result = subprocess.run(
                ["git", "diff", "--staged"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except Exception as e:
            return False, f"Error getting git diff: {str(e)}"

def main():
    """CLI interface for Gemini tools"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gemini AI Tools")
    parser.add_argument("--api-key", help="Gemini API key")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Chat with Gemini AI")
    chat_parser.add_argument("message", help="Message to send")
    
    # Commit message command
    commit_parser = subparsers.add_parser("commit", 
                                        help="Generate commit message for staged changes")
    
    args = parser.parse_args()
    
    try:
        tools = GeminiTools(args.api_key)
        
        if args.command == "chat":
            success, response = tools.chat_with_ai(args.message)
            if success:
                print("\nGemini AI:", response)
            else:
                print("Error:", response)
                
        elif args.command == "commit":
            # Get git diff
            success, diff = tools.get_git_diff()
            if not success:
                print("Error:", diff)
                return
                
            if not diff.strip():
                print("No staged changes found. Stage your changes with 'git add' first.")
                return
                
            # Generate commit message
            success, message = tools.generate_commit_message(diff)
            if success:
                print("\nGenerated Commit Message:")
                print("-" * 40)
                print(message)
                print("-" * 40)
                
                # Ask if user wants to commit with this message
                response = input("\nDo you want to commit with this message? (y/N): ")
                if response.lower() == 'y':
                    # Write message to temp file to preserve formatting
                    temp_file = Path("temp_commit_msg.txt")
                    temp_file.write_text(message)
                    
                    # Commit with the message
                    result = subprocess.run(
                        ["git", "commit", "-F", "temp_commit_msg.txt"],
                        capture_output=True,
                        text=True
                    )
                    
                    # Clean up temp file
                    temp_file.unlink()
                    
                    if result.returncode == 0:
                        print("\nChanges committed successfully!")
                    else:
                        print("\nError committing changes:", result.stderr)
            else:
                print("Error:", message)
                
        else:
            parser.print_help()
            
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Set the GEMINI_API_KEY environment variable or pass it with --api-key")

if __name__ == "__main__":
    main() 