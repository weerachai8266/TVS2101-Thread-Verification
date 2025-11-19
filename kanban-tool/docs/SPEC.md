# Kanban Tool Technical Specification
# ข้อมูลจำเพาะทางเทคนิคของเครื่องมือ Kanban

## System Overview | ภาพรวมระบบ

The Kanban Tool is a Python-based desktop application that provides a graphical interface for managing RFID Kanban cards used in the CWT Thread Verification System.

## Architecture | สถาปัตยกรรม

```
┌─────────────────────────────────────────┐
│         Main Application (main.py)      │
│  ┌───────────────────────────────────┐  │
│  │   Application Controller          │  │
│  │   - Event Handling                │  │
│  │   - State Management              │  │
│  │   - Error Handling                │  │
│  └───────────────────────────────────┘  │
│              │            │              │
│              ▼            ▼              │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │    GUI      │  │  RFID Manager    │  │
│  │  (gui.py)   │  │ (rfid_manager.py)│  │
│  │             │  │                  │  │
│  │  - Tkinter  │  │  - pyscard       │  │
│  │  - Widgets  │  │  - ACR122U API   │  │
│  │  - Events   │  │  - MIFARE Ops    │  │
│  └─────────────┘  └──────────────────┘  │
│                           │              │
│                           ▼              │
│                  ┌─────────────────┐     │
│                  │   ACR122U       │     │
│                  │   RFID Reader   │     │
│                  └─────────────────┘     │
│                           │              │
│                           ▼              │
│                  ┌─────────────────┐     │
│                  │  MIFARE Classic │     │
│                  │  1K Card        │     │
│                  └─────────────────┘     │
└─────────────────────────────────────────┘
```

## Component Specifications | ข้อมูลจำเพาะของส่วนประกอบ

### 1. main.py - Application Controller

**Purpose:** Main entry point and application controller

**Key Classes:**
- `KanbanToolApp` - Main application class

**Responsibilities:**
- Initialize GUI and RFID manager
- Handle user actions
- Coordinate between GUI and RFID operations
- Error handling and logging

**Key Methods:**
```python
initialize_reader() -> None
wait_for_card() -> bool
write_kanban(thread1: str, thread2: str) -> None
read_kanban() -> None
write_bypass() -> None
clear_card() -> None
run() -> None
```

### 2. gui.py - User Interface

**Purpose:** Tkinter-based graphical user interface

**Key Classes:**
- `KanbanGUI` - Main GUI window

**Components:**
- Header section with title and version
- Status indicators (reader, card)
- Thread code input fields (with length validation)
- Action buttons (Write, Read, Bypass, Clear)
- Activity log with colored output

**Event Callbacks:**
```python
on_write_kanban: Callable[[str, str], None]
on_read_kanban: Callable[[], None]
on_write_bypass: Callable[[], None]
on_clear_card: Callable[[], None]
```

**Public Methods:**
```python
log(message: str, level: str) -> None
set_reader_status(status: str, connected: bool) -> None
set_card_status(status: str, present: bool) -> None
set_thread_values(thread1: str, thread2: str) -> None
clear_inputs() -> None
show_error/success/warning(title: str, message: str) -> None
```

### 3. rfid_manager.py - RFID Operations

**Purpose:** Handle all RFID card operations

**Key Classes:**
- `RFIDManager` - RFID card operations manager

**Dependencies:**
- `smartcard.System` - PC/SC interface
- `smartcard.util` - Utility functions

**Key Methods:**

```python
connect_reader() -> Tuple[bool, str]
    """Connect to ACR122U reader"""

wait_for_card(timeout: int) -> Tuple[bool, str]
    """Wait for card presence"""

authenticate_block(block: int, key: List[int]) -> Tuple[bool, str]
    """Authenticate MIFARE block"""

read_block(block: int) -> Tuple[bool, Optional[bytes], str]
    """Read 16 bytes from block"""

write_block(block: int, data: bytes) -> Tuple[bool, str]
    """Write 16 bytes to block"""

write_kanban(thread1: str, thread2: str) -> Tuple[bool, str]
    """Write thread codes to card"""

read_kanban() -> Tuple[bool, Optional[str], Optional[str], str]
    """Read thread codes from card"""

verify_data(expected_thread1: str, expected_thread2: str) -> Tuple[bool, str]
    """Verify written data"""

write_bypass() -> Tuple[bool, str]
    """Write bypass mode"""

clear_card() -> Tuple[bool, str]
    """Clear card data"""

disconnect() -> None
    """Disconnect from card"""
```

### 4. config.py - Configuration

**Purpose:** Central configuration constants

**Constants:**

```python
# RFID Configuration
BLOCK_THREAD1 = 4
BLOCK_THREAD2 = 5
BLOCK_SIZE = 16
DEFAULT_KEY_A = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
BYPASS_KEYWORD = "bypass"

# Application Configuration
APP_TITLE = "CWT Thread Verification - Kanban Card Tool"
APP_VERSION = "1.0.0"
APP_WIDTH = 600
APP_HEIGHT = 500

# Reader Configuration
READER_TIMEOUT = 5  # seconds
READER_NAME_FILTER = "acr122"

# UI Colors
COLOR_SUCCESS = "#28a745"
COLOR_ERROR = "#dc3545"
COLOR_WARNING = "#ffc107"
COLOR_INFO = "#17a2b8"
COLOR_BG = "#f8f9fa"

# Logging
LOG_MAX_LINES = 1000
```

## Data Flow | ขั้นตอนการทำงาน

### Write Kanban Workflow

```
User Input (Thread Codes)
         ↓
Validation (Length, Format)
         ↓
GUI: Click "Write Kanban"
         ↓
Main: write_kanban()
         ↓
RFID: wait_for_card()
         ↓
RFID: authenticate_block(4)
         ↓
RFID: write_block(4, thread1_data)
         ↓
RFID: authenticate_block(5)
         ↓
RFID: write_block(5, thread2_data)
         ↓
RFID: verify_data()
         ↓
GUI: Show Success/Error
         ↓
RFID: disconnect()
```

### Read Kanban Workflow

```
GUI: Click "Read Kanban"
         ↓
Main: read_kanban()
         ↓
RFID: wait_for_card()
         ↓
RFID: authenticate_block(4)
         ↓
RFID: read_block(4)
         ↓
RFID: authenticate_block(5)
         ↓
RFID: read_block(5)
         ↓
Convert bytes to strings
         ↓
GUI: Update input fields
         ↓
GUI: Show data dialog
         ↓
RFID: disconnect()
```

## APDU Commands | คำสั่ง APDU

### ACR122U Command Set

```
Load Authentication Key:
FF 82 00 00 06 [6 key bytes]
Response: 90 00 (success)

Authenticate Block:
FF 86 00 00 05 01 00 [block] [key_type] 00
  - key_type: 60 (Key A), 61 (Key B)
Response: 90 00 (success)

Read Binary Block:
FF B0 00 [block] [length]
Response: [data bytes] 90 00

Update Binary Block:
FF D6 00 [block] [length] [data bytes]
Response: 90 00 (success)
```

### Response Codes

| Code | Meaning |
|------|---------|
| 90 00 | Success |
| 63 00 | Authentication failed |
| 69 81 | Command not allowed |
| 6A 81 | Function not supported |
| 6A 82 | File/record not found |

## Error Handling | การจัดการข้อผิดพลาด

### Error Hierarchy

```
Exception
├── CardConnectionException
│   ├── NoCardException
│   └── ConnectionError
├── AuthenticationError
├── ReadError
└── WriteError
```

### Error Recovery

1. **Reader Not Found:**
   - Display warning
   - Allow operation attempts
   - Graceful degradation

2. **Card Not Present:**
   - Wait with timeout
   - Display clear instructions
   - Allow retry

3. **Authentication Failed:**
   - Log error details
   - Suggest card replacement
   - Try alternative keys

4. **Write Failed:**
   - Roll back operation
   - Clear partial data
   - Notify user

## Performance Specifications | ข้อมูลจำเพาะประสิทธิภาพ

### Timing

| Operation | Typical | Maximum |
|-----------|---------|---------|
| Reader Connection | 500 ms | 2 s |
| Card Detection | 200 ms | 10 s |
| Block Authentication | 50 ms | 200 ms |
| Block Read | 50 ms | 200 ms |
| Block Write | 100 ms | 500 ms |
| Complete Write | 300 ms | 2 s |
| Complete Read | 200 ms | 1 s |

### Memory Usage

```
Application: ~50 MB
  - Python Runtime: ~30 MB
  - Tkinter GUI: ~10 MB
  - pyscard: ~5 MB
  - Other: ~5 MB
```

### CPU Usage

```
Idle: < 1%
Active (card operation): 5-10%
Peak (GUI updates): < 20%
```

## Testing Requirements | ข้อกำหนดการทดสอบ

### Unit Tests

```python
test_rfid_manager.py:
  - test_connect_reader()
  - test_authenticate_block()
  - test_read_block()
  - test_write_block()
  - test_write_kanban()
  - test_read_kanban()
  - test_verify_data()

test_gui.py:
  - test_input_validation()
  - test_button_callbacks()
  - test_log_display()
  - test_status_updates()
```

### Integration Tests

```python
test_integration.py:
  - test_complete_write_read_cycle()
  - test_bypass_mode()
  - test_clear_operation()
  - test_error_handling()
```

### Manual Testing Checklist

- [ ] Reader connection with ACR122U
- [ ] Card detection timing
- [ ] Write operation with various thread codes
- [ ] Read operation accuracy
- [ ] Bypass mode creation
- [ ] Card clearing
- [ ] Error message display
- [ ] Log output correctness
- [ ] GUI responsiveness
- [ ] Multi-card operations

## Security Considerations | ข้อควรระวังด้านความปลอดภัย

### Authentication

- Uses default MIFARE Key A (0xFF x 6)
- Supports custom key configuration
- Key stored in memory only (not persisted)

### Data Validation

```python
def validate_thread_code(code: str) -> bool:
    """Validate thread code format"""
    if len(code) > 16:
        return False
    if not code.isprintable():
        return False
    return True
```

### Access Control

- No built-in access control
- Bypass mode requires explicit confirmation
- Activity log for audit trail

### Recommendations

1. **Production Use:**
   - Change default MIFARE keys
   - Implement user authentication
   - Encrypt sensitive data
   - Add digital signatures

2. **Bypass Cards:**
   - Store securely
   - Track usage
   - Limit distribution
   - Regular audits

## Future Enhancements | การพัฒนาในอนาคต

### Planned Features

1. **Batch Operations:**
   - Import thread codes from CSV
   - Process multiple cards
   - Export card data

2. **Database Integration:**
   - Store card history
   - Track thread inventory
   - Generate reports

3. **Network Features:**
   - Remote card management
   - Cloud backup
   - Multi-station sync

4. **Advanced Security:**
   - Custom key management
   - User access control
   - Encrypted storage
   - Audit logging

## References | เอกสารอ้างอิง

- MIFARE Classic 1K Datasheet (NXP)
- ACR122U Application Programming Interface (ACS)
- PC/SC Specification (PC/SC Workgroup)
- pyscard Documentation
- Tkinter Documentation

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-01-19  
**Author:** CWT Team
