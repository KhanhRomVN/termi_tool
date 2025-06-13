import subprocess
import re
from typing import List, Tuple, Optional

class ADBTools:
    @staticmethod
    def run_command(command: List[str]) -> Tuple[bool, str]:
        """Run an ADB command and return the result"""
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            return True, result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return False, str(e)

    @staticmethod
    def connect_wifi(ip: str, port: str = "5555") -> Tuple[bool, str]:
        """Connect to device via WiFi ADB"""
        success, output = ADBTools.run_command(["adb", "connect", f"{ip}:{port}"])
        return success, output

    @staticmethod
    def list_devices() -> Tuple[bool, List[dict]]:
        """List all connected ADB devices"""
        success, output = ADBTools.run_command(["adb", "devices", "-l"])
        if not success:
            return False, []

        devices = []
        lines = output.strip().split('\n')[1:]  # Skip first line (header)
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    device = {
                        'id': parts[0],
                        'state': parts[1],
                        'description': ' '.join(parts[2:]) if len(parts) > 2 else ''
                    }
                    devices.append(device)
        return True, devices

    @staticmethod
    def remove_device(device_id: str) -> Tuple[bool, str]:
        """Remove a device from ADB"""
        success, output = ADBTools.run_command(["adb", "disconnect", device_id])
        return success, output

    @staticmethod
    def uninstall_app(package_name: str, device_id: Optional[str] = None) -> Tuple[bool, str]:
        """Uninstall an app using its package name"""
        cmd = ["adb"]
        if device_id:
            cmd.extend(["-s", device_id])
        cmd.extend(["uninstall", package_name])
        success, output = ADBTools.run_command(cmd)
        return success, output

def main():
    """CLI interface for ADB tools"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ADB Management Tools")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Connect WiFi
    wifi_parser = subparsers.add_parser("connect", help="Connect via WiFi")
    wifi_parser.add_argument("ip", help="IP address of the device")
    wifi_parser.add_argument("--port", default="5555", help="Port (default: 5555)")
    
    # List devices
    subparsers.add_parser("list", help="List connected devices")
    
    # Remove device
    remove_parser = subparsers.add_parser("remove", help="Remove a device")
    remove_parser.add_argument("device_id", help="Device ID to remove")
    
    # Uninstall app
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall an app")
    uninstall_parser.add_argument("package", help="Package name to uninstall")
    uninstall_parser.add_argument("--device", help="Specific device ID")
    
    args = parser.parse_args()
    
    if args.command == "connect":
        success, output = ADBTools.connect_wifi(args.ip, args.port)
        print(output)
    
    elif args.command == "list":
        success, devices = ADBTools.list_devices()
        if success and devices:
            print("\nConnected devices:")
            for device in devices:
                print(f"\nDevice ID: {device['id']}")
                print(f"State: {device['state']}")
                if device['description']:
                    print(f"Description: {device['description']}")
        else:
            print("No devices connected")
    
    elif args.command == "remove":
        success, output = ADBTools.remove_device(args.device_id)
        print(output)
    
    elif args.command == "uninstall":
        success, output = ADBTools.uninstall_app(args.package, args.device)
        print(output)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 