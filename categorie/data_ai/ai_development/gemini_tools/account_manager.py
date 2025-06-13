import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class GeminiAccountManager:
    def __init__(self):
        self.config_dir = Path.home() / '.termi_tool' / 'gemini'
        self.config_file = self.config_dir / 'accounts.json'
        self._ensure_config_dir()
        self.accounts = self._load_accounts()
        self.current_account = self._load_current_account()

    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            self._save_accounts({})

    def _load_accounts(self) -> Dict:
        """Load accounts from config file"""
        try:
            return json.loads(self.config_file.read_text())
        except:
            return {}

    def _save_accounts(self, accounts: Dict):
        """Save accounts to config file"""
        self.config_file.write_text(json.dumps(accounts, indent=2))

    def _load_current_account(self) -> Optional[str]:
        """Load current account from config"""
        current_file = self.config_dir / 'current_account'
        return current_file.read_text().strip() if current_file.exists() else None

    def _save_current_account(self, email: str):
        """Save current account to config"""
        current_file = self.config_dir / 'current_account'
        current_file.write_text(email)

    def add_account(self, email: str, api_key: str) -> Tuple[bool, str]:
        """Add a new Gemini account"""
        try:
            if email in self.accounts:
                return False, "Account already exists"

            self.accounts[email] = {
                "api_key": api_key,
                "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self._save_accounts(self.accounts)

            # If this is the first account, set it as current
            if len(self.accounts) == 1:
                self._save_current_account(email)
                self.current_account = email

            return True, "Account added successfully"
        except Exception as e:
            return False, f"Error adding account: {str(e)}"

    def list_accounts(self) -> List[Dict]:
        """List all Gemini accounts"""
        accounts_list = []
        for email, data in self.accounts.items():
            accounts_list.append({
                "email": email,
                "added_at": data["added_at"],
                "is_current": email == self.current_account
            })
        return accounts_list

    def switch_account(self, email: str) -> Tuple[bool, str]:
        """Switch to a different account"""
        try:
            if email not in self.accounts:
                return False, "Account not found"

            self._save_current_account(email)
            self.current_account = email
            return True, "Successfully switched account"
        except Exception as e:
            return False, f"Error switching account: {str(e)}"

    def delete_account(self, email: str) -> Tuple[bool, str]:
        """Delete a Gemini account"""
        try:
            if email not in self.accounts:
                return False, "Account not found"

            del self.accounts[email]
            self._save_accounts(self.accounts)

            # If deleted account was current, switch to another account if available
            if email == self.current_account:
                if self.accounts:
                    new_current = next(iter(self.accounts.keys()))
                    self._save_current_account(new_current)
                    self.current_account = new_current
                else:
                    # No accounts left
                    if (self.config_dir / 'current_account').exists():
                        (self.config_dir / 'current_account').unlink()
                    self.current_account = None

            return True, "Account deleted successfully"
        except Exception as e:
            return False, f"Error deleting account: {str(e)}"

    def get_current_credentials(self) -> Optional[Tuple[str, str]]:
        """Get current account credentials"""
        if not self.current_account:
            return None
        account_data = self.accounts.get(self.current_account)
        if not account_data:
            return None
        return self.current_account, account_data["api_key"]

def main():
    """CLI interface for Gemini account management"""
    try:
        manager = GeminiAccountManager()
        
        # Get command from path
        path = os.environ.get('MENU_PATH', '').split('.')
        if not path:
            print("\nError: No menu path provided")
            return
            
        command = path[-1]
        
        if command == "1":  # Add Account
            print("\n=== Add Gemini Account ===\n")
            email = input("Enter Gmail: ").strip()
            api_key = input("Enter Gemini API Key: ").strip()
            
            if not email or not api_key:
                print("\nError: Both email and API key are required")
            else:
                success, message = manager.add_account(email, api_key)
                print(f"\n{message}")
                
        elif command == "3":  # Switch Account
            accounts = manager.list_accounts()
            if not accounts:
                print("\nNo accounts found")
            else:
                print("\nAvailable Accounts:")
                for i, acc in enumerate(accounts, 1):
                    current = "* " if acc["is_current"] else "  "
                    print(f"{i}. {current}{acc['email']}")
                    
                try:
                    idx = int(input("\nSelect account number: ").strip()) - 1
                    if 0 <= idx < len(accounts):
                        success, message = manager.switch_account(accounts[idx]["email"])
                        print(f"\n{message}")
                    else:
                        print("\nInvalid selection")
                except ValueError:
                    print("\nInvalid input")
                    
        elif command == "4":  # Delete Account
            accounts = manager.list_accounts()
            if not accounts:
                print("\nNo accounts found")
            else:
                print("\nAvailable Accounts:")
                for i, acc in enumerate(accounts, 1):
                    current = "* " if acc["is_current"] else "  "
                    print(f"{i}. {current}{acc['email']}")
                    
                try:
                    idx = int(input("\nSelect account number to delete: ").strip()) - 1
                    if 0 <= idx < len(accounts):
                        confirm = input(f"\nAre you sure you want to delete {accounts[idx]['email']}? (y/N): ")
                        if confirm.lower() == 'y':
                            success, message = manager.delete_account(accounts[idx]["email"])
                            print(f"\n{message}")
                    else:
                        print("\nInvalid selection")
                except ValueError:
                    print("\nInvalid input")

    except Exception as e:
        print(f"\nError: {e}")
        
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 