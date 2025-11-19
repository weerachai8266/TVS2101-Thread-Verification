"""
CWT Thread Verification System - RFID Manager
Handles all RFID card operations using ACR122U reader
"""

import logging
from typing import Optional, Tuple, List
from smartcard.System import readers
from smartcard.util import toHexString, toBytes
from smartcard.Exceptions import CardConnectionException, NoCardException
import time

from config import (
    BLOCK_THREAD1, BLOCK_THREAD2, BLOCK_SIZE,
    DEFAULT_KEY_A, BYPASS_KEYWORD, READER_TIMEOUT,
    READER_NAME_FILTER
)


class RFIDManager:
    """Manages RFID card operations for Kanban cards"""
    
    def __init__(self):
        self.reader = None
        self.connection = None
        self.logger = logging.getLogger(__name__)
        
    def connect_reader(self) -> Tuple[bool, str]:
        """
        Connect to ACR122U RFID reader
        
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        try:
            # Get list of available readers
            reader_list = readers()
            
            if len(reader_list) == 0:
                return False, "No RFID readers found. Please connect ACR122U."
            
            # Find ACR122U reader
            acr122_reader = None
            for r in reader_list:
                if READER_NAME_FILTER.lower() in str(r).lower():
                    acr122_reader = r
                    break
            
            if acr122_reader is None:
                # Use first available reader as fallback
                acr122_reader = reader_list[0]
                self.logger.warning(f"ACR122U not found, using: {acr122_reader}")
            
            self.reader = acr122_reader
            self.logger.info(f"Connected to reader: {self.reader}")
            return True, f"Reader connected: {self.reader}"
            
        except Exception as e:
            self.logger.error(f"Failed to connect reader: {e}")
            return False, f"Failed to connect reader: {str(e)}"
    
    def wait_for_card(self, timeout: int = READER_TIMEOUT) -> Tuple[bool, str]:
        """
        Wait for a card to be placed on the reader
        
        Args:
            timeout: Maximum seconds to wait for card
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        if self.reader is None:
            return False, "Reader not connected"
        
        try:
            # Try to connect to card
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    self.connection = self.reader.createConnection()
                    self.connection.connect()
                    
                    # Get card ATR (Answer To Reset)
                    atr = self.connection.getATR()
                    self.logger.info(f"Card detected, ATR: {toHexString(atr)}")
                    return True, "Card detected"
                    
                except NoCardException:
                    time.sleep(0.2)  # Wait before retry
                    continue
                except Exception as e:
                    self.logger.error(f"Error connecting to card: {e}")
                    time.sleep(0.2)
                    continue
            
            return False, "Timeout waiting for card"
            
        except Exception as e:
            self.logger.error(f"Error in wait_for_card: {e}")
            return False, f"Error: {str(e)}"
    
    def authenticate_block(self, block: int, key: List[int] = None) -> Tuple[bool, str]:
        """
        Authenticate a block using Key A
        
        Args:
            block: Block number to authenticate
            key: 6-byte authentication key (default: DEFAULT_KEY_A)
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        if self.connection is None:
            return False, "No card connected"
        
        if key is None:
            key = DEFAULT_KEY_A
        
        try:
            # Load authentication key into reader
            # Command: Load Key (FF 82 00 00 06 + 6 key bytes)
            load_key = [0xFF, 0x82, 0x00, 0x00, 0x06] + key
            data, sw1, sw2 = self.connection.transmit(load_key)
            
            if sw1 != 0x90 or sw2 != 0x00:
                return False, f"Failed to load key: {sw1:02X} {sw2:02X}"
            
            # Authenticate block
            # Command: Authenticate (FF 86 00 00 05 01 00 + block + 60 + key_number)
            # 60 = Key A, 61 = Key B
            auth_cmd = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, block, 0x60, 0x00]
            data, sw1, sw2 = self.connection.transmit(auth_cmd)
            
            if sw1 != 0x90 or sw2 != 0x00:
                return False, f"Authentication failed: {sw1:02X} {sw2:02X}"
            
            self.logger.info(f"Block {block} authenticated successfully")
            return True, f"Block {block} authenticated"
            
        except Exception as e:
            self.logger.error(f"Error authenticating block {block}: {e}")
            return False, f"Authentication error: {str(e)}"
    
    def read_block(self, block: int) -> Tuple[bool, Optional[bytes], str]:
        """
        Read 16 bytes from a block
        
        Args:
            block: Block number to read
            
        Returns:
            Tuple[bool, Optional[bytes], str]: (Success status, Data, Message)
        """
        if self.connection is None:
            return False, None, "No card connected"
        
        try:
            # Authenticate first
            success, msg = self.authenticate_block(block)
            if not success:
                return False, None, msg
            
            # Read binary block
            # Command: Read Binary (FF B0 00 + block + 10)
            read_cmd = [0xFF, 0xB0, 0x00, block, BLOCK_SIZE]
            data, sw1, sw2 = self.connection.transmit(read_cmd)
            
            if sw1 != 0x90 or sw2 != 0x00:
                return False, None, f"Read failed: {sw1:02X} {sw2:02X}"
            
            self.logger.info(f"Block {block} read: {toHexString(data)}")
            return True, bytes(data), f"Block {block} read successfully"
            
        except Exception as e:
            self.logger.error(f"Error reading block {block}: {e}")
            return False, None, f"Read error: {str(e)}"
    
    def write_block(self, block: int, data: bytes) -> Tuple[bool, str]:
        """
        Write 16 bytes to a block
        
        Args:
            block: Block number to write
            data: 16 bytes of data
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        if self.connection is None:
            return False, "No card connected"
        
        if len(data) != BLOCK_SIZE:
            return False, f"Data must be exactly {BLOCK_SIZE} bytes"
        
        try:
            # Authenticate first
            success, msg = self.authenticate_block(block)
            if not success:
                return False, msg
            
            # Update binary block
            # Command: Update Binary (FF D6 00 + block + 10 + 16 data bytes)
            write_cmd = [0xFF, 0xD6, 0x00, block, BLOCK_SIZE] + list(data)
            response, sw1, sw2 = self.connection.transmit(write_cmd)
            
            if sw1 != 0x90 or sw2 != 0x00:
                return False, f"Write failed: {sw1:02X} {sw2:02X}"
            
            self.logger.info(f"Block {block} written: {toHexString(data)}")
            return True, f"Block {block} written successfully"
            
        except Exception as e:
            self.logger.error(f"Error writing block {block}: {e}")
            return False, f"Write error: {str(e)}"
    
    def write_kanban(self, thread1: str, thread2: str) -> Tuple[bool, str]:
        """
        Write thread codes to Kanban card
        
        Args:
            thread1: Thread 1 code (max 16 characters)
            thread2: Thread 2 code (max 16 characters)
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        if self.connection is None:
            return False, "No card connected"
        
        # Validate inputs
        if len(thread1) > BLOCK_SIZE:
            return False, f"Thread 1 code too long (max {BLOCK_SIZE} chars)"
        if len(thread2) > BLOCK_SIZE:
            return False, f"Thread 2 code too long (max {BLOCK_SIZE} chars)"
        
        try:
            # Convert strings to bytes and pad with zeros
            thread1_bytes = thread1.encode('ascii').ljust(BLOCK_SIZE, b'\x00')
            thread2_bytes = thread2.encode('ascii').ljust(BLOCK_SIZE, b'\x00')
            
            # Write Thread 1 to Block 4
            success, msg = self.write_block(BLOCK_THREAD1, thread1_bytes)
            if not success:
                return False, f"Failed to write Thread 1: {msg}"
            
            # Write Thread 2 to Block 5
            success, msg = self.write_block(BLOCK_THREAD2, thread2_bytes)
            if not success:
                return False, f"Failed to write Thread 2: {msg}"
            
            # Verify written data
            success, msg = self.verify_data(thread1, thread2)
            if not success:
                return False, f"Verification failed: {msg}"
            
            return True, "Kanban card written and verified successfully"
            
        except Exception as e:
            self.logger.error(f"Error writing Kanban: {e}")
            return False, f"Write error: {str(e)}"
    
    def read_kanban(self) -> Tuple[bool, Optional[str], Optional[str], str]:
        """
        Read thread codes from Kanban card
        
        Returns:
            Tuple[bool, Optional[str], Optional[str], str]: 
                (Success status, Thread1, Thread2, Message)
        """
        if self.connection is None:
            return False, None, None, "No card connected"
        
        try:
            # Read Thread 1 from Block 4
            success, data1, msg = self.read_block(BLOCK_THREAD1)
            if not success:
                return False, None, None, f"Failed to read Thread 1: {msg}"
            
            # Read Thread 2 from Block 5
            success, data2, msg = self.read_block(BLOCK_THREAD2)
            if not success:
                return False, None, None, f"Failed to read Thread 2: {msg}"
            
            # Convert bytes to strings (strip null padding)
            thread1 = data1.decode('ascii', errors='ignore').rstrip('\x00')
            thread2 = data2.decode('ascii', errors='ignore').rstrip('\x00')
            
            return True, thread1, thread2, "Kanban card read successfully"
            
        except Exception as e:
            self.logger.error(f"Error reading Kanban: {e}")
            return False, None, None, f"Read error: {str(e)}"
    
    def verify_data(self, expected_thread1: str, expected_thread2: str) -> Tuple[bool, str]:
        """
        Verify that written data matches expected values
        
        Args:
            expected_thread1: Expected Thread 1 code
            expected_thread2: Expected Thread 2 code
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        success, actual_thread1, actual_thread2, msg = self.read_kanban()
        
        if not success:
            return False, f"Could not read card for verification: {msg}"
        
        if actual_thread1 != expected_thread1:
            return False, f"Thread 1 mismatch: expected '{expected_thread1}', got '{actual_thread1}'"
        
        if actual_thread2 != expected_thread2:
            return False, f"Thread 2 mismatch: expected '{expected_thread2}', got '{actual_thread2}'"
        
        return True, "Data verified successfully"
    
    def write_bypass(self) -> Tuple[bool, str]:
        """
        Write bypass mode to Kanban card
        
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        return self.write_kanban(BYPASS_KEYWORD, "")
    
    def clear_card(self) -> Tuple[bool, str]:
        """
        Clear Kanban data from card (write zeros)
        
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        try:
            # Write zeros to both blocks
            zero_data = b'\x00' * BLOCK_SIZE
            
            success, msg = self.write_block(BLOCK_THREAD1, zero_data)
            if not success:
                return False, f"Failed to clear Thread 1: {msg}"
            
            success, msg = self.write_block(BLOCK_THREAD2, zero_data)
            if not success:
                return False, f"Failed to clear Thread 2: {msg}"
            
            return True, "Card cleared successfully"
            
        except Exception as e:
            self.logger.error(f"Error clearing card: {e}")
            return False, f"Clear error: {str(e)}"
    
    def disconnect(self):
        """Disconnect from card and reader"""
        if self.connection is not None:
            try:
                self.connection.disconnect()
            except:
                pass
            self.connection = None
        
        self.reader = None
        self.logger.info("Disconnected from reader")
