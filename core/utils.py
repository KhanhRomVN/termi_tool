from typing import List, Dict, Optional
import importlib
import os

def get_tool_module(path: List[str]) -> Optional[str]:
    """
    Get the module path for a tool based on the menu path
    
    Args:
        path (List[str]): Current menu path
        
    Returns:
        Optional[str]: Module path if found, None otherwise
    """
    # Map of menu paths to module paths
    tool_map = {
        # Data & AI Utilities
        "1.1.2.1": "categorie.data_ai.vision_tool.video_tool.video_to_frames",
        "1.2.1.1": "categorie.data_ai.dataset_tools.format_conversion.coco_to_yolo",
        "1.3.1.1": "categorie.data_ai.ai_development.huggingface_tools.huggingface_manager",
        "1.3.1.2": "categorie.data_ai.ai_development.huggingface_tools.huggingface_manager",
        "1.3.2.1": "categorie.data_ai.ai_development.gemini_tools.gemini_tools",
        "1.3.2.2": "categorie.data_ai.ai_development.gemini_tools.gemini_tools",
        
        # Mobile Development
        "2.1.1.1": "categorie.mobile_dev.android_tools.adb_management.adb_tools",
        "2.1.1.2": "categorie.mobile_dev.android_tools.adb_management.adb_tools",
        "2.1.1.3": "categorie.mobile_dev.android_tools.adb_management.adb_tools",
        "2.1.1.4": "categorie.mobile_dev.android_tools.adb_management.adb_tools",
        "2.1.2.1": "categorie.mobile_dev.android_tools.build_tools.build_tools",
        
        # System Tools
        "3.1.1": "categorie.system_tools.performance_monitor.system_monitor",
        "3.1.2": "categorie.system_tools.performance_monitor.system_monitor",
        "3.1.3": "categorie.system_tools.performance_monitor.system_monitor",
        "3.1.4": "categorie.system_tools.performance_monitor.system_monitor",
        "3.2.1": "categorie.system_tools.network_tools.request_logger",
        "3.3.1": "categorie.system_tools.ssh_management.ssh_manager",
        "3.3.2": "categorie.system_tools.ssh_management.ssh_manager",
        "3.3.3": "categorie.system_tools.ssh_management.ssh_manager",
        
        # Developer Setup
        "4.1.1": "categorie.dev_setup.env_setup.dev_tools_installer",
        "4.2.1": "categorie.dev_setup.env_setup.dev_tools_installer",
        "4.2.2": "categorie.dev_setup.env_setup.dev_tools_installer"
    }
    
    path_key = ".".join(path)
    return tool_map.get(path_key)

def execute_tool(path: List[str]) -> None:
    """
    Execute the tool based on the menu path
    
    Args:
        path (List[str]): Current menu path
    """
    module_path = get_tool_module(path)
    if not module_path:
        print("\n⚠️  This menu option doesn't have an associated tool yet.")
        input("\nPress Enter to continue...")
        return
        
    try:
        # Import the module
        module = importlib.import_module(module_path)
        
        # Execute the main function if it exists
        if hasattr(module, 'main'):
            module.main()
        else:
            print("\n⚠️  Tool implementation not found.")
        
        input("\nPress Enter to continue...")
    except ImportError as e:
        print(f"\n❌ Error loading tool: {e}")
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"\n❌ Error executing tool: {e}")
        input("\nPress Enter to continue...") 