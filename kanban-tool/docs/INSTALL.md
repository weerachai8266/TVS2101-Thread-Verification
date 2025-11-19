# Installation Guide - Kanban Card Tool
# คู่มือการติดตั้ง - เครื่องมือการ์ด Kanban

## System Requirements | ความต้องการของระบบ

### Minimum Requirements | ข้อกำหนดขั้นต่ำ

- **Operating System:** Windows 10 (64-bit) or later
- **Processor:** Intel Core i3 or equivalent
- **RAM:** 2 GB
- **Storage:** 500 MB free space
- **USB:** USB 2.0 port (for ACR122U reader)
- **Display:** 1024x768 resolution

### Recommended Requirements | ข้อกำหนดที่แนะนำ

- **Operating System:** Windows 11 (64-bit)
- **Processor:** Intel Core i5 or better
- **RAM:** 4 GB or more
- **Storage:** 1 GB free space
- **USB:** USB 3.0 port
- **Display:** 1920x1080 resolution

## Installation Steps | ขั้นตอนการติดตั้ง

### Step 1: Install Python | ติดตั้ง Python

1. **Download Python:**
   - Go to https://www.python.org/downloads/
   - Click "Download Python 3.11.x" (or latest 3.x version)
   - Save the installer file

2. **Run Python Installer:**
   - Double-click the downloaded installer
   - ⚠️ **IMPORTANT:** Check "Add Python to PATH"
   - Click "Install Now"
   - Wait for installation to complete
   - Click "Close"

3. **Verify Installation:**
   ```cmd
   python --version
   ```
   - Should display: `Python 3.11.x` (or your installed version)

   ```cmd
   pip --version
   ```
   - Should display pip version information

### Step 2: Install ACR122U Driver | ติดตั้งไดรเวอร์ ACR122U

1. **Connect ACR122U Reader:**
   - Plug ACR122U into USB port
   - Windows should detect and install driver automatically
   - Wait for "Device ready to use" notification

2. **Verify Driver Installation:**
   - Open Device Manager (Win + X, then M)
   - Expand "Smart card readers"
   - Look for "ACS ACR122U PICC Interface" or similar
   - If not present, proceed to manual installation

3. **Manual Driver Installation (if needed):**
   - Download driver from: https://www.acs.com.hk/en/driver/3/acr122u-usb-nfc-reader/
   - Extract ZIP file
   - Run installer
   - Follow on-screen instructions
   - Restart computer if prompted

### Step 3: Download Project Files | ดาวน์โหลดไฟล์โปรเจค

**Option A: Download ZIP from GitHub**

