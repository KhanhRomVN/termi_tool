import sys
from core.menu import Menu
from queue import Queue
import builtins

def start():
    # Global log queue for the live log viewer everywhere
    builtins.log_queue = Queue()
    
    # Create menu instance
    menu = Menu()
    current_path = []
    
    while True:
        try:
            # Display menu
            menu.print_menu(current_path)
            
            # Get user input
            choice = menu.get_input()
            
            # Get current menu structure
            current_menu = menu.get_current_menu(current_path)
            
            # Handle navigation choices
            if choice == '0':
                print("\nExiting...\n")
                sys.exit(0)
            elif choice == 'b' and current_path:
                current_path.pop()
            elif choice == 'm':
                current_path = []
            # Handle valid menu choices
            elif menu.is_valid_choice(choice, current_menu):
                current_path.append(choice)
            else:
                print("\nInvalid choice! Please try again.")
                input("Press Enter to continue...")

        except Exception as e:
            print(f"\nMenu error: {e}")
            input("Press Enter to return to main menu...")

if __name__ == "__main__":
    try:
        start()
    except KeyboardInterrupt:
        print("\nExiting...\n")
        sys.exit(0)