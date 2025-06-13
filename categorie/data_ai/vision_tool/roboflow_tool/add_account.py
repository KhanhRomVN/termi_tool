import os
from core.utils import print_colored, input_colored, custom_log
from .upload_model.upload_model import ROBOFLOW_KEYS, ROBOFLOW_VERSION

def add_account_interactive(manager):
    custom_log("Starting add account interactive", "INFO")
    print_colored("=== Add Roboflow Account ===", "yellow")
    print_colored("Please provide your Roboflow workspace slug and API key.", "cyan")
    print_colored("You can find your API key at https://app.roboflow.com/settings?tab=api", "cyan")
    print()

    # Show current accounts if any exist
    if manager.accounts:
        print_colored("\nExisting accounts:", "yellow")
        for idx, acc in enumerate(manager.accounts.keys(), 1):
            print_colored(f"[{idx}] {acc}", "cyan")
        print()

    # Loop for workspace slug until valid or user cancels
    while True:
        workspace = input_colored("Workspace slug (or 'b' to cancel): ", "cyan").strip()
        if workspace.lower() == "b":
            custom_log("User cancelled workspace input", "INFO")
            return
        
        if not workspace:
            custom_log("Empty workspace input", "ERROR")
            print_colored("Workspace cannot be empty!", "red")
            print()
            continue
        custom_log(f"Workspace input received: {workspace}", "INFO")
        break

    # Loop for API key until valid or user cancels
    while True:
        api_key = input_colored("Roboflow API key (or 'b' to cancel): ", "yellow").strip()
        if api_key.lower() == "b":
            custom_log("User cancelled API key input", "INFO")
            return
            
        if not api_key:
            custom_log("Empty API key input", "ERROR")
            print_colored("API key cannot be empty!", "red")
            print()
            continue
        custom_log("API key input received", "INFO")
        break

    # Username will be the workspace slug for simplicity/uniqueness
    username = workspace
    if username in manager.accounts:
        custom_log(f"Workspace {username} already exists", "ERROR")
        print_colored("This workspace is already added!", "red")
        input_colored("Press Enter to continue...", "grey")
        return

    try:
        # Try to validate the API key by making a test connection
        from roboflow import Roboflow
        rf = Roboflow(api_key=api_key)
        ws = rf.workspace()
        custom_log(f"Successfully validated API key for workspace: {workspace}", "INFO")
        
        # Save to manager's accounts
        acc = {
            "ROBOFLOW_API_KEY": api_key,
            "ROBOFLOW_WORKSPACE": workspace
        }
        manager.accounts[username] = acc
        
        # Set as current account if it's the first one or if there's no current account
        if len(manager.accounts) == 1 or manager.last_username is None:
            manager.last_username = username
            custom_log(f"Set {username} as current account", "INFO")
        
        # Ask if user wants to make this the current account
        elif input_colored(f"\nMake {username} the current account? [y/N]: ", "yellow").strip().lower() == 'y':
            manager.last_username = username
            custom_log(f"Set {username} as current account", "INFO")
        
        # Save both the accounts list and current account
        manager._save_accounts()
        
        print_colored("✅ Account added successfully!", "green")
        if manager.last_username == username:
            print_colored(f"✅ {username} is now the current account", "green")
        custom_log(f"Account {username} added successfully (total accounts: {len(manager.accounts)})", "INFO")
        
    except Exception as e:
        custom_log(f"Failed to validate API key: {str(e)}", "ERROR")
        print_colored(f"⚠️ Error validating API key: {str(e)}", "red")
        print_colored("Account not added due to validation failure", "red")
        
    input_colored("Press Enter to continue...", "grey")