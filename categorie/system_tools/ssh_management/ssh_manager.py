import os
import subprocess
from pathlib import Path
from typing import Tuple, Optional

class SSHManager:
    def __init__(self):
        self.ssh_dir = os.path.expanduser("~/.ssh")
        os.makedirs(self.ssh_dir, exist_ok=True)
        os.chmod(self.ssh_dir, 0o700)  # Set correct permissions

    def generate_key(self, key_name: str, key_type: str = "ed25519", 
                    comment: Optional[str] = None) -> Tuple[bool, str]:
        """
        Generate a new SSH key
        
        Args:
            key_name (str): Name of the key file
            key_type (str): Type of key (rsa, ed25519, etc.)
            comment (str, optional): Comment/label for the key
        
        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            key_path = os.path.join(self.ssh_dir, key_name)
            
            # Check if key already exists
            if os.path.exists(key_path):
                return False, f"Key {key_name} already exists"
            
            # Build command
            cmd = ["ssh-keygen", "-t", key_type, "-f", key_path]
            if comment:
                cmd.extend(["-C", comment])
            cmd.extend(["-N", ""])  # Empty passphrase
            
            # Run command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Set correct permissions
                os.chmod(key_path, 0o600)
                os.chmod(f"{key_path}.pub", 0o644)
                return True, f"SSH key generated successfully at {key_path}"
            else:
                return False, f"Error generating key: {result.stderr}"
                
        except Exception as e:
            return False, f"Error: {str(e)}"

    def view_public_key(self, key_name: str) -> Tuple[bool, str]:
        """
        View the contents of a public key
        
        Args:
            key_name (str): Name of the key file
        
        Returns:
            Tuple[bool, str]: Success status and key content or error message
        """
        try:
            key_path = os.path.join(self.ssh_dir, f"{key_name}.pub")
            
            if not os.path.exists(key_path):
                return False, f"Public key {key_name}.pub not found"
            
            with open(key_path, 'r') as f:
                content = f.read().strip()
            
            return True, content
            
        except Exception as e:
            return False, f"Error reading public key: {str(e)}"

    def remove_key(self, key_name: str) -> Tuple[bool, str]:
        """
        Remove an SSH key pair
        
        Args:
            key_name (str): Name of the key file
        
        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            private_key = os.path.join(self.ssh_dir, key_name)
            public_key = f"{private_key}.pub"
            
            removed = []
            
            # Remove private key
            if os.path.exists(private_key):
                os.remove(private_key)
                removed.append("private key")
            
            # Remove public key
            if os.path.exists(public_key):
                os.remove(public_key)
                removed.append("public key")
            
            if removed:
                return True, f"Removed {' and '.join(removed)} for {key_name}"
            else:
                return False, f"No keys found for {key_name}"
                
        except Exception as e:
            return False, f"Error removing key: {str(e)}"

    def list_keys(self) -> Tuple[bool, list]:
        """
        List all SSH keys in the .ssh directory
        
        Returns:
            Tuple[bool, list]: Success status and list of key information
        """
        try:
            keys = []
            for file in os.listdir(self.ssh_dir):
                if file.endswith('.pub'):
                    key_name = file[:-4]  # Remove .pub extension
                    success, content = self.view_public_key(key_name)
                    if success:
                        key_type = content.split()[0]
                        comment = content.split()[2] if len(content.split()) > 2 else None
                        keys.append({
                            'name': key_name,
                            'type': key_type,
                            'comment': comment
                        })
            
            return True, keys
            
        except Exception as e:
            return False, f"Error listing keys: {str(e)}"

def main():
    """CLI interface for SSH key management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SSH Key Management Tools")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Generate key command
    gen_parser = subparsers.add_parser("generate", help="Generate new SSH key")
    gen_parser.add_argument("name", help="Name for the key file")
    gen_parser.add_argument("--type", default="ed25519", 
                          choices=["rsa", "ed25519", "ecdsa"],
                          help="Key type (default: ed25519)")
    gen_parser.add_argument("--comment", help="Comment/label for the key")
    
    # View public key command
    view_parser = subparsers.add_parser("view", help="View public key")
    view_parser.add_argument("name", help="Name of the key")
    
    # Remove key command
    remove_parser = subparsers.add_parser("remove", help="Remove SSH key pair")
    remove_parser.add_argument("name", help="Name of the key to remove")
    
    # List keys command
    subparsers.add_parser("list", help="List all SSH keys")
    
    args = parser.parse_args()
    manager = SSHManager()
    
    if args.command == "generate":
        success, message = manager.generate_key(args.name, args.type, args.comment)
        print(message)
        
    elif args.command == "view":
        success, content = manager.view_public_key(args.name)
        print(content if success else f"Error: {content}")
        
    elif args.command == "remove":
        success, message = manager.remove_key(args.name)
        print(message)
        
    elif args.command == "list":
        success, keys = manager.list_keys()
        if success:
            if keys:
                print("\nSSH Keys:")
                for key in keys:
                    print(f"\nName: {key['name']}")
                    print(f"Type: {key['type']}")
                    if key['comment']:
                        print(f"Comment: {key['comment']}")
            else:
                print("No SSH keys found")
        else:
            print(f"Error: {keys}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 