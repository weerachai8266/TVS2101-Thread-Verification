# User Guide - Kanban Card Tool
# คู่มือผู้ใช้ - เครื่องมือการ์ด Kanban

## Table of Contents | สารบัญ

1. [Getting Started](#getting-started--เริ่มต้นใช้งาน)
2. [Understanding the Interface](#understanding-the-interface--ทำความเข้าใจหน้าจอ)
3. [Writing Kanban Cards](#writing-kanban-cards--การเขียนการ์ด-kanban)
4. [Reading Kanban Cards](#reading-kanban-cards--การอ่านการ์ด-kanban)
5. [Creating Bypass Cards](#creating-bypass-cards--การสร้างการ์ดบายพาส)
6. [Clearing Cards](#clearing-cards--การล้างข้อมูลการ์ด)
7. [Best Practices](#best-practices--แนวทางปฏิบัติที่ดี)
8. [Troubleshooting](#troubleshooting--การแก้ไขปัญหา)

## Getting Started | เริ่มต้นใช้งาน

### Prerequisites | สิ่งที่ต้องเตรียม

Before using the Kanban Tool, ensure you have:

- ✅ ACR122U RFID reader connected via USB
- ✅ MIFARE Classic 1K cards
- ✅ Application installed (see [INSTALL.md](INSTALL.md))
- ✅ Reader driver installed and working

### Launching the Application | เปิดโปรแกรม

**Method 1: Desktop Shortcut**
- Double-click "Kanban Tool" shortcut on Desktop

**Method 2: Command Line**
```cmd
cd C:\CWT-Thread-Verification\kanban-tool
python main.py
```

### First Launch | การเปิดครั้งแรก

When you first launch the application:

1. **Application Window Opens**
   - Title: "CWT Thread Verification - Kanban Card Tool"
   - Version number displayed

2. **Reader Status Check**
   - If ACR122U detected: Status shows "Connected" (green)
   - If not detected: Warning dialog appears

3. **Ready to Use**
   - Log shows: "Ready to use..."
   - Card status: "No Card"

## Understanding the Interface | ทำความเข้าใจหน้าจอ

### Window Layout | รูปแบบหน้าต่าง

```
┌────────────────────────────────────────────┐
│ [1] Header Section                         │
├────────────────────────────────────────────┤
│ [2] Status Section                         │
├────────────────────────────────────────────┤
│ [3] Input Section                          │
├────────────────────────────────────────────┤
│ [4] Button Section                         │
├────────────────────────────────────────────┤
│ [5] Activity Log Section                   │
└────────────────────────────────────────────┘
```

### Section Details | รายละเอียดแต่ละส่วน

#### [1] Header Section
- **Title:** "CWT Thread Verification"
- **Subtitle:** "Kanban Card Management Tool"
- **Version:** Current version number

#### [2] Status Section
- **Reader:** Shows ACR122U connection status
  - "Connected" (bold) = Ready to use
  - "Not Connected" = Check USB connection
- **Card:** Shows card presence on reader
  - "No Card" = No card detected
  - "Card Detected" = Ready for operation
  - "Waiting..." = Waiting for card placement

#### [3] Input Section
- **Thread 1:** Text field for first thread code
  - Maximum 16 characters
  - Character counter shows X/16
  - Red counter if > 16 characters
- **Thread 2:** Text field for second thread code
  - Same rules as Thread 1
- **Example:** Guidance text with examples

#### [4] Button Section
Four action buttons:
- **📝 Write Kanban:** Write thread codes to card
- **📖 Read Kanban:** Read thread codes from card
- **⚡ Write Bypass:** Create bypass mode card
- **🗑️ Clear Card:** Erase card data

#### [5] Activity Log Section
- **Scrollable text area** showing all operations
- **Timestamps:** Each entry shows time
- **Color coding:**
  - Blue = Information
  - Green = Success
  - Yellow = Warning
  - Red = Error

## Writing Kanban Cards | การเขียนการ์ด Kanban

### Step-by-Step Process | ขั้นตอนทีละขั้น

#### Step 1: Prepare Thread Information

Before starting, know your thread codes:
- Thread 1 code (e.g., "TH-RED-001")
- Thread 2 code (e.g., "TH-BLUE-002")

#### Step 2: Enter Thread Codes

1. Click in "Thread 1" field
2. Type first thread code
3. Check character counter (must be ≤ 16)
4. Click in "Thread 2" field
5. Type second thread code
6. Check character counter

**Example:**
```
Thread 1: TH-001
Thread 2: TH-002
```

#### Step 3: Initiate Write Operation

1. Click "📝 Write Kanban" button
2. Log shows: "Writing Kanban: Thread1='TH-001', Thread2='TH-002'"
3. Log shows: "Waiting for card... Please place card on reader."

#### Step 4: Place Card on Reader

1. Take a MIFARE Classic 1K card
2. Place it flat on ACR122U reader
3. Keep card still (don't move)
4. Wait for detection (1-2 seconds)

**Card Placement Tips:**
- Place card centered on reader
- Keep card flat and still
- Remove any metal objects nearby
- One card at a time

#### Step 5: Wait for Completion

The application will:
1. Detect card (log shows "Card detected")
2. Authenticate block 4
3. Write Thread 1 data
4. Authenticate block 5
5. Write Thread 2 data
6. Verify written data
7. Show success message

**Success Dialog:**
```
✅ Success

Kanban card written successfully!

Thread 1: TH-001
Thread 2: TH-002

[ OK ]
```

#### Step 6: Remove Card

1. Read the success message
2. Click "OK"
3. Remove card from reader
4. Card is now ready to use on machine

### Writing Multiple Cards | เขียนหลายการ์ด

To write the same codes to multiple cards:

1. Enter thread codes once
2. Click "Write Kanban"
3. Place first card → Wait for success → Remove
4. Click "Write Kanban" again
5. Place second card → Wait for success → Remove
6. Repeat for all cards

**Time Estimate:** ~5 seconds per card

### Thread Code Guidelines | แนวทางรหัสด้าย

**Valid Characters:**
- Letters: A-Z, a-z
- Numbers: 0-9
- Symbols: Hyphen (-), Underscore (_)
- Spaces: Allowed but not recommended

**Good Examples:**
```
TH-001          ✅ Short and simple
RED-100         ✅ Color-based
COTTON-RED-01   ✅ Material-Color-Number
BLU_POLY_2      ✅ Using underscores
```

**Bad Examples:**
```
THREAD-NUMBER-001-LONG  ❌ Too long (> 16 chars)
สีแดง                   ❌ Non-ASCII characters
TH#001                  ❌ Special character (#)
                        ❌ Empty/blank
```

## Reading Kanban Cards | การอ่านการ์ด Kanban

### When to Read Cards | เมื่อไรควรอ่านการ์ด

- Verify card content after writing
- Check existing cards
- Troubleshoot machine issues
- Audit card inventory

### Reading Process | ขั้นตอนการอ่าน

#### Step 1: Initiate Read

1. Click "📖 Read Kanban" button
2. Log shows: "Reading Kanban card..."
3. Log shows: "Waiting for card..."

#### Step 2: Place Card

1. Place card on reader (same as writing)
2. Keep still until complete

#### Step 3: View Results

**Success:** Dialog shows thread codes
```
✅ Card Read Successfully

Thread 1: TH-001
Thread 2: TH-002

[ OK ]
```

**Also:**
- Thread codes appear in input fields
- Log shows both thread values
- Can now edit and re-write if needed

**Bypass Card Detected:**
```
⚠️ Bypass Card

This is a BYPASS card.

Machine will operate without verification.

[ OK ]
```

#### Step 4: Use Information

After reading:
- Input fields filled with card data
- Can modify codes and write back
- Can clear card
- Can write to new card with same codes

## Creating Bypass Cards | การสร้างการ์ดบายพาส

### What is a Bypass Card? | การ์ดบายพาสคืออะไร

A bypass card tells the machine to:
- ✅ Skip thread verification
- ✅ Enable operation immediately
- ⚠️ Ignore QR code scanning

**Use Cases:**
- Machine maintenance
- Emergency operations
- Testing without threads
- Special situations

**⚠️ WARNING:** Use bypass cards responsibly!

### Creating Bypass Card | สร้างการ์ดบายพาส

#### Step 1: Initiate Bypass Write

1. Click "⚡ Write Bypass" button
2. Confirmation dialog appears:

```
⚠️ Confirm Bypass

This will write a bypass card that skips verification.

Are you sure you want to continue?

[ Yes ]  [ No ]
```

#### Step 2: Confirm Action

1. Read the warning carefully
2. Click "Yes" if certain
3. Click "No" to cancel

#### Step 3: Place Card

1. Log shows: "Writing BYPASS card..."
2. Place card on reader
3. Wait for completion

#### Step 4: Success

```
✅ Success

BYPASS card written successfully!

⚠️ WARNING: This card will bypass all verification.
Use only for maintenance or special operations.

[ OK ]
```

### Bypass Card Best Practices | แนวทางการใช้การ์ดบายพาส

1. **Limited Quantity:**
   - Create only 1-2 bypass cards
   - Mark clearly with "BYPASS" label

2. **Secure Storage:**
   - Store in locked location
   - Limit access to supervisors only
   - Track usage

3. **Clear Marking:**
   - Use red card holder
   - Label "BYPASS - SUPERVISOR ONLY"
   - Document serial number

4. **Usage Logging:**
   - Record when used
   - Note reason and duration
   - Sign log book

5. **Regular Audit:**
   - Check bypass card location weekly
   - Verify not in general use
   - Replace if lost

## Clearing Cards | การล้างข้อมูลการ์ด

### When to Clear Cards | เมื่อไรควรล้างการ์ด

- Reuse cards for different thread codes
- Correct writing errors
- Decommission cards
- Before disposal

### Clearing Process | ขั้นตอนการล้าง

#### Step 1: Initiate Clear

1. Click "🗑️ Clear Card" button
2. Confirmation dialog:

```
⚠️ Confirm Clear

This will erase all data from the card.

Are you sure you want to continue?

[ Yes ]  [ No ]
```

#### Step 2: Confirm and Place Card

1. Click "Yes"
2. Place card on reader
3. Wait for completion

#### Step 3: Verify Clear

```
✅ Success

Card cleared successfully!

[ OK ]
```

Card is now blank and ready for new data.

### Bulk Clearing | ล้างหลายการ์ด

To clear multiple cards:
1. Click "Clear Card"
2. Confirm once
3. Place first card → Wait → Remove
4. Repeat "Clear Card" for next card
5. Continue until all cards cleared

## Best Practices | แนวทางปฏิบัติที่ดี

### Card Handling | การจัดการการ์ด

**DO:**
- ✅ Keep cards clean and dry
- ✅ Store in card holders
- ✅ Handle by edges
- ✅ Keep away from magnets
- ✅ Label card purpose

**DON'T:**
- ❌ Bend or fold cards
- ❌ Expose to extreme temperatures
- ❌ Place near strong magnets
- ❌ Use damaged cards
- ❌ Stack cards on reader

### Writing Operations | การเขียนข้อมูล

**Recommendations:**
- Always verify after writing (use Read function)
- Write cards in advance, not during production
- Keep backup cards ready
- Document all card contents
- Test new cards before field use

### Reader Maintenance | การบำรุงรักษาเครื่องอ่าน

**Weekly:**
- Clean reader surface with soft cloth
- Check USB cable connection
- Verify LED indicator working

**Monthly:**
- Test with known-good card
- Clean USB port
- Check for driver updates

## Troubleshooting | การแก้ไขปัญหา

### Card Not Detected

**Symptom:** "Timeout waiting for card"

**Solutions:**
1. ✓ Remove and repl ace card
2. ✓ Try different card position
3. ✓ Clean reader surface
4. ✓ Check reader LED is on
5. ✓ Try different USB port
6. ✓ Restart application

### Write Failed

**Symptom:** "Failed to write" error

**Solutions:**
1. ✓ Try clearing card first
2. ✓ Use different card
3. ✓ Check thread code length (≤16)
4. ✓ Remove special characters
5. ✓ Restart reader
6. ✓ Check reader connection

### Read Returns Wrong Data

**Symptom:** Different data than expected

**Possible Causes:**
- Wrong card used
- Card has old data
- Partial write occurred

**Solutions:**
1. Clear card
2. Write again
3. Verify immediately
4. Use fresh card if problem persists

### Application Freezes

**Symptom:** Program not responding

**Solutions:**
1. Wait 10 seconds (may be busy)
2. Close and restart application
3. Unplug reader, restart app, plug reader
4. Check system resources
5. Reinstall if persistent

## Quick Reference | อ้างอิงด่วน

### Common Thread Code Formats

```
Format               Example          Notes
─────────────────────────────────────────────────
TH-XXX              TH-001           Simple number
COLOR-NUM           RED-100          Color + number
MAT-COLOR-NUM       POLY-BLU-01      Material-Color-Number
BRAND-CODE          ACME-X200        Brand + code
```

### Keyboard Shortcuts

Currently, no keyboard shortcuts implemented.
Future versions may include:
- Ctrl+W: Write Kanban
- Ctrl+R: Read Kanban
- Ctrl+L: Clear inputs

### Status Indicators

| Color  | Meaning |
|--------|---------|
| Blue   | Information, normal operation |
| Green  | Success, operation completed |
| Yellow | Warning, attention needed |
| Red    | Error, operation failed |

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-01-19  
**Author:** CWT Team  
**For Support:** See main README or open GitHub issue
