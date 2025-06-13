import os
import subprocess
import platform
from typing import List, Dict, Tuple, Optional
import json
from pathlib import Path

class DevToolsInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.common_tools = {
            "git": {
                "windows": ["winget", "install", "--id", "Git.Git", "-e"],
                "linux": ["sudo", "apt-get", "install", "-y", "git"],
                "darwin": ["brew", "install", "git"]
            },
            "vscode": {
                "windows": ["winget", "install", "--id", "Microsoft.VisualStudioCode", "-e"],
                "linux": ["sudo", "snap", "install", "code", "--classic"],
                "darwin": ["brew", "install", "--cask", "visual-studio-code"]
            },
            "node": {
                "windows": ["winget", "install", "--id", "OpenJS.NodeJS", "-e"],
                "linux": ["sudo", "apt-get", "install", "-y", "nodejs", "npm"],
                "darwin": ["brew", "install", "node"]
            },
            "python": {
                "windows": ["winget", "install", "--id", "Python.Python.3.11", "-e"],
                "linux": ["sudo", "apt-get", "install", "-y", "python3", "python3-pip"],
                "darwin": ["brew", "install", "python"]
            },
            "docker": {
                "windows": ["winget", "install", "--id", "Docker.DockerDesktop", "-e"],
                "linux": [
                    "sudo", "apt-get", "install", "-y",
                    "docker.io", "docker-compose"
                ],
                "darwin": ["brew", "install", "--cask", "docker"]
            }
        }

    def check_package_manager(self) -> Tuple[bool, str]:
        """Check if the required package manager is installed"""
        try:
            if self.system == "windows":
                result = subprocess.run(["winget", "--version"], 
                                     capture_output=True, text=True)
                if result.returncode != 0:
                    return False, "winget is not installed"
            
            elif self.system == "linux":
                result = subprocess.run(["apt-get", "--version"], 
                                     capture_output=True, text=True)
                if result.returncode != 0:
                    return False, "apt-get is not installed"
            
            elif self.system == "darwin":
                result = subprocess.run(["brew", "--version"], 
                                     capture_output=True, text=True)
                if result.returncode != 0:
                    return False, "Homebrew is not installed"
            
            return True, "Package manager is available"
            
        except Exception as e:
            return False, f"Error checking package manager: {str(e)}"

    def install_tool(self, tool_name: str) -> Tuple[bool, str]:
        """
        Install a development tool
        
        Args:
            tool_name (str): Name of the tool to install
            
        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            if tool_name not in self.common_tools:
                return False, f"Tool {tool_name} is not supported"
            
            if self.system not in self.common_tools[tool_name]:
                return False, f"Tool {tool_name} is not supported on {self.system}"
            
            cmd = self.common_tools[tool_name][self.system]
            print(f"\nInstalling {tool_name}...")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, f"{tool_name} installed successfully"
            else:
                return False, f"Error installing {tool_name}: {result.stderr}"
                
        except Exception as e:
            return False, f"Error installing {tool_name}: {str(e)}"

    def install_multiple_tools(self, tools: List[str]) -> List[Dict]:
        """
        Install multiple development tools
        
        Args:
            tools (List[str]): List of tool names to install
            
        Returns:
            List[Dict]: Installation results for each tool
        """
        results = []
        for tool in tools:
            success, message = self.install_tool(tool)
            results.append({
                'tool': tool,
                'success': success,
                'message': message
            })
        return results

class AppManager:
    def __init__(self):
        self.system = platform.system().lower()

    def list_running_apps(self) -> Tuple[bool, List[Dict]]:
        """
        List all running applications
        
        Returns:
            Tuple[bool, List[Dict]]: Success status and list of running apps
        """
        try:
            if self.system == "windows":
                cmd = ["tasklist", "/FO", "CSV", "/NH"]
            else:
                cmd = ["ps", "aux"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, []
            
            apps = []
            lines = result.stdout.strip().split('\n')
            
            if self.system == "windows":
                for line in lines:
                    parts = line.strip('"').split('","')
                    if len(parts) >= 2:
                        apps.append({
                            'name': parts[0],
                            'pid': parts[1],
                            'memory': parts[4].rstrip('"')
                        })
            else:
                for line in lines[1:]:  # Skip header
                    parts = line.split()
                    if len(parts) >= 10:
                        apps.append({
                            'name': ' '.join(parts[10:]),
                            'pid': parts[1],
                            'cpu': parts[2],
                            'memory': parts[3]
                        })
            
            return True, apps
            
        except Exception as e:
            return False, f"Error listing apps: {str(e)}"

    def uninstall_app(self, app_name: str) -> Tuple[bool, str]:
        """
        Uninstall an application
        
        Args:
            app_name (str): Name of the application to uninstall
            
        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            if self.system == "windows":
                cmd = ["wmic", "product", "where", f"name='{app_name}'", 
                      "call", "uninstall", "/nointeractive"]
            elif self.system == "linux":
                cmd = ["sudo", "apt-get", "remove", "-y", app_name]
            else:
                cmd = ["brew", "uninstall", app_name]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, f"{app_name} uninstalled successfully"
            else:
                return False, f"Error uninstalling {app_name}: {result.stderr}"
                
        except Exception as e:
            return False, f"Error uninstalling app: {str(e)}"

def main():
    """CLI interface for developer tools installation and app management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Developer Tools and App Management")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Install tools command
    install_parser = subparsers.add_parser("install", 
                                         help="Install development tools")
    install_parser.add_argument("tools", nargs="+", 
                              help="Tools to install (git/vscode/node/python/docker)")
    
    # List running apps command
    subparsers.add_parser("list-apps", help="List running applications")
    
    # Uninstall app command
    uninstall_parser = subparsers.add_parser("uninstall", 
                                           help="Uninstall an application")
    uninstall_parser.add_argument("app_name", help="Name of the app to uninstall")
    
    args = parser.parse_args()
    
    if args.command == "install":
        installer = DevToolsInstaller()
        
        # Check package manager
        success, message = installer.check_package_manager()
        if not success:
            print(f"Error: {message}")
            return
        
        # Install tools
        results = installer.install_multiple_tools(args.tools)
        
        print("\nInstallation Results:")
        for result in results:
            status = "✓" if result['success'] else "✗"
            print(f"{status} {result['tool']}: {result['message']}")
    
    elif args.command == "list-apps":
        manager = AppManager()
        success, apps = manager.list_running_apps()
        
        if success and isinstance(apps, list):
            print("\nRunning Applications:")
            for app in apps:
                print(f"\nName: {app['name']}")
                print(f"PID: {app['pid']}")
                if 'cpu' in app:
                    print(f"CPU: {app['cpu']}%")
                print(f"Memory: {app['memory']}")
        else:
            print(f"Error: {apps}")
    
    elif args.command == "uninstall":
        manager = AppManager()
        success, message = manager.uninstall_app(args.app_name)
        print(message)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 