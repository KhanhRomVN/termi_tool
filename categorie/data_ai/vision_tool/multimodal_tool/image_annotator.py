import os
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import google.generativeai as genai
from PIL import Image
import jsonlines
import sys

# Add parent directory to sys.path to allow imports from sibling directories
parent_dir = str(Path(__file__).resolve().parents[4])
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from categorie.data_ai.ai_development.gemini_tools.account_manager import GeminiAccountManager

class MultimodalAnnotator:
    def __init__(self):
        self.account_manager = GeminiAccountManager()
        self.current_model = None
        self.current_email = None
        self._setup_initial_model()

    def _setup_initial_model(self):
        """Setup initial Gemini model with first available account"""
        print("\n🔍 Setting up initial model...")
        credentials = self.account_manager.get_current_credentials()
        if not credentials:
            print("❌ No credentials found!")
            raise ValueError("No Gemini accounts configured. Please add an account first.")
        print(f"✅ Found credentials for account: {credentials[0]}")
        self._switch_to_account(*credentials)

    def _switch_to_account(self, email: str, api_key: str):
        """Switch to a different Gemini account"""
        try:
            print(f"\n🔄 Configuring API with key: {api_key[:4]}...{api_key[-4:]}")
            genai.configure(api_key=api_key)
            
            print(f"🚀 Initializing model 'gemini-2.0-flash' with account: {email}")
            model = genai.GenerativeModel('gemini-2.0-flash')
            print(f"📝 Model type: {type(model)}")
            print(f"📋 Available model methods: {dir(model)}")
            
            self.current_model = model
            self.current_email = email
            print(f"✅ Successfully initialized model with account: {email}")
        except Exception as e:
            print(f"❌ Failed to initialize model with account {email}")
            print(f"🔍 Error type: {type(e)}")
            print(f"🔍 Error details: {str(e)}")
            raise

    def _get_next_account(self) -> Optional[Tuple[str, str]]:
        """Get next available account when current one hits RPM limit"""
        accounts = self.account_manager.list_accounts()
        if not accounts:
            return None

        # Find current account index
        current_idx = -1
        for i, acc in enumerate(accounts):
            if acc['email'] == self.current_email:
                current_idx = i
                break

        # Try next account
        next_idx = (current_idx + 1) % len(accounts)
        next_email = accounts[next_idx]['email']
        account_data = self.account_manager.accounts.get(next_email)
        if account_data:
            return next_email, account_data['api_key']
        return None

    def _generate_context_prompt(self, context: str) -> str:
        """Generate context prompt for image analysis"""
        return f"""Analyze this image in the context of: {context}

Your task is to generate a comprehensive list of prefix-suffix pairs that describe different aspects of the image in great detail.
Each pair should focus on a specific element or feature of the image.

Guidelines for generating pairs:
1. Create at least 15-20 pairs
2. Each prefix should identify a specific element
3. Each suffix should provide detailed description about that element
4. Cover various aspects:
   - Overall layout and structure
   - Specific UI elements and their positions
   - Text content and language
   - Colors and visual design
   - Interactive elements
   - Spatial relationships between elements
   - State of UI elements (active, hover, selected)
   - Any unique or notable features
5. Be as specific and detailed as possible
6. Use technical terms when appropriate
7. Include measurements or proportions when relevant
8. Describe both major and minor details

Format your response as a JSON array of objects, each with "prefix" and "suffix" keys.
Example format:
[
  {{"prefix": "The main navigation bar", "suffix": "spans the full width of the screen, featuring a dark blue (#1877F2) background with white text and includes Home, Pages, and Groups icons aligned to the left"}},
  {{"prefix": "The profile section", "suffix": "occupies approximately 20% of the viewport width on the left side, displaying the user's profile picture, name, and customizable navigation options"}}
]

Ensure each prefix-suffix pair is unique and provides valuable information about the image."""

    def _analyze_image(self, image_path: str, context: str) -> List[Dict[str, str]]:
        """Analyze image using Gemini Vision API with automatic account rotation"""
        try:
            print(f"\n📁 Loading image from: {image_path}")
            # Load and encode image
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            print(f"✅ Successfully loaded image, size: {len(image_bytes)} bytes")
            
            # Get all available accounts first
            print("\n🔍 Fetching available accounts...")
            all_accounts = self.account_manager.list_accounts()
            if not all_accounts:
                print("❌ No accounts available.")
                return []
            print(f"✅ Found {len(all_accounts)} accounts")

            # Try with each account until success or all accounts exhausted
            tried_accounts = set()
            current_account = self.current_email
            print(f"\n🚀 Starting with account: {current_account}")
            
            while len(tried_accounts) < len(all_accounts):
                if current_account not in tried_accounts:
                    tried_accounts.add(current_account)
                    account_data = self.account_manager.accounts.get(current_account)
                    
                    if account_data:
                        print(f"\n🔄 Trying with account: {current_account}")
                        try:
                            # Configure API with current account
                            api_key = account_data["api_key"]
                            print(f"🔑 Configuring API with key: {api_key[:4]}...{api_key[-4:]}")
                            genai.configure(api_key=api_key)
                            
                            print("🎯 Creating model instance: gemini-2.0-flash")
                            model = genai.GenerativeModel('gemini-2.0-flash',
                                generation_config={
                                    "temperature": 0.7,  # Increased for more creative descriptions
                                    "top_p": 0.9,       # Increased for more diverse output
                                    "top_k": 40,
                                    "max_output_tokens": 2048  # Increased for longer responses
                                })
                            print(f"📝 Model type: {type(model)}")
                            
                            # Generate response
                            print("\n📤 Sending request to API...")
                            context_prompt = self._generate_context_prompt(context)
                            print(f"📋 Context prompt length: {len(context_prompt)}")
                            print(f"📋 Image data length: {len(image_bytes)}")
                            
                            response = model.generate_content(
                                [
                                    context_prompt,
                                    {"mime_type": "image/jpeg", "data": image_bytes}
                                ]
                            )
                            print("\n📥 Received response from API")
                            print(f"📝 Response type: {type(response)}")
                            
                            # Parse response
                            if hasattr(response, 'text'):
                                response_text = response.text
                                print(f"\n📝 Full response text:\n{response_text}\n")
                                
                                # Clean up response text
                                if response_text.startswith('```json'):
                                    response_text = response_text[7:]
                                if response_text.endswith('```'):
                                    response_text = response_text[:-3]
                                response_text = response_text.strip()
                                
                                try:
                                    result = json.loads(response_text)
                                    if isinstance(result, list):
                                        print(f"✅ Success with account: {current_account}")
                                        print(f"📊 Generated {len(result)} annotations")
                                        return result
                                    else:
                                        print(f"⚠️ Response is not a list: {type(result)}")
                                except json.JSONDecodeError as je:
                                    print(f"⚠️ JSON parsing error: {str(je)}")
                                    print(f"⚠️ Problematic text: {response_text}")
                            else:
                                print("⚠️ Response has no 'text' attribute")
                            
                            print(f"⚠️ Invalid response format from account: {current_account}")
                            
                        except Exception as e:
                            error_str = str(e).lower()
                            print(f"⚠️ Error with account {current_account}")
                            print(f"🔍 Error type: {type(e)}")
                            print(f"🔍 Error details: {error_str}")
                            
                            if not any(keyword in error_str for keyword in ["quota", "rate", "limit"]):
                                print(f"❌ Permanent error with account {current_account}, skipping...")
                    
                    # Get next account in rotation
                    accounts_list = [acc["email"] for acc in all_accounts]
                    current_idx = accounts_list.index(current_account)
                    next_idx = (current_idx + 1) % len(accounts_list)
                    current_account = accounts_list[next_idx]
                    print(f"\n⏳ Waiting before trying next account: {current_account}")
                    time.sleep(1)
                
                else:
                    if len(tried_accounts) == len(all_accounts):
                        print("\n⚠️ All accounts tried once. Waiting before retry cycle...")
                        time.sleep(5)
                        tried_accounts.clear()
                        print("🔄 Starting new cycle...")
                    current_account = self.current_email
            
            print("\n❌ All accounts exhausted without success")
            return []

        except Exception as e:
            print(f"\n❌ Error loading image")
            print(f"🔍 Error type: {type(e)}")
            print(f"🔍 Error details: {str(e)}")
            return []

    def annotate_directory(self, image_dir: str, context: str):
        """Annotate all images in a directory"""
        image_dir = Path(image_dir)
        if not image_dir.exists() or not image_dir.is_dir():
            raise ValueError(f"Invalid directory: {image_dir}")

        # Get list of image files
        image_files = []
        for ext in ['.jpg', '.jpeg', '.png', '.gif']:
            image_files.extend(image_dir.glob(f'*{ext}'))
            image_files.extend(image_dir.glob(f'*{ext.upper()}'))

        if not image_files:
            raise ValueError(f"No image files found in {image_dir}")

        # Create output file
        output_file = image_dir / 'annotations.jsonl'
        total_images = len(image_files)

        print(f"\nStarting annotation of {total_images} images...")
        print(f"Context: {context}")

        with jsonlines.open(output_file, mode='w') as writer:
            for i, image_path in enumerate(image_files, 1):
                print(f"\n{'='*50}")
                print(f"Processing image {i}/{total_images}: {image_path.name}")
                print(f"{'='*50}")
                
                # Analyze image with account rotation
                annotations = self._analyze_image(str(image_path), context)
                
                # Write annotations
                for annotation in annotations:
                    writer.write({
                        "image": image_path.name,
                        "prefix": annotation["prefix"],
                        "suffix": annotation["suffix"]
                    })
                
                print(f"\nGenerated {len(annotations)} annotations for {image_path.name}")

        print(f"\nAnnotation complete! Results saved to: {output_file}")

def main():
    """CLI interface for multimodal annotation"""
    try:
        annotator = MultimodalAnnotator()
        
        print("\n=== Multimodal Annotation Tool ===")
        
        # Get image directory
        while True:
            image_dir = input("\nEnter path to image directory: ").strip()
            if os.path.isdir(image_dir):
                break
            print("Invalid directory path. Please try again.")

        # Get context
        context = input("\nEnter the context for annotation (e.g., 'Computer screen interface'): ").strip()
        
        # Start annotation
        annotator.annotate_directory(image_dir, context)

    except ValueError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 