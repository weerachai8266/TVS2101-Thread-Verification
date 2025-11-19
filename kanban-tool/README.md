# Kanban Card Management Tool
# เครื่องมือจัดการการ์ด Kanban

## Overview | ภาพรวม

The Kanban Card Management Tool is a Windows desktop application for writing and reading RFID Kanban cards used in the CWT Thread Verification System.

เครื่องมือจัดการการ์ด Kanban เป็นโปรแกรมเดสก์ท็อปสำหรับ Windows ที่ใช้เขียนและอ่านการ์ด Kanban แบบ RFID สำหรับระบบตรวจสอบด้าย CWT

## Features | คุณสมบัติ

- ✅ **Write Kanban Cards** - Write thread codes to RFID cards
- ✅ **Read Kanban Cards** - Read and verify thread codes from cards
- ✅ **Bypass Mode** - Create bypass cards for special operations
- ✅ **Clear Cards** - Erase data from cards for reuse
- ✅ **User-Friendly GUI** - Simple and intuitive interface
- ✅ **Activity Log** - Track all operations with timestamps
- ✅ **Data Verification** - Automatic verification after writing

## Requirements | ความต้องการ

### Hardware | ฮาร์ดแวร์

1. **Windows PC**
   - Windows 10 or later (64-bit)
   - Minimum 2GB RAM
   - USB port

2. **ACR122U RFID Reader/Writer**
   - USB interface
   - PC/SC compliant
   - Supports MIFARE Classic 1K

3. **MIFARE Classic 1K Cards**
   - 13.56 MHz
   - 1KB storage
   - Standard Kanban cards

### Software | ซอฟต์แวร์

1. **Python 3.8 or later**
2. **pyscard library** (for RFID operations)
3. **ACR122U driver** (automatically installed by Windows)

## Installation | การติดตั้ง

See [INSTALL.md](docs/INSTALL.md) for detailed installation instructions.

### Quick Start | เริ่มต้นใช้งานด่วน

```bash
# 1. Install Python (if not already installed)
# Download from: https://www.python.org/downloads/

# 2. Navigate to kanban-tool directory
cd kanban-tool

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python main.py
```

## Usage | การใช้งาน

See [USER_GUIDE.md](docs/USER_GUIDE.md) for step-by-step instructions.

### Basic Workflow | ขั้นตอนพื้นฐาน

1. **Connect ACR122U reader** to PC via USB
2. **Launch application** by running `python main.py`
3. **Enter thread codes** in Thread 1 and Thread 2 fields
4. **Place Kanban card** on reader when prompted
5. **Click "Write Kanban"** to write data to card
6. **Verify** by reading the card back

### Writing a Kanban Card | การเขียนการ์ด Kanban

1. Enter Thread 1 code (e.g., "TH-001")
2. Enter Thread 2 code (e.g., "TH-002")
3. Click "Write Kanban" button
4. Place card on reader within 10 seconds
5. Wait for success message
6. Remove card

### Reading a Kanban Card | การอ่านการ์ด Kanban

1. Click "Read Kanban" button
2. Place card on reader within 10 seconds
3. Thread codes will appear in input fields
4. Check activity log for details
5. Remove card

### Creating a Bypass Card | การสร้างการ์ดบายพาส

1. Click "Write Bypass" button
2. Confirm the action
3. Place card on reader within 10 seconds
4. Wait for success message
5. Remove card

⚠️ **Warning:** Bypass cards skip all verification. Use with caution!

### Clearing a Card | การล้างข้อมูลการ์ด

1. Click "Clear Card" button
2. Confirm the action
3. Place card on reader within 10 seconds
4. Wait for success message
5. Card is now ready for reuse

## GUI Overview | ภาพรวมหน้าจอ

