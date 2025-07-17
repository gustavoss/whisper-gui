# Whisper GUI

This Dockerfile creates a web interface to upload audio/video files to whisper for transcriptions.

## Install Instructions

### Step 1: Clone the repository
```bash
git clone https://github.com/gustavoss/whisper-gui.git
```

### Step 2: Navigate into the repository
```bash
cd ./whisper-gui
```

### Step 3: Build image
```bash
docker build -t whisper-gui .
```

### Step 4: Create and run container
```bash
docker run -d \
--name=whisper-gui \
--network=host \
--restart always  \
whisper-gui
```

### Step 5: Web interface
Go to http://localhost:5000
