## Tool Navigation
```
Dashboard
├── 1. Data & AI Utilities
│   ├── 1. Vision Tool
│   │   ├── 1. Roboflow Tools
│   │   │   ├── 1. Upload Model
│   │   │   ├── 2. Add Account
│   │   │   ├── 3. Delete Account
│   │   │   └── 4. Switch Account
│   │   ├── 2. Video Tools
│   │   │   └── 1. Video to Frames
│   │   └── 3. Multimodal Tools
│   │       └── 1. Image Annotation
│   ├── 2. Dataset Tools
│   │   └── 1. Format Conversion
│   │       └── 1. COCO to YOLO
│   └── 3. AI Development
│       ├── 1. Hugging Face Tools
│       │   ├── 1. Clone Model Repository
│       │   └── 2. Model Management
│       └── 2. Gemini AI Tools
│           ├── 1. Chat CLI
│           ├── 2. Auto Git Commit Message
│           └── 3. Account Management
│               ├── 1. Add Account
│               ├── 3. Switch Account
│               └── 4. Delete Account
├── 2. Mobile Development
│   ├── 1. Android Tools
│   │   ├── 1. ADB Management
│   │   │   ├── 1. Connect ADB WiFi
│   │   │   ├── 2. List ADB Devices
│   │   │   ├── 3. Remove ADB Device
│   │   │   └── 4. Uninstall App
│   │   └── 2. Build Tools
│   │       └── 1. Generate AAB
│   └── 2. Flutter Tools
│       └── 1. Development Utils
├── 3. System Tools
│   ├── 1. Performance Monitor
│   │   ├── 1. CPU Usage
│   │   ├── 2. RAM Usage
│   │   ├── 3. Storage Analysis
│   │   └── 4. Process List
│   ├── 2. Network Tools
│   │   └── 1. Request Logger
│   └── 3. SSH Management
│       ├── 1. Generate SSH Key
│       ├── 2. View Public Key
│       └── 3. Remove SSH Key
└── 4. Developer Setup
    ├── 1. Environment Setup
    │   └── 1. Install Dev Tools
    └── 2. Application Management
        ├── 1. View Running Apps
        └── 2. Uninstall Apps
```

## Project Structure
.
├── categorie
│   ├── data_ai
│   │   ├── vision_tool
│   │   │   ├── roboflow_tool
│   │   │   │   ├── add_account.py
│   │   │   │   ├── delete_account.py
│   │   │   │   ├── log.txt
│   │   │   │   ├── roboflow_tool.py
│   │   │   │   ├── switch_account.py
│   │   │   │   └── upload_model
│   │   │   │       └── upload_model.py
│   │   │   ├── video_tool
│   │   │   │   └── video_to_frames.py
│   │   │   └── multimodal_tool
│   │   │       └── image_annotator.py
│   │   ├── ai_development
│   │   │   └── gemini_tools
│   │   │       ├── account_manager.py
│   │   │       └── gemini_tools.py
│   │   └── dataset_tools
│   │       └── format_conversion
│   │           └── coco_to_yolo.py
│   ├── mobile_dev
│   │   ├── android_tools
│   │   │   ├── adb_management.py
│   │   │   └── build_tools.py
│   │   └── flutter_tools
│   │       └── dev_utils.py
│   ├── system_tools
│   │   ├── performance_monitor.py
│   │   ├── network_tools.py
│   │   └── ssh_management.py
│   └── dev_setup
│       ├── env_setup.py
│       └── app_management.py
├── convert_to_instance.py
├── core
│   ├── menu.py
│   └── utils.py
├── log.txt
├── main.py
├── requirements.txt
└── TREE.md 