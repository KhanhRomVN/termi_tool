from core.utils import clear_screen
from .format_conversion.menu import format_conversion_menu

def dataset_tools_menu():
    """Main menu for dataset tools"""
    while True:
        clear_screen()
        print("=== Dataset Tools ===\n")
        print("1. Format Conversion")
        print("0. Back\n")
        
        choice = input("Enter your choice (0-1): ").strip()
        
        if choice == "1":
            format_conversion_menu()
        elif choice == "0":
            return
        else:
            print("\nInvalid choice. Press Enter to continue...")
            input() 