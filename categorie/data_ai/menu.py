from core.utils import clear_screen
from .vision_tool.roboflow_tool import roboflow_tool_menu
from .dataset_tools import dataset_tools_menu

def data_ai_menu():
    """Main menu for Data & AI tools"""
    while True:
        clear_screen()
        print("=== Data & AI Tools ===\n")
        print("1. Vision Tools")
        print("2. Dataset Tools")
        print("0. Back\n")
        
        choice = input("Enter your choice (0-2): ").strip()
        
        if choice == "1":
            roboflow_tool_menu()
        elif choice == "2":
            dataset_tools_menu()
        elif choice == "0":
            return
        else:
            print("\nInvalid choice. Press Enter to continue...")
            input() 