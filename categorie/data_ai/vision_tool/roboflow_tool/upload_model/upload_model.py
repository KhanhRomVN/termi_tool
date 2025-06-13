import os
import sys
import json
import datetime
from pathlib import Path
from core.utils import print_colored, input_colored, normalize_path, validate_model_path, custom_log

try:
    from roboflow import Roboflow
except ImportError:
    Roboflow = None

ROBOFLOW_KEYS = [
    ("ROBOFLOW_API_KEY", "Enter your Roboflow API KEY: ", "yellow"),
    ("ROBOFLOW_WORKSPACE", "Workspace slug: ", "cyan"),
]
ROBOFLOW_VERSION = "ROBOFLOW_VERSION_ID"
ENV_FILE = ".env"

# Define config directory in user's home
CONFIG_DIR = os.path.join(str(Path.home()), ".config", "termi_tool")
ACCOUNTS_FILE = os.path.join(CONFIG_DIR, "roboflow_accounts.json")

class RoboflowSessionManager:
    def __init__(self):
        self.accounts = {}
        self.last_username = None
        self._ensure_config_dir()
        self._load_accounts()

    def _ensure_config_dir(self):
        """Ensure the config directory exists"""
        try:
            os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)
            custom_log(f"Ensured config directory exists at: {CONFIG_DIR}", "INFO")
        except Exception as e:
            custom_log(f"Error creating config directory: {str(e)}", "ERROR")
            print_colored(f"Error creating config directory: {str(e)}", "red")

    def _load_accounts(self):
        try:
            # Load from config file in user's home
            if os.path.exists(ACCOUNTS_FILE):
                with open(ACCOUNTS_FILE, 'r') as f:
                    data = json.load(f)
                    self.accounts = data.get('accounts', {})
                    self.last_username = data.get('last_username')
                    if self.last_username:
                        # Set environment variables for current account
                        account = self.accounts.get(self.last_username)
                        if account:
                            os.environ["ROBOFLOW_API_KEY"] = account["ROBOFLOW_API_KEY"]
                            os.environ["ROBOFLOW_WORKSPACE"] = account["ROBOFLOW_WORKSPACE"]
                            custom_log(f"Loaded current account from config: {self.last_username}", "INFO")
                        
            if not self.accounts:
                custom_log("No existing accounts found", "INFO")
                
        except Exception as e:
            custom_log(f"Error loading accounts: {str(e)}", "ERROR")
            print_colored(f"Error loading accounts: {str(e)}", "red")

    def _save_accounts(self):
        try:
            # Ensure config directory exists
            self._ensure_config_dir()
            
            # Save to config file
            data = {
                'accounts': self.accounts,
                'last_username': self.last_username
            }
            
            # Save with restricted permissions (only user can read/write)
            with open(ACCOUNTS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            os.chmod(ACCOUNTS_FILE, 0o600)
            
            # Update environment variables for current account
            if self.last_username and self.last_username in self.accounts:
                account = self.accounts[self.last_username]
                os.environ["ROBOFLOW_API_KEY"] = account["ROBOFLOW_API_KEY"]
                os.environ["ROBOFLOW_WORKSPACE"] = account["ROBOFLOW_WORKSPACE"]
                custom_log(f"Saved current account {self.last_username} to config and environment", "INFO")
            else:
                # Clear environment variables if no account is selected
                os.environ.pop("ROBOFLOW_API_KEY", None)
                os.environ.pop("ROBOFLOW_WORKSPACE", None)
                custom_log("Cleared environment variables", "INFO")
        except Exception as e:
            custom_log(f"Error saving accounts: {str(e)}", "ERROR")
            print_colored(f"Error saving accounts: {str(e)}", "red")

def custom_log(message: str, level: str = "INFO", print_to_console: bool = False):
    """
    Log a message to the log file with timestamp and level.
    Args:
        message: The message to log
        level: Log level (INFO, ERROR, DEBUG, etc.)
        print_to_console: Whether to also print to console (default False)
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Write to log file
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_file = os.path.join(project_root, "log.txt")
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
        # Only print to console if explicitly requested
        if print_to_console:
            color = "yellow" if level == "INFO" else "red" if level == "ERROR" else "cyan"
            print_colored(log_entry.strip(), color)
            
    except Exception as e:
        print_colored(f"Logging failed: {str(e)}", "red")

def upload_model_workflow(manager: RoboflowSessionManager):
    try:
        custom_log("Starting upload model workflow", "INFO")
        custom_log("Step 1: Checking prerequisites", "INFO")
        
        if Roboflow is None:
            custom_log("Roboflow SDK not installed", "ERROR")
            print_colored("❌ Roboflow SDK not installed. Run: pip install roboflow>=1.0.1", "red")
            input_colored("Press Enter to continue...", "grey")
            return

        # Check for environment variables first
        api_key = os.environ.get("ROBOFLOW_API_KEY")
        workspace = os.environ.get("ROBOFLOW_WORKSPACE")
        
        custom_log(f"Step 2: Environment variables check - API KEY: {'Present' if api_key else 'Missing'}, WORKSPACE: {'Present' if workspace else 'Missing'}", "INFO")
        
        if not api_key or not workspace:
            custom_log("Missing required environment variables", "ERROR")
            print_colored("❌ No Roboflow account found in environment variables.", "red")
            print_colored("Please set ROBOFLOW_API_KEY and ROBOFLOW_WORKSPACE in your environment", "yellow")
            print_colored("Or use the Add Account option to add a new account", "yellow")
            input_colored("Press Enter to continue...", "grey")
            return

        if not manager.last_username or manager.last_username not in manager.accounts:
            custom_log("No active Roboflow account", "ERROR")
            print_colored("❌ No active Roboflow account selected.", "red")
            print_colored("Please add or select an account first!", "yellow")
            input_colored("Press Enter to continue...", "grey")
            return

        username = manager.last_username
        account = manager.accounts[username]
        api_key = account["ROBOFLOW_API_KEY"]
        workspace = account["ROBOFLOW_WORKSPACE"]
        
        custom_log(f"Step 3: Using account {username} with workspace {workspace}", "INFO")

        # Initialize Roboflow client
        custom_log("Step 4: Initializing Roboflow client", "INFO")
        print_colored("\nValidating Roboflow connection...", "cyan")
        
        try:
            rf = Roboflow(api_key=api_key)
            custom_log("Roboflow client initialized successfully", "INFO")
        except Exception as e:
            custom_log(f"Failed to initialize Roboflow client: {str(e)}", "ERROR")
            raise
        
        try:
            custom_log("Step 5: Connecting to workspace", "INFO")
            ws = rf.workspace(workspace)
            custom_log(f"Successfully connected to workspace: {workspace}", "INFO")
            print_colored("✅ Successfully connected to Roboflow!", "green")
        except Exception as e:
            custom_log(f"Failed to connect to workspace {workspace}: {str(e)}", "ERROR")
            raise
        
        # Get list of available projects
        custom_log("Step 6: Fetching projects list", "INFO")
        try:
            projects = ws.projects()
            custom_log(f"Raw projects data: {projects}", "INFO")
            
            # Clean up project names - remove workspace prefix
            cleaned_projects = []
            custom_log("Step 7: Cleaning project names", "INFO")
            for p in projects:
                custom_log(f"Processing project: {p}", "INFO")
                if '/' in p:
                    workspace_name, project_name = p.split('/')
                    cleaned_projects.append(project_name)
                    custom_log(f"Cleaned project name from {p} to {project_name}", "INFO")
                else:
                    cleaned_projects.append(p)
                    custom_log(f"Project name unchanged: {p}", "INFO")
            projects = cleaned_projects
            
            custom_log(f"Found {len(projects)} projects", "INFO")
            custom_log(f"Final projects list: {projects}", "INFO")
            
            if not projects:
                custom_log("No projects found in workspace", "ERROR")
                print_colored("❌ No projects found in workspace", "red")
                input_colored("Press Enter to continue...", "grey")
                return
                
            custom_log("Step 8: Displaying projects", "INFO")
            print_colored("\nAvailable projects in workspace:", "yellow")
            for idx, project_name in enumerate(projects, 1):
                print_colored(f"[{idx}] {project_name}", "cyan")
                custom_log(f"Displayed project {idx}: {project_name}", "INFO")
                
            # Get project selection
            custom_log("Step 9: Waiting for project selection", "INFO")
            project_id = None
            
            while project_id is None:
                # Clear screen and show projects list each time
                os.system('cls' if os.name == 'nt' else 'clear')
                print_colored("=== Model Upload ===\n", "yellow")
                print_colored("Available projects in workspace:", "yellow")
                for idx, project_name in enumerate(projects, 1):
                    print_colored(f"[{idx}] {project_name}", "cyan")
                    
                try:
                    project_choice = input_colored("\nSelect project number or enter project slug (or 'b' to go back): ", "cyan").strip()
                    custom_log(f"User input for project selection: {project_choice}", "INFO")
                    
                    if project_choice.lower() == 'b':
                        custom_log("User chose to go back", "INFO")
                        return
                        
                    if not project_choice:
                        custom_log("Empty project selection", "INFO")
                        continue
                        
                    # Try to get by index
                    if project_choice.isdigit():
                        idx = int(project_choice) - 1
                        custom_log(f"Attempting to get project by index {idx}", "INFO")
                        if 0 <= idx < len(projects):
                            project_id = projects[idx]
                            custom_log(f"Selected project by index: {project_id}", "INFO")
                        else:
                            custom_log(f"Invalid project index: {idx + 1}", "ERROR")
                            print_colored(f"❌ Invalid project number. Please enter 1-{len(projects)}", "red")
                            input_colored("Press Enter to try again...", "grey")
                    # Try as direct slug
                    else:
                        custom_log(f"Attempting to get project by slug: {project_choice}", "INFO")
                        # Verify project exists
                        if project_choice in projects:
                            project_id = project_choice
                            custom_log(f"Selected project by exact match: {project_id}", "INFO")
                        else:
                            # Try to get project to validate it exists
                            custom_log(f"Validating project slug: {project_choice}", "INFO")
                            project = ws.project(project_choice)
                            project_id = project_choice
                            custom_log(f"Selected project by validation: {project_id}", "INFO")
                except Exception as e:
                    error_msg = str(e)
                    custom_log(f"Invalid project selection: {error_msg}", "ERROR")
                    print_colored(f"❌ Invalid project selection: {error_msg}", "red")
                    input_colored("Press Enter to try again...", "grey")
            
            custom_log("Step 10: Getting version information", "INFO")
            # Get and validate version
            version_id = input_colored("\nEnter version ID of the dataset (required): ", "yellow").strip()
            custom_log(f"User input for version ID: {version_id}", "INFO")
            
            if not version_id:
                custom_log("Version ID is required but was empty", "ERROR")
                print_colored("❌ Version ID is required", "red")
                input_colored("Press Enter to continue...", "grey")
                return
                
            try:
                custom_log(f"Validating version {version_id} for project {project_id}", "INFO")
                project = ws.project(project_id)
                version = project.version(version_id)
                custom_log(f"Successfully validated version {version_id}", "INFO")
                print_colored(f"✅ Found version {version_id}", "green")
            except Exception as e:
                error_msg = str(e)
                custom_log(f"Failed to validate version: {error_msg}", "ERROR")
                raise Exception(f"Invalid version ID: {error_msg}")

            custom_log("Step 11: Getting model file path", "INFO")
            # Get model path
            model_path_input = input_colored("\nEnter path to .pt model file (abs/rel/~): ", "yellow").strip()
            custom_log(f"User input for model path: {model_path_input}", "INFO")
            
            if not validate_model_path(model_path_input):
                custom_log("Invalid model file path", "ERROR")
                print_colored("❌ Invalid file. Must be .pt & file exists!", "red")
                input_colored("Press Enter to continue...", "grey")
                return
                
            model_abs_path = normalize_path(model_path_input)
            custom_log(f"Normalized model path: {model_abs_path}", "INFO")
            
            # Double check file exists
            if not os.path.isfile(model_abs_path):
                custom_log(f"Model file not found: {model_abs_path}", "ERROR")
                print_colored(f"❌ File not found: {model_abs_path}", "red")
                input_colored("Press Enter to continue...", "grey")
                return

            custom_log("Step 12: Getting model type", "INFO")
            # Define supported model types with categories
            model_categories = {
                "Object Detection": [
                    'yolov5', 'yolov7', 'yolov8', 'yolov9',
                    'yolov10', 'yolov11', 'yolov12', 'yolonas',
                    'paligemma', 'paligemma2', 'florence-2', 'rfdetr'
                ],
                "Instance Segmentation": [
                    'yolov5-seg', 'yolov7-seg', 'yolov8-seg',
                    'yolov9-seg', 'yolov10-seg', 'yolov11-seg', 'yolov12-seg'
                ],
                "Semantic Segmentation": [
                    'yolov5-semantic', 'yolov7-semantic', 'yolov8-semantic',
                    'yolov9-semantic', 'yolov10-semantic', 'yolov11-semantic',
                    'yolov12-semantic'
                ]
            }
            
            # Flatten the model types for easy lookup
            supported_models = []
            for category_models in model_categories.values():
                supported_models.extend(category_models)
            
            # Display model type options in a formatted table with categories
            print_colored("\nSupported model types:", "yellow")
            print_colored("-" * 60, "grey")
            print_colored("| {:^4} | {:<40} | {:<12} |".format("No.", "Model Type", "Category"), "yellow")
            print_colored("-" * 60, "grey")
            
            idx = 1
            for category, models in model_categories.items():
                for model in models:
                    print_colored("| {:^4} | {:<40} | {:<12} |".format(idx, model, category.split()[0]), "cyan")
                    idx += 1
            
            print_colored("-" * 60, "grey")
            
            while True:
                model_choice = input_colored("\nSelect model type (number or name) [yolov8]: ", "cyan").strip() or "yolov8"
                
                if model_choice.isdigit():
                    idx = int(model_choice) - 1
                    if 0 <= idx < len(supported_models):
                        model_type = supported_models[idx]
                        break
                    else:
                        print_colored(f"❌ Invalid number. Please enter 1-{len(supported_models)}", "red")
                else:
                    if model_choice in supported_models:
                        model_type = model_choice
                        break
                    else:
                        print_colored("❌ Invalid model type. Please select from the list above.", "red")
            
            custom_log(f"Model type: {model_type}", "INFO")

            custom_log("Step 13: Confirming upload", "INFO")
            # Confirm upload
            print_colored("\nUpload Summary:", "yellow")
            print_colored(f"• Project: {project_id}", "cyan")
            print_colored(f"• Version: {version_id}", "cyan")
            print_colored(f"• Model Type: {model_type}", "cyan")
            print_colored(f"• File: {os.path.basename(model_abs_path)}", "cyan")
            
            confirm = input_colored("\nProceed with upload? [y/N]: ", "yellow").strip().lower()
            custom_log(f"User confirmation: {confirm}", "INFO")
            
            if confirm != 'y':
                custom_log("User cancelled upload", "INFO")
                return
                
            custom_log("Step 14: Starting model upload", "INFO")
            # Upload model
            print_colored(f"\nUploading model to {project_id}...", "cyan")
            custom_log(f"Starting model upload: {model_abs_path} to {project_id} version {version_id}", "INFO")
            
            # Get directory and filename
            model_dir = os.path.dirname(model_abs_path)
            model_file = os.path.basename(model_abs_path)
            
            custom_log(f"Model directory: {model_dir}", "INFO")
            custom_log(f"Model filename: {model_file}", "INFO")
            custom_log(f"Model type: {model_type}", "INFO")
            
            try:
                custom_log("Step 15: Deploying model", "INFO")
                # Deploy model
                version.deploy(
                    model_type=model_type,
                    model_path=model_dir,
                    filename=model_file
                )
                custom_log("Model upload completed", "INFO")
                print_colored("✅ Upload successful!", "green")
            except Exception as e:
                error_msg = str(e)
                custom_log(f"Upload failed: {error_msg}", "ERROR")
                
                # Check for common API errors
                if "Dataset is not of the correct type" in error_msg:
                    print_colored("\n❌ Upload failed: Project type mismatch", "red")
                    print_colored("\nPossible solutions:", "yellow")
                    print_colored("1. Ensure your Roboflow project is configured for the correct type:", "cyan")
                    print_colored("   • For YOLOv* models: Object Detection", "cyan")
                    print_colored("   • For YOLOv*-seg models: Instance Segmentation", "cyan")
                    print_colored("   • For YOLOv*-semantic models: Semantic Segmentation", "cyan")
                    print_colored("\nNote: Currently, Roboflow may have limited support for semantic segmentation.", "yellow")
                    print_colored("You might need to:", "yellow")
                    print_colored("1. Convert your semantic segmentation model to instance segmentation", "cyan")
                    print_colored("2. Or contact Roboflow support for semantic segmentation support", "cyan")
                elif "401" in error_msg and "Unauthorized" in error_msg:
                    print_colored("\n❌ Upload failed: Authentication error", "red")
                    print_colored("\nPossible solutions:", "yellow")
                    print_colored("1. Check if your API key is valid", "cyan")
                    print_colored("2. Use the 'Add Account' option to add a new API key", "cyan")
                    print_colored("3. Ensure you have permission to upload to this project", "cyan")
                else:
                    print_colored(f"\n❌ Upload failed: {error_msg}", "red")
                
                input_colored("\nPress Enter to continue...", "grey")
                return
                
        except Exception as e:
            error_msg = str(e)
            custom_log(f"Failed to process projects: {error_msg}", "ERROR")
            print_colored(f"❌ Error: {error_msg}", "red")
            input_colored("\nPress Enter to continue...", "grey")
            
    except Exception as e:
        error_msg = str(e)
        custom_log(f"Error in upload workflow: {error_msg}", "ERROR")
        print_colored(f"❌ Error: {error_msg}", "red")
        
    finally:
        custom_log("Upload workflow completed", "INFO")
        input_colored("\nPress Enter to continue...", "grey") 