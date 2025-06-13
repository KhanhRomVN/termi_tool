import cv2
import os
from typing import Optional

def video_to_frames(video_path: str, output_dir: str, frame_interval: Optional[int] = 1) -> bool:
    """
    Convert a video file to individual frames
    
    Args:
        video_path (str): Path to the video file
        output_dir (str): Directory to save the frames
        frame_interval (int, optional): Interval between frames to save. Defaults to 1 (every frame)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Open the video file
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            print(f"Error: Could not open video file {video_path}")
            return False
        
        # Get video properties
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        
        print(f"Video properties:")
        print(f"Total frames: {total_frames}")
        print(f"FPS: {fps}")
        
        frame_count = 0
        saved_count = 0
        
        while True:
            success, frame = video.read()
            if not success:
                break
                
            if frame_count % frame_interval == 0:
                frame_filename = os.path.join(output_dir, f"frame_{saved_count:05d}.jpg")
                cv2.imwrite(frame_filename, frame)
                saved_count += 1
                
                # Print progress
                if saved_count % 100 == 0:
                    progress = (frame_count / total_frames) * 100
                    print(f"Progress: {progress:.1f}% ({saved_count} frames saved)")
            
            frame_count += 1
        
        video.release()
        print(f"\nCompleted! Saved {saved_count} frames to {output_dir}")
        return True
        
    except Exception as e:
        print(f"Error during video conversion: {str(e)}")
        return False

def main():
    """CLI interface for video to frames conversion"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert video to frames")
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("output_dir", help="Directory to save the frames")
    parser.add_argument("--interval", type=int, default=1, 
                      help="Save every nth frame (default: 1)")
    
    args = parser.parse_args()
    video_to_frames(args.video_path, args.output_dir, args.interval)

if __name__ == "__main__":
    main() 