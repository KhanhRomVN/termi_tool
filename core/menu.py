import os
import platform
from typing import List, Dict, Optional
import datetime
import psutil

class Menu:
    def __init__(self):
        self.system = platform.system().lower()
        self.clear_command = 'cls' if self.system == 'windows' else 'clear'
        self.menus = {
            "1": {
                "title": "Data & AI Utilities",
                "items": {
                    "1": {
                        "title": "Vision Tool",
                        "items": {
                            "1": {
                                "title": "Roboflow Tools",
                                "items": {
                                    "1": "Upload Model",
                                    "2": "Add Account",
                                    "3": "Delete Account",
                                    "4": "Switch Account"
                                }
                            },
                            "2": {
                                "title": "Video Tools",
                                "items": {
                                    "1": "Video to Frames"
                                }
                            },
                            "3": {
                                "title": "Multimodal Tools",
                                "items": {
                                    "1": "Image Annotation"
                                }
                            }
                        }
                    },
                    "2": {
                        "title": "Dataset Tools",
                        "items": {
                            "1": {
                                "title": "Format Conversion",
                                "items": {
                                    "1": "COCO to YOLO"
                                }
                            }
                        }
                    },
                    "3": {
                        "title": "AI Development",
                        "items": {
                            "1": {
                                "title": "Hugging Face Tools",
                                "items": {
                                    "1": "Clone Model Repository",
                                    "2": "Model Management"
                                }
                            },
                            "2": {
                                "title": "Gemini AI Tools",
                                "items": {
                                    "1": "Chat CLI",
                                    "2": "Auto Git Commit Message",
                                    "3": {
                                        "title": "Account Management",
                                        "items": {
                                            "1": "Add Account",
                                            "3": "Switch Account",
                                            "4": "Delete Account"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "2": {
                "title": "Mobile Development",
                "items": {
                    "1": {
                        "title": "Android Tools",
                        "items": {
                            "1": {
                                "title": "ADB Management",
                                "items": {
                                    "1": "Connect ADB WiFi",
                                    "2": "List ADB Devices",
                                    "3": "Remove ADB Device",
                                    "4": "Uninstall App"
                                }
                            },
                            "2": {
                                "title": "Build Tools",
                                "items": {
                                    "1": "Generate AAB"
                                }
                            }
                        }
                    },
                    "2": {
                        "title": "Flutter Tools",
                        "items": {
                            "1": "Development Utils"
                        }
                    }
                }
            },
            "3": {
                "title": "System Tools",
                "items": {
                    "1": {
                        "title": "Performance Monitor",
                        "items": {
                            "1": "CPU Usage",
                            "2": "RAM Usage",
                            "3": "Storage Analysis",
                            "4": "Process List"
                        }
                    },
                    "2": {
                        "title": "Network Tools",
                        "items": {
                            "1": "Request Logger"
                        }
                    },
                    "3": {
                        "title": "SSH Management",
                        "items": {
                            "1": "Generate SSH Key",
                            "2": "View Public Key",
                            "3": "Remove SSH Key"
                        }
                    }
                }
            },
            "4": {
                "title": "Developer Setup",
                "items": {
                    "1": {
                        "title": "Environment Setup",
                        "items": {
                            "1": "Install Dev Tools"
                        }
                    },
                    "2": {
                        "title": "Application Management",
                        "items": {
                            "1": "View Running Apps",
                            "2": "Uninstall Apps"
                        }
                    }
                }
            }
        }

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system(self.clear_command)

    def get_system_info(self):
        """Get basic system information"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return {
            'cpu': cpu_percent,
            'memory': memory.percent,
            'disk': disk.percent,
            'platform': platform.system(),
            'python': platform.python_version(),
            'processor': platform.processor()
        }

    def print_header(self):
        """Print the application header with system information"""
        self.clear_screen()
        
        print("\n+---------------------------------------------------------------+")
        print("|                    TERMINAL TOOL DASHBOARD                    |")
        print("|                  'Infinite Function Toolkit'                  |")
        print("+---------------------------------------------------------------+\n")

    def print_menu(self, current_path: List[str] = None):
        """Print the menu based on current path"""
        self.print_header()
        
        if not current_path:
            self._print_main_menu()
        else:
            self._print_submenu(current_path)

    def _print_main_menu(self):
        """Print the main menu options"""
        print("+-------+----------------------------------+")
        print("| Index |              Title               |")
        print("+-------+----------------------------------+")
        print("|   1   | 📊 Data & AI Utilities           |")
        print("|   2   | 📱 Mobile Development            |")
        print("|   3   | ⚙️  System Tools                  |")
        print("|   4   | 🔧 Developer Setup               |")
        print("+-------+----------------------------------+")
        print("|   0   | 🚪 Exit                          |")
        print("+-------+----------------------------------+")

    def _print_submenu(self, path: List[str]):
        """Print submenu based on path"""
        current = self.menus
        title_path = []
        
        # Navigate to current menu level
        for p in path:
            if p in current:
                current = current[p]
                title_path.append(current.get("title", ""))
                if "items" in current:
                    current = current["items"]
            else:
                print(f"Invalid path: {'.'.join(path)}")
                return

        # Print current path
        print(f"📍 {' > '.join(['Main Menu'] + title_path):<59}")

        # Special handling for Gemini Account Management menu
        if len(path) == 4 and path[0] == "1" and path[1] == "3" and path[2] == "2" and path[3] == "3":
            try:
                # Import account manager
                from categorie.data_ai.ai_development.gemini_tools.account_manager import GeminiAccountManager
                manager = GeminiAccountManager()
                accounts = manager.list_accounts()
                
                if accounts:
                    print("\n=== Registered Gemini Accounts ===")
                    print("+-------+----------------------------------+------------------+")
                    print("| Index |              Email               |     Status      |")
                    print("+-------+----------------------------------+------------------+")
                    for i, acc in enumerate(accounts, 1):
                        status = "🟢 Current" if acc["is_current"] else "⚪ Available"
                        email = acc["email"][:32]  # Truncate if too long
                        print(f"|   {i:<3} | {email:<32} | {status:<14} |")
                    print("+-------+----------------------------------+------------------+\n")
                else:
                    print("\n⚠️  No Gemini accounts registered yet.\n")
            except Exception as e:
                print(f"\n⚠️  Error loading accounts: {str(e)}\n")

        # Print menu items table
        print("+-------+----------------------------------+")
        print("| Index |              Title               |")
        print("+-------+----------------------------------+")
        
        # Print menu items
        for key, value in current.items():
            # Skip List Accounts option since we're showing the list automatically
            if len(path) == 4 and path[0] == "1" and path[1] == "3" and path[2] == "2" and path[3] == "3":
                if key == "2":  # Skip "List Accounts" option
                    continue
            title = value.get('title', value) if isinstance(value, dict) else value
            print(f"|   {key:<3} | {title:<32} |")

        # Print navigation options
        print("+-------+----------------------------------+")
        print("|   b   | ⬅️ Back                           |")
        print("|   m   | 🏠 Main Menu                     |")
        print("|   0   | 🚪 Exit                          |")
        print("+-------+----------------------------------+")

    def get_input(self) -> str:
        """Get user input"""
        return input("\nEnter your choice: ").strip().lower()

    def get_current_menu(self, path: List[str]) -> Dict:
        """Get the menu structure at the current path"""
        current = self.menus
        
        # Navigate to current menu level
        for p in path:
            if p in current:
                current = current[p]
                if "items" in current:
                    current = current["items"]
            else:
                return {}
                
        return current

    def is_valid_choice(self, choice: str, current_menu: Dict) -> bool:
        """Check if the input choice is valid for current menu"""
        if choice in ['0', 'b', 'm']:
            return True
        return choice in current_menu 