```
┌─────────────────────────────────────────────┐
│  CWT Thread Verification                    │
│  Kanban Card Management Tool                │
│  Version 1.0.0                              │
├─────────────────────────────────────────────┤
│  Status                                     │
│  Reader: Connected                          │
│  Card: No Card                              │
├─────────────────────────────────────────────┤
│  Thread Codes                               │
│  Thread 1: [________________]  0/16         │
│  Thread 2: [________________]  0/16         │
│  Example: TH-001, TH-RED-100, etc.          │
├─────────────────────────────────────────────┤
│  [Write Kanban] [Read Kanban]               │
│  [Write Bypass] [Clear Card]                │
├─────────────────────────────────────────────┤
│  Activity Log                               │
│  [12:34:56] Ready to use...                 │
│  [12:35:10] Writing Kanban...               │
│  [12:35:12] Card detected                   │
│  [12:35:15] Success!                        │
│  ▼                                          │
└─────────────────────────────────────────────┘
```

## Troubleshooting | การแก้ไขปัญหา

### Reader Not Detected

**Problem:** "No RFID readers found" message

**Solutions:**
1. Check USB connection
2. Install/update ACR122U driver
3. Try different USB port
4. Restart application

### Card Not Reading

**Problem:** "Timeout waiting for card" message

**Solutions:**
1. Place card flat on reader
2. Keep card still for 3-5 seconds
3. Try different card
4. Clean reader surface
5. Check card type (must be MIFARE Classic 1K)

### Write Failed

**Problem:** "Failed to write" error

**Solutions:**
1. Verify card is not write-protected
2. Try clearing card first
3. Use new card
4. Check card compatibility

### Authentication Failed

**Problem:** "Authentication failed" error

**Solutions:**
1. Card may have custom keys
2. Try different card
3. Clear card using factory reset tools
4. Use new card

## Data Format | รูปแบบข้อมูล

See [../docs/DATA_FORMAT.md](../docs/DATA_FORMAT.md) for detailed specification.

### Kanban Card Layout

```
Block 4: Thread 1 Code (16 bytes, ASCII)
Block 5: Thread 2 Code (16 bytes, ASCII)
```

### Thread Code Format

- **Maximum Length:** 16 characters
- **Encoding:** ASCII
- **Allowed Characters:** A-Z, a-z, 0-9, hyphen (-), underscore (_)
- **Examples:**
  - "TH-001"
  - "RED-100"
  - "BLUE-COTTON-01"
  - "bypass" (special keyword)

## Advanced Features | คุณสมบัติขั้นสูง

### Command-Line Mode (Future)

```bash
# Write Kanban
python main.py --write --thread1 "TH-001" --thread2 "TH-002"

# Read Kanban
python main.py --read

# Write Bypass
python main.py --bypass

# Clear Card
python main.py --clear
```

### Batch Operations (Future)

Process multiple cards from CSV file:

```bash
python main.py --batch cards.csv
```

## Security Considerations | ข้อควรระวังด้านความปลอดภัย

1. **Card Access:** Uses default MIFARE keys. Consider changing keys for production.
2. **Bypass Cards:** Store securely, restrict access to authorized personnel only.
3. **Data Validation:** Application validates input length and format.
4. **Audit Trail:** Activity log records all operations with timestamps.

## Support | การสนับสนุน

### Documentation

- [Installation Guide](docs/INSTALL.md) - Setup instructions
- [User Guide](docs/USER_GUIDE.md) - Detailed usage instructions
- [Specification](docs/SPEC.md) - Technical details

### Getting Help

- Check troubleshooting section above
- Review activity log for error messages
- Open an issue on GitHub

## Development | การพัฒนา

### Project Structure

```
kanban-tool/
├── main.py           # Main application
├── gui.py            # GUI components
├── rfid_manager.py   # RFID operations
├── config.py         # Configuration
├── requirements.txt  # Dependencies
└── docs/            # Documentation
```

### Testing

```bash
# Run with verbose logging
python main.py --verbose

# Test without hardware (simulation mode)
python main.py --simulate
```

## License | สัญญาอนุญาต

MIT License - See [../LICENSE](../LICENSE) for details

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-19  
**Author:** CWT Team
