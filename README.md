# TGOMMO
# Virtual Environment Setup Guide

#### Step 1: Create New Virtual Environment
```bash
# Navigate to your project directory
cd C:\Users\Ryan\PycharmProjects\3rdParty\Bumbot_SketchingAlley_TGO_MMO

# Create fresh virtual environment
python -m venv bumbot_env
```
#### Step 2: Configure PyCharm Interpreter
1. **File → Settings → Project → Python Interpreter**
2. **Click gear icon** → **Add...**
3. **Select "Existing environment"**
4. **Browse to:** `bumbot_env\Scripts\python.exe`
5. **Click OK**

#### Step 3: Activate and Install Dependencies
```bash
# Activate the environment
bumbot_env\Scripts\activate

# Install your requirements
pip install -r requirements.txt
```
#### Step 4: Verify Setup
```bash
# Check you're in the right environment
echo %VIRTUAL_ENV%

# Verify packages installed
pip list

# Test specific packages
pip show apscheduler
pip show discord.py
pip show twitchAPI
```

## Quick Reference Commands
### Check Active Environment
```bash
# Show virtual environment path
echo %VIRTUAL_ENV%

# Show Python location
where python

# Show pip location  
where pip
```

### Environment Management
```bash
# Activate environment
bumbot_env\Scripts\activate

# Deactivate environment
deactivate

# Create new environment
python -m venv env_name
```
### Troubleshooting

**Missing Package Error (`ModuleNotFoundError`)**
- Check if package is in `requirements.txt`
- Verify virtual environment is activated
- Re-run `pip install -r requirements.txt`

**Wrong Interpreter in PyCharm**
- Bottom right corner should show correct environment name
- Terminal should show `(bumbot_env)` prefix
- Follow Step 2 above to reconfigure

**Environment Location Issues**
- Always use full path to `Scripts\python.exe`
- Ensure environment folder exists
- Use `where python` to verify active interpreter

## Project Dependencies

This project requires the following key packages:
- `discord.py==2.7.1` - Discord bot framework
- `apscheduler==3.10.4` - Task scheduling
- `twitchAPI==4.4.0` - Twitch API integration
- `obs-websocket-py==1.0` - OBS Studio control
- `pynput==1.7.7` - Input automation
- `yt-dlp==2026.3.17` - YouTube downloading
- `pillow==12.1.1` - Image processing
- `requests==2.32.5` - HTTP requests

Full dependency list is maintained in `requirements.txt` with 38 packages total.

## When Things Go Wrong: Complete Reset

### 1. Delete Current Virtual Environment
```bash
# First deactivate the current environment
deactivate

# Delete the environment folder (replace with your actual env name)
rmdir /s /q bumbot_env
```
### 2. Remove Interpreter from PyCharm

1. **File → Settings → Project → Python Interpreter**
2. **Click gear icon** → **Show All...**
3. **Select the problematic interpreter**
4. **Click the `-` (minus) button**
5. **Confirm deletion**

### 3. Fresh Virtual Environment Setup

#### Repeat Steps 1-4 from the initial setup guide above to create a new environment, configure PyCharm, and install dependencies.