1. Go to https://github.com/weerachai8266/CWT-Thread-Verification
2. Click green "Code" button
3. Click "Download ZIP"
4. Extract ZIP to desired location (e.g., `C:\CWT\`)

**Option B: Clone with Git**

```cmd
cd C:\
git clone https://github.com/weerachai8266/CWT-Thread-Verification.git
cd CWT-Thread-Verification
```

### Step 4: Install Python Dependencies | ติดตั้งไลบรารี Python

1. **Open Command Prompt:**
   - Press Win + R
   - Type `cmd` and press Enter

2. **Navigate to kanban-tool directory:**
   ```cmd
   cd C:\CWT-Thread-Verification\kanban-tool
   ```
   (Adjust path based on where you extracted/cloned)

3. **Install requirements:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Verify installation:**
   ```cmd
   pip list | findstr pyscard
   ```
   - Should show: `pyscard 2.0.7` (or similar)

### Step 5: Test Installation | ทดสอบการติดตั้ง

1. **Ensure ACR122U is connected**

2. **Run the application:**
   ```cmd
   python main.py
   ```

3. **Verify:**
   - Application window should open
   - Status should show "Reader: Connected"
   - If reader not connected, check troubleshooting section

## Creating Desktop Shortcut | สร้างทางลัดบนเดสก์ท็อป

### Option A: Manual Shortcut

1. Right-click on Desktop
2. New → Shortcut
3. Enter location:
   ```
   C:\Python311\python.exe "C:\CWT-Thread-Verification\kanban-tool\main.py"
   ```
   (Adjust paths to match your installation)
4. Click "Next"
5. Name it "Kanban Tool"
6. Click "Finish"
7. Right-click shortcut → Properties
8. Set "Start in" to: `C:\CWT-Thread-Verification\kanban-tool`
9. Click "OK"

### Option B: Batch File Launcher

1. Create file `Kanban_Tool.bat` on Desktop
2. Edit with Notepad and add:
   ```batch
   @echo off
   cd /d C:\CWT-Thread-Verification\kanban-tool
   python main.py
   pause
   ```
3. Save and close
4. Double-click to run

## Creating Standalone Executable (Optional) | สร้างไฟล์ exe (เพิ่มเติม)

For easier distribution without Python installation:

1. **Install PyInstaller:**
   ```cmd
   pip install pyinstaller
   ```

2. **Create executable:**
   ```cmd
   cd C:\CWT-Thread-Verification\kanban-tool
   pyinstaller --onefile --windowed --name "Kanban_Tool" main.py
   ```

3. **Find executable:**
   - Location: `kanban-tool\dist\Kanban_Tool.exe`
   - Can be copied to Desktop or other location
   - No Python needed on target computer

4. **Note:** 
   - Executable size: ~15-20 MB
   - ACR122U driver still required
   - May trigger antivirus (false positive)

## Troubleshooting Installation | แก้ไขปัญหาการติดตั้ง

### Python Not Found

**Error:** `'python' is not recognized as an internal or external command`

**Solutions:**
1. Reinstall Python with "Add to PATH" checked
2. Manually add Python to PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add `C:\Python311` and `C:\Python311\Scripts`
   - Restart Command Prompt

### pip Not Working

**Error:** `'pip' is not recognized...`

**Solutions:**
1. Try `python -m pip install -r requirements.txt`
2. Reinstall Python
3. Update pip: `python -m pip install --upgrade pip`

### pyscard Installation Failed

**Error:** `error: Microsoft Visual C++ 14.0 or greater is required`

**Solutions:**

**Option 1: Install Build Tools**
1. Download: https://visualstudio.microsoft.com/downloads/
2. Install "Build Tools for Visual Studio 2022"
3. Select "Desktop development with C++"
4. Install and restart
5. Retry: `pip install pyscard`

**Option 2: Use Pre-built Wheel**
1. Download pyscard wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyscard
2. Choose file matching your Python version (e.g., `pyscard‑2.0.7‑cp311‑cp311‑win_amd64.whl`)
3. Install: `pip install path\to\downloaded\file.whl`

### ACR122U Not Detected

**Problem:** "No RFID readers found"

**Solutions:**

1. **Check USB Connection:**
   - Try different USB port
   - Avoid USB hubs if possible
   - Look for LED on reader

2. **Verify Device Manager:**
   - Open Device Manager
   - Check "Smart card readers"
   - Should see ACR122U listed
   - If yellow warning icon, update driver

3. **Reinstall Driver:**
   - Uninstall ACR122U from Device Manager
   - Unplug reader
   - Download fresh driver from ACS website
   - Install driver
   - Plug in reader

4. **Test with Other Software:**
   - Download "ACS ACR122U Tools" from ACS website
   - Test card reading
   - If works there, check Python installation

### Application Won't Start

**Error:** Application crashes immediately

**Solutions:**
1. Run from Command Prompt to see error messages
2. Check Python version: `python --version` (should be 3.8+)
3. Verify all files present in kanban-tool directory
4. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
5. Check Windows Event Viewer for errors

### Import Error: smartcard

**Error:** `ModuleNotFoundError: No module named 'smartcard'`

**Solutions:**
1. Install pyscard: `pip install pyscard`
2. Check pip list: `pip list | findstr pyscard`
3. Verify Python environment (not using wrong Python installation)
4. Try: `python -m pip install pyscard`

## Updating the Application | อัปเดตโปรแกรม

### Update from GitHub

```cmd
cd C:\CWT-Thread-Verification
git pull origin main
cd kanban-tool
pip install -r requirements.txt --upgrade
```

### Manual Update

1. Download latest release from GitHub
2. Extract to temporary folder
3. Copy new files over old installation
4. Keep your data/settings if any
5. Test application

## Uninstallation | การถอนการติดตั้ง

### Remove Application

1. Delete project folder:
   ```cmd
   rmdir /s "C:\CWT-Thread-Verification"
   ```

2. Remove Python packages (optional):
   ```cmd
   pip uninstall pyscard -y
   ```

3. Delete shortcuts from Desktop

### Keep Python Installed

- Python can be used for other projects
- If you want to remove it:
  - Settings → Apps → Python → Uninstall

### Remove ACR122U Driver

- Usually keep installed for other RFID applications
- To remove:
  - Device Manager → ACR122U → Uninstall device
  - Check "Delete driver software"

## Multi-Computer Deployment | การติดตั้งหลายเครื่อง

### For Multiple Workstations

1. **Prepare Installation Package:**
   - Create folder with:
     - Python installer
     - ACR122U driver
     - Project files (ZIP)
     - Installation script

2. **Installation Script (install.bat):**
   ```batch
   @echo off
   echo Installing CWT Kanban Tool...
   
   REM Install Python
   python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
   
   REM Install driver
   ACR122U-driver.exe /S
   
   REM Extract project
   powershell -command "Expand-Archive -Path CWT.zip -DestinationPath C:\"
   
   REM Install dependencies
   cd C:\CWT-Thread-Verification\kanban-tool
   pip install -r requirements.txt
   
   echo Installation complete!
   pause
   ```

3. **Deploy via USB or network share**

### Alternative: Standalone EXE

- Create executable with PyInstaller (see above)
- Distribute single EXE file
- Only ACR122U driver needed on target PC
- Easier for non-technical users

## Support | การสนับสนุน

### Documentation

- User Guide: [USER_GUIDE.md](USER_GUIDE.md)
- Technical Spec: [SPEC.md](SPEC.md)
- Main README: [README.md](../README.md)

### Getting Help

- GitHub Issues: Report bugs or request features
- Email support: Check main README for contact

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-01-19  
**Tested On:** Windows 10/11, Python 3.11  
**Author:** CWT Team
