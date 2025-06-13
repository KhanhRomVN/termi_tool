import os
from core.utils import clear_screen, get_valid_path
from .coco_to_yolo import convert_coco_to_yolo

def coco_to_yolo_menu():
    """Menu for COCO to YOLO dataset conversion"""
    while True:
        clear_screen()
        print("=== COCO to YOLO Dataset Conversion ===\n")
        print("This tool converts COCO format datasets to YOLO format.")
        print("\nRequired source dataset structure:")
        print("source_folder/")
        print("├── train/           (required)")
        print("│   ├── images/      (contains image files)")
        print("│   └── annotations.json")
        print("├── valid/           (optional)")
        print("│   ├── images/")
        print("│   └── annotations.json")
        print("└── test/            (optional)")
        print("    ├── images/")
        print("    └── annotations.json\n")
        
        # Get source path
        print("Enter the source dataset path (or 'q' to quit):")
        source_path = input().strip()
        if source_path.lower() == 'q':
            return
            
        # Get destination path
        print("\nEnter the destination path (or 'q' to quit):")
        dest_path = input().strip()
        if dest_path.lower() == 'q':
            return
            
        # Validate and convert paths to absolute
        source_path = get_valid_path(source_path)
        dest_path = get_valid_path(dest_path)
        
        if not source_path or not dest_path:
            print("\nInvalid path provided. Press Enter to try again...")
            input()
            continue
            
        # Perform conversion
        success = convert_coco_to_yolo(source_path, dest_path)
        
        if success:
            print("\nConversion completed successfully! Press Enter to continue...")
        else:
            print("\nConversion failed. Press Enter to try again...")
        input()
        return

def format_conversion_menu():
    """Main menu for dataset format conversion tools"""
    while True:
        clear_screen()
        print("=== Dataset Format Conversion Tools ===\n")
        print("1. COCO to YOLO Conversion")
        print("0. Back\n")
        
        choice = input("Enter your choice (0-1): ").strip()
        
        if choice == "1":
            coco_to_yolo_menu()
        elif choice == "0":
            return
        else:
            print("\nInvalid choice. Press Enter to continue...")
            input() 