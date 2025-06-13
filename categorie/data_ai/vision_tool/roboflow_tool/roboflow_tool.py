import os
from core.utils import print_colored, input_colored, custom_log
from .upload_model.upload_model import RoboflowSessionManager, upload_model_workflow
from .add_account import add_account_interactive
from .delete_account import delete_account_interactive
from .switch_account import switch_account_interactive

try:
    import readchar
    from readchar import key
except ImportError:
    readchar = None
    key = None
    custom_log("readchar module not found - this will affect keyboard input", "ERROR")

def roboflow_tools_menu():
    import shutil
    import builtins
    history_stack = getattr(builtins, "history_stack", None)
    # Ensure Roboflow Tools is in the breadcrumb stack for accurate context
    if history_stack is not None and (not history_stack or history_stack[-1] != "Roboflow Tools"):
        history_stack.append("Roboflow Tools")

    def show_breadcrumb_local():
        if history_stack:
            crumb = " > ".join(history_stack)
            print_colored(crumb, "yellow")
            print()

    def print_accounts_table(manager):
        if not manager.accounts:
            custom_log("No Roboflow accounts found", "INFO")
            return
        header = "Index  Workspace              API Key"
        sep = "-" * 36
        print()
        print_colored("=== Roboflow Accounts ===", "yellow")
        print_colored(header, "green")
        print_colored(sep, "grey")
        for idx, username in enumerate(manager.accounts.keys(), 1):
            acc = manager.accounts[username]
            api_key = acc['ROBOFLOW_API_KEY']
            if len(api_key) > 8:
                masked_api = api_key[:4] + '****' + api_key[-4:]
            else:
                masked_api = '*' * len(api_key)
            print_colored(f"{idx:<6} {username:<22} {masked_api:<22}", "cyan")
        print()

    # Initialize manager once at the start
    try:
        manager = RoboflowSessionManager()
        custom_log("RoboflowSessionManager initialized successfully", "INFO")
    except Exception as e:
        custom_log(f"Error initializing RoboflowSessionManager: {str(e)}", "ERROR")
        return

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        show_breadcrumb_local()
        print_accounts_table(manager)

        # If only one account and current is None or not valid, set it as current
        if len(manager.accounts) == 1:
            only_acc = list(manager.accounts.keys())[0]
            if not manager.last_username or manager.last_username not in manager.accounts:
                manager.last_username = only_acc
                custom_log(f"Auto-selected only account: {only_acc}", "INFO")
                manager._save_accounts()

        print_colored("=== Roboflow Tools ===", "yellow")
        print_colored("[1] Upload Model", "cyan")
        print_colored("[a] Add Account", "cyan")
        print_colored("[d] Delete Account", "cyan")
        print_colored("[s] Switch Account", "cyan")
        print_colored("-------------------------", "grey")
        print_colored("<   Back to previous menu", "magenta")
        
        # Get current account status
        cur = manager.last_username if manager.last_username else "None"
        if cur != "None":
            print_colored(f"Current Account: {cur}", "green")
        else:
            print_colored(f"Current Account: {cur}", "yellow")

        choice = None
        if readchar:
            try:
                c = readchar.readkey()
                custom_log(f"Key pressed: {c}", "INFO")
                if c in ("\x1b", key.ESC, key.LEFT):
                    custom_log("Exiting Roboflow Tools menu", "INFO")
                    return
                if c in ('b', 'B', '<'):
                    custom_log("Going back from Roboflow Tools menu", "INFO")
                    return
                choice = c.lower()
            except Exception as e:
                custom_log(f"Error reading key: {str(e)}", "ERROR")
                choice = None
        else:
            try:
                choice = input_colored("\nSelect option: ", "magenta").strip().lower()
                custom_log(f"Option selected: {choice}", "INFO")
                if choice in ('b', 'B', '<'):
                    custom_log("Going back from Roboflow Tools menu", "INFO")
                    return
            except Exception as e:
                custom_log(f"Error reading input: {str(e)}", "ERROR")
                choice = None

        if choice == "1":
            os.system('cls' if os.name == 'nt' else 'clear')
            show_breadcrumb_local()
            print_colored("=== Model Upload ===", "yellow")
            try:
                upload_model_workflow(manager)
            except Exception as e:
                print_colored(f"Upload failed: {e}", "red")
                input_colored("Press Enter to continue...", "grey")
        elif choice == "a":
            os.system('cls' if os.name == 'nt' else 'clear')
            show_breadcrumb_local()
            print_colored("Add Roboflow Account", "yellow")
            add_account_interactive(manager)
            # Reload manager after adding account
            manager = RoboflowSessionManager()
        elif choice == "d":
            os.system('cls' if os.name == 'nt' else 'clear')
            show_breadcrumb_local()
            delete_account_interactive(manager)
            # Reload manager after deleting account
            manager = RoboflowSessionManager()
        elif choice == "s":
            try:
                custom_log("Attempting to switch Roboflow account", "INFO")
                os.system('cls' if os.name == 'nt' else 'clear')
                show_breadcrumb_local()
                print_colored("Switch Roboflow Account", "yellow")
                switch_account_interactive(manager, print_colored, input_colored, show_breadcrumb_local)
                # Reload manager after switching account
                manager = RoboflowSessionManager()
                custom_log(f"Current account after switch: {manager.last_username}", "INFO")
            except Exception as e:
                custom_log(f"Error in switch account: {str(e)}", "ERROR")
                input_colored("Press Enter to continue...", "grey")
        else:
            print_colored("Invalid choice", "red")
            input_colored("Press Enter to continue...", "grey")