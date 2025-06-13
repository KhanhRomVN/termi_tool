import os
from core.utils import print_colored, input_colored, custom_log

def delete_account_interactive(manager):
    """Interactive account deletion with improved feedback and logging"""
    custom_log("Starting delete account interactive", "INFO")
    print_colored("=== Delete Roboflow Account ===", "yellow")

    if not manager.accounts:
        custom_log("No accounts found to delete", "INFO")
        print_colored("No accounts to delete!", "red")
        input_colored("Press Enter to continue...", "grey")
        return

    # Show current accounts
    print_colored("\nAvailable accounts:", "yellow")
    accounts = list(manager.accounts.keys())
    for i, acc in enumerate(accounts, 1):
        if acc == manager.last_username:
            print_colored(f"[{i}] {acc} (current)", "cyan")
        else:
            print_colored(f"[{i}] {acc}", "cyan")
    print()

    # Get user choice
    while True:
        choice = input_colored("Select account number to delete (or 'b' to cancel): ", "magenta").strip().lower()
        
        if choice == 'b':
            custom_log("User cancelled account deletion", "INFO")
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(accounts):
                acc_to_delete = accounts[idx]
                
                # Additional confirmation for safety
                confirm = input_colored(f"\nAre you sure you want to delete account '{acc_to_delete}'? [y/N]: ", "yellow").strip().lower()
                
                if confirm == 'y':
                    # Handle current account status
                    if manager.last_username == acc_to_delete:
                        manager.last_username = None
                        custom_log(f"Removed {acc_to_delete} as current account", "INFO")
                    
                    # Delete the account
                    del manager.accounts[acc_to_delete]
                    manager._save_accounts()
                    
                    custom_log(f"Successfully deleted account: {acc_to_delete}", "INFO")
                    print_colored(f"\n✅ Account {acc_to_delete} deleted successfully!", "green")
                    
                    # If there are remaining accounts and no current account is set
                    if manager.accounts and manager.last_username is None:
                        remaining = list(manager.accounts.keys())[0]
                        confirm_new = input_colored(f"\nSet {remaining} as current account? [y/N]: ", "yellow").strip().lower()
                        if confirm_new == 'y':
                            manager.last_username = remaining
                            manager._save_accounts()
                            print_colored(f"✅ {remaining} is now the current account", "green")
                            custom_log(f"Set {remaining} as new current account", "INFO")
                else:
                    custom_log("User cancelled account deletion at confirmation", "INFO")
                    print_colored("\nDeletion cancelled.", "yellow")
                
                break
            else:
                custom_log(f"Invalid account index selected: {choice}", "ERROR")
                print_colored("Invalid account number!", "red")
        except ValueError:
            custom_log(f"Invalid input received: {choice}", "ERROR")
            print_colored("Please enter a valid number!", "red")

    input_colored("\nPress Enter to continue...", "grey")
