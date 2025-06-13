import os
import readchar
from readchar import key
from core.utils import custom_log

def log_message(msg: str):
    """Log only specific business logs to <project-root>/termi_tool/log.txt."""
    try:
        import re
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        log_dir = os.path.join(project_root, "termi_tool")
        log_path = os.path.join(log_dir, "log.txt")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        ansi_escape = re.compile(r'\x1b[^m]*m')
        log_entry = ansi_escape.sub('', msg)
        with open(log_path, "a", encoding="utf-8") as logf:
            logf.write(log_entry + "\n")
    except Exception:
        pass

def switch_account_interactive(manager, print_colored, input_colored, show_breadcrumb_local):
    custom_log("Starting switch account interactive", "INFO")
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        show_breadcrumb_local()
        accounts = list(manager.accounts.keys())
        if not accounts:
            custom_log("No Roboflow accounts available", "ERROR")
            print_colored("No Roboflow accounts available to switch.", "red")
            input_colored("Press Enter to continue...", "grey")
            return

        print_colored("Switch Roboflow Account", "yellow")
        print_colored("Select an account to switch:", "yellow")
        for idx, acc in enumerate(accounts, 1):
            print_colored(f"[{idx}] {acc}", "cyan")
        print_colored("[B] Cancel or press ESC to go back", "magenta")

        custom_log("Displaying account selection menu", "INFO")

        if readchar:
            try:
                c = readchar.readkey()
                custom_log(f"Key pressed in switch account: {c}", "INFO")
                if c in ("\x1b", key.ESC, key.LEFT):
                    custom_log("Exiting switch account", "INFO")
                    return
                if c in ('b', 'B', '<'):
                    custom_log("Cancelling switch account", "INFO")
                    return
                choice = c.lower()
            except Exception as e:
                custom_log(f"Error reading key in switch account: {str(e)}", "ERROR")
                return
        else:
            try:
                choice = input_colored("\nAccount number: ", "magenta").strip().lower()
                custom_log(f"Account selection input: {choice}", "INFO")
                if choice in ('b', 'B', '<'):
                    custom_log("Cancelling switch account", "INFO")
                    return
            except Exception as e:
                custom_log(f"Error reading input in switch account: {str(e)}", "ERROR")
                return

        try:
            sel_idx = int(choice) - 1
            if sel_idx < 0 or sel_idx >= len(accounts):
                custom_log(f"Invalid account selection: {choice}", "ERROR")
                print_colored("Invalid selection.", "red")
                input_colored("Press Enter to continue...", "grey")
                continue
            username = accounts[sel_idx]
            api_key = manager.accounts[username]['ROBOFLOW_API_KEY']

            if not api_key:
                custom_log(f"Empty API key for account: {username}", "ERROR")
                print_colored("API key is empty! Please edit account to add key.", "red")
                input_colored("Press Enter to continue...", "grey")
                continue

            try:
                custom_log(f"Attempting to login with account: {username}", "INFO")
                from roboflow import Roboflow
                rf = Roboflow(api_key=api_key)
                workspace = rf.workspace()
                print_colored(f"✅ Successfully logged in as: {workspace}", "green")
                manager.last_username = username
                manager._save_accounts()
                print_colored(f"Active account switched to: {username}", "green")
                custom_log(f"Successfully switched to account: {username} ({workspace})", "INFO")
            except Exception as e:
                custom_log(f"Login failed for account {username}: {str(e)}", "ERROR")
                print_colored(f"⚠️ Login failed: {str(e)}", "red")
            input_colored("Press Enter to continue...", "grey")
            return
        except ValueError:
            custom_log("Invalid input format for account selection", "ERROR")
            print_colored("Please enter a valid number or 'B' to cancel.", "red")
            input_colored("Press Enter to continue...", "grey")
            continue