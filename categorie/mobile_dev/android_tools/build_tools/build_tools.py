import os
import subprocess
from typing import Tuple, Optional
from pathlib import Path

class AndroidBuildTools:
    @staticmethod
    def generate_aab(project_path: str, output_path: Optional[str] = None,
                    build_type: str = "release") -> Tuple[bool, str]:
        """
        Generate Android App Bundle (AAB) file
        
        Args:
            project_path (str): Path to Android project root
            output_path (str, optional): Custom output path for AAB file
            build_type (str): Build type (debug/release)
            
        Returns:
            Tuple[bool, str]: Success status and output path or error message
        """
        try:
            # Verify project path exists
            if not os.path.exists(project_path):
                return False, f"Project path does not exist: {project_path}"
            
            # Check if gradlew exists
            gradlew = os.path.join(project_path, 
                                 "gradlew.bat" if os.name == "nt" else "gradlew")
            if not os.path.exists(gradlew):
                return False, f"Gradle wrapper not found in {project_path}"
            
            # Make gradlew executable on Unix-like systems
            if os.name != "nt":
                os.chmod(gradlew, 0o755)
            
            # Build the command
            cmd = [gradlew]
            if build_type == "release":
                cmd.append("bundleRelease")
            else:
                cmd.append("bundleDebug")
            
            # Run the build command
            print(f"\nBuilding {build_type} AAB...")
            result = subprocess.run(cmd, cwd=project_path, 
                                 capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, f"Build failed:\n{result.stderr}"
            
            # Find generated AAB file
            app_dir = os.path.join(project_path, "app", "build", "outputs", "bundle", build_type)
            aab_files = list(Path(app_dir).glob("*.aab"))
            
            if not aab_files:
                return False, "AAB file not found after build"
            
            aab_path = str(aab_files[0])
            
            # Move to custom output path if specified
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                os.replace(aab_path, output_path)
                aab_path = output_path
            
            return True, f"AAB generated successfully at: {aab_path}"
            
        except Exception as e:
            return False, f"Error generating AAB: {str(e)}"

    @staticmethod
    def clean_project(project_path: str) -> Tuple[bool, str]:
        """
        Clean Android project build files
        
        Args:
            project_path (str): Path to Android project root
            
        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            gradlew = os.path.join(project_path, 
                                 "gradlew.bat" if os.name == "nt" else "gradlew")
            
            if not os.path.exists(gradlew):
                return False, f"Gradle wrapper not found in {project_path}"
            
            # Make gradlew executable on Unix-like systems
            if os.name != "nt":
                os.chmod(gradlew, 0o755)
            
            # Run clean command
            result = subprocess.run([gradlew, "clean"], 
                                 cwd=project_path,
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "Project cleaned successfully"
            else:
                return False, f"Clean failed:\n{result.stderr}"
                
        except Exception as e:
            return False, f"Error cleaning project: {str(e)}"

def main():
    """CLI interface for Android build tools"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Android Build Tools")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Generate AAB command
    aab_parser = subparsers.add_parser("aab", help="Generate Android App Bundle")
    aab_parser.add_argument("project_path", help="Path to Android project root")
    aab_parser.add_argument("--output", help="Custom output path for AAB file")
    aab_parser.add_argument("--type", choices=["debug", "release"],
                          default="release", help="Build type (default: release)")
    
    # Clean project command
    clean_parser = subparsers.add_parser("clean", help="Clean project build files")
    clean_parser.add_argument("project_path", help="Path to Android project root")
    
    args = parser.parse_args()
    
    if args.command == "aab":
        success, message = AndroidBuildTools.generate_aab(
            args.project_path, args.output, args.type)
        print(message)
        
    elif args.command == "clean":
        success, message = AndroidBuildTools.clean_project(args.project_path)
        print(message)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 