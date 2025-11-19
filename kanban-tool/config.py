"""
CWT Thread Verification System - Kanban Tool Configuration
Configuration constants for RFID Kanban card operations
"""

# RFID Card Block Assignments
BLOCK_THREAD1 = 4  # Block number for Thread 1 data
BLOCK_THREAD2 = 5  # Block number for Thread 2 data
BLOCK_SIZE = 16    # MIFARE Classic block size in bytes

# Default MIFARE Classic Key (Key A)
# Factory default: all bytes are 0xFF
DEFAULT_KEY_A = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# Special Keywords
BYPASS_KEYWORD = "bypass"  # Keyword for bypass mode

# Application Settings
APP_TITLE = "CWT Thread Verification - Kanban Card Tool"
APP_VERSION = "1.0.0"
APP_WIDTH = 600
APP_HEIGHT = 500

# Reader Settings
READER_TIMEOUT = 5  # Seconds to wait for card
READER_NAME_FILTER = "acr122"  # Filter for ACR122U reader (case-insensitive)

# UI Colors
COLOR_SUCCESS = "#28a745"  # Green
COLOR_ERROR = "#dc3545"    # Red
COLOR_WARNING = "#ffc107"  # Yellow
COLOR_INFO = "#17a2b8"     # Blue
COLOR_BG = "#f8f9fa"       # Light gray background

# Log Settings
LOG_MAX_LINES = 1000  # Maximum lines in log display
