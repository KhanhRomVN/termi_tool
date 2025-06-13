import os
import json
from pathlib import Path
from typing import Optional, List, Dict
import shutil
from tqdm import tqdm
import sys

class COCOtoYOLOConverter:
    def __init__(self):
        self.required_folders = ['train']
        self.optional_folders = ['valid', 'test']
        
    def validate_source_path(self, source_path: str) -> bool:
        """Validate if source path meets requirements for COCO dataset"""
        if not os.path.exists(source_path):
            print(f"Error: Source path '{source_path}' does not exist")
            return False
            
        # Check if train folder exists
        train_path = os.path.join(source_path, 'train')
        if not os.path.exists(train_path):
            print(f"Error: Required 'train' folder not found in {source_path}")
            return False
            
        # Validate structure for each folder
        for folder in [*self.required_folders, *self.optional_folders]:
            folder_path = os.path.join(source_path, folder)
            if os.path.exists(folder_path):
                # Check for annotations file (either _annotations.coco.json or annotations.json)
                annotations_file = None
                for fname in os.listdir(folder_path):
                    if fname.endswith('.coco.json') or fname == 'annotations.json':
                        annotations_file = os.path.join(folder_path, fname)
                        break
                
                if not annotations_file:
                    print(f"Error: No COCO annotations file found in {folder_path}")
                    return False
                    
                # Validate annotations file format
                try:
                    with open(annotations_file, 'r') as f:
                        data = json.load(f)
                        required_keys = ['images', 'annotations', 'categories']
                        if not all(key in data for key in required_keys):
                            print(f"Error: Invalid COCO format in {annotations_file}")
                            return False
                            
                        # Verify that the referenced images exist
                        image_files = {img['file_name'] for img in data['images']}
                        for img_file in image_files:
                            img_path = os.path.join(folder_path, img_file)
                            if not os.path.exists(img_path):
                                print(f"Error: Referenced image not found: {img_file}")
                                return False
                                
                except Exception as e:
                    print(f"Error reading annotations file: {str(e)}")
                    return False
                    
        return True
        
    def validate_destination_path(self, dest_path: str) -> bool:
        """Validate if destination path is valid"""
        try:
            dest_dir = Path(dest_path)
            if not dest_dir.exists():
                print(f"Creating destination directory: {dest_path}")
                os.makedirs(dest_path)
            return True
        except Exception as e:
            print(f"Error with destination path: {str(e)}")
            return False
            
    def convert_bbox_coco_to_yolo(self, bbox: List[float], img_width: int, img_height: int) -> List[float]:
        """Convert COCO bbox format to YOLO format"""
        # COCO: [x_min, y_min, width, height]
        # YOLO: [x_center, y_center, width, height] (normalized)
        x_min, y_min, width, height = bbox
        
        x_center = (x_min + width/2) / img_width
        y_center = (y_min + height/2) / img_height
        norm_width = width / img_width
        norm_height = height / img_height
        
        return [x_center, y_center, norm_width, norm_height]
        
    def convert_folder(self, source_folder: str, dest_folder: str, categories: Dict[int, int]) -> None:
        """Convert a single folder (train/valid/test) from COCO to YOLO format"""
        # Find annotations file
        annotations_file = None
        for fname in os.listdir(source_folder):
            if fname.endswith('.coco.json') or fname == 'annotations.json':
                annotations_file = os.path.join(source_folder, fname)
                break
                
        # Create destination structure
        dest_images = os.path.join(dest_folder, 'images')
        dest_labels = os.path.join(dest_folder, 'labels')
        os.makedirs(dest_images, exist_ok=True)
        os.makedirs(dest_labels, exist_ok=True)
        
        # Load annotations
        with open(annotations_file, 'r') as f:
            coco_data = json.load(f)
            
        # Create image id to annotations mapping
        img_to_anns = {}
        for ann in coco_data['annotations']:
            img_id = ann['image_id']
            if img_id not in img_to_anns:
                img_to_anns[img_id] = []
            img_to_anns[img_id].append(ann)
            
        # Process each image
        for img_info in tqdm(coco_data['images'], desc=f"Converting {os.path.basename(source_folder)}"):
            img_id = img_info['id']
            img_name = img_info['file_name']
            img_width = img_info['width']
            img_height = img_info['height']
            
            # Copy image
            src_img_path = os.path.join(source_folder, img_name)
            dst_img_path = os.path.join(dest_images, img_name)
            shutil.copy2(src_img_path, dst_img_path)
            
            # Create YOLO annotation
            label_name = os.path.splitext(img_name)[0] + '.txt'
            label_path = os.path.join(dest_labels, label_name)
            
            with open(label_path, 'w') as f:
                if img_id in img_to_anns:
                    for ann in img_to_anns[img_id]:
                        cat_id = categories[ann['category_id']]
                        bbox = self.convert_bbox_coco_to_yolo(ann['bbox'], img_width, img_height)
                        f.write(f"{cat_id} {' '.join([str(x) for x in bbox])}\n")
                        
    def convert(self, source_path: str, dest_path: str) -> bool:
        """Main conversion method"""
        print("Starting COCO to YOLO conversion...")
        
        # Validate paths
        if not self.validate_source_path(source_path):
            return False
        if not self.validate_destination_path(dest_path):
            return False
            
        # Create destination folder with timestamp
        dest_folder = os.path.join(dest_path, 'yolo_dataset')
        os.makedirs(dest_folder, exist_ok=True)
        
        # Find train annotations file
        train_annotations = None
        train_folder = os.path.join(source_path, 'train')
        for fname in os.listdir(train_folder):
            if fname.endswith('.coco.json') or fname == 'annotations.json':
                train_annotations = os.path.join(train_folder, fname)
                break
                
        # Load categories from train annotations
        with open(train_annotations, 'r') as f:
            coco_data = json.load(f)
            
        # Create category mapping
        categories = {cat['id']: idx for idx, cat in enumerate(coco_data['categories'])}
        
        # Save category names
        with open(os.path.join(dest_folder, 'classes.txt'), 'w') as f:
            for cat in sorted(coco_data['categories'], key=lambda x: categories[x['id']]):
                f.write(f"{cat['name']}\n")
                
        # Convert each folder
        for folder in self.required_folders + self.optional_folders:
            source_folder = os.path.join(source_path, folder)
            if os.path.exists(source_folder):
                dest_subfolder = os.path.join(dest_folder, folder)
                os.makedirs(dest_subfolder, exist_ok=True)
                self.convert_folder(source_folder, dest_subfolder, categories)
                
        print(f"\nConversion completed successfully!")
        print(f"Dataset saved to: {dest_folder}")
        return True

def convert_coco_to_yolo(source_path: str, dest_path: str) -> bool:
    """Entry point function for the conversion tool"""
    converter = COCOtoYOLOConverter()
    return converter.convert(source_path, dest_path) 