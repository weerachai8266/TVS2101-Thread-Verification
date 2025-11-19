"""
CWT Thread Verification System - Kanban Tool
Main application for writing and reading Kanban cards using ACR122U RFID reader

Author: CWT Team
Version: 1.0.0
License: MIT
"""

import tkinter as tk
import logging
import sys
from typing import Optional

from gui import KanbanGUI
from rfid_manager import RFIDManager
from config import APP_TITLE, BYPASS_KEYWORD


class KanbanToolApp:
    """Main application controller"""
    
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Create main window
        self.root = tk.Tk()
        self.gui = KanbanGUI(self.root)
        
        # Create RFID manager
        self.rfid = RFIDManager()
        
        # Connect GUI callbacks
        self.gui.on_write_kanban = self.write_kanban
        self.gui.on_read_kanban = self.read_kanban
        self.gui.on_write_bypass = self.write_bypass
        self.gui.on_clear_card = self.clear_card
        
        # Initialize reader
        self.initialize_reader()
    
    def initialize_reader(self):
        """Initialize RFID reader connection"""
        self.gui.log("Initializing RFID reader...", 'info')
        
        success, msg = self.rfid.connect_reader()
        
        if success:
            self.gui.log(msg, 'success')
            self.gui.set_reader_status("Connected", True)
        else:
            self.gui.log(msg, 'error')
            self.gui.set_reader_status("Not Connected", False)
            self.gui.show_warning(
                "Reader Not Found",
                "ACR122U reader not detected.\n\n"
                "Please connect the reader and restart the application.\n\n"
                "You can still use the interface, but card operations will fail."
            )
    
    def wait_for_card(self) -> bool:
        """
        Wait for card to be placed on reader
        
        Returns:
            bool: True if card detected, False otherwise
        """
        self.gui.log("Waiting for card... Please place card on reader.", 'info')
        self.gui.set_card_status("Waiting...", False)
        
        # Allow GUI to update
        self.root.update()
        
        success, msg = self.rfid.wait_for_card(timeout=10)
        
        if success:
            self.gui.log(msg, 'success')
            self.gui.set_card_status("Card Detected", True)
            return True
        else:
            self.gui.log(msg, 'warning')
            self.gui.set_card_status("No Card", False)
            return False
    
    def write_kanban(self, thread1: str, thread2: str):
        """
        Write thread codes to Kanban card
        
        Args:
            thread1: Thread 1 code
            thread2: Thread 2 code
        """
        self.gui.log(f"Writing Kanban: Thread1='{thread1}', Thread2='{thread2}'", 'info')
        
        # Wait for card
        if not self.wait_for_card():
            self.gui.show_error(
                "No Card Detected",
                "Please place a card on the reader and try again."
            )
            return
        
        # Write data
        success, msg = self.rfid.write_kanban(thread1, thread2)
        
        if success:
            self.gui.log(msg, 'success')
            self.gui.show_success(
                "Success",
                f"Kanban card written successfully!\n\n"
                f"Thread 1: {thread1}\n"
                f"Thread 2: {thread2}"
            )
        else:
            self.gui.log(f"Failed to write Kanban: {msg}", 'error')
            self.gui.show_error(
                "Write Failed",
                f"Failed to write Kanban card.\n\n{msg}"
            )
        
        # Disconnect from card
        self.rfid.disconnect()
        self.gui.set_card_status("No Card", False)
    
    def read_kanban(self):
        """Read and display thread codes from Kanban card"""
        self.gui.log("Reading Kanban card...", 'info')
        
        # Wait for card
        if not self.wait_for_card():
            self.gui.show_error(
                "No Card Detected",
                "Please place a card on the reader and try again."
            )
            return
        
        # Read data
        success, thread1, thread2, msg = self.rfid.read_kanban()
        
        if success:
            self.gui.log(msg, 'success')
            self.gui.log(f"Thread 1: {thread1}", 'info')
            self.gui.log(f"Thread 2: {thread2}", 'info')
            
            # Update GUI inputs
            self.gui.set_thread_values(thread1, thread2)
            
            # Show results
            if thread1.lower() == BYPASS_KEYWORD.lower():
                self.gui.show_warning(
                    "Bypass Card",
                    "This is a BYPASS card.\n\n"
                    "Machine will operate without verification."
                )
            else:
                self.gui.show_success(
                    "Card Read Successfully",
                    f"Thread 1: {thread1}\n"
                    f"Thread 2: {thread2}"
                )
        else:
            self.gui.log(f"Failed to read Kanban: {msg}", 'error')
            self.gui.show_error(
                "Read Failed",
                f"Failed to read Kanban card.\n\n{msg}"
            )
        
        # Disconnect from card
        self.rfid.disconnect()
        self.gui.set_card_status("No Card", False)
    
    def write_bypass(self):
        """Write bypass mode to card"""
        self.gui.log("Writing BYPASS card...", 'warning')
        
        # Wait for card
        if not self.wait_for_card():
            self.gui.show_error(
                "No Card Detected",
                "Please place a card on the reader and try again."
            )
            return
        
        # Write bypass
        success, msg = self.rfid.write_bypass()
        
        if success:
            self.gui.log("BYPASS card written successfully", 'success')
            self.gui.show_success(
                "Success",
                "BYPASS card written successfully!\n\n"
                "⚠️ WARNING: This card will bypass all verification.\n"
                "Use only for maintenance or special operations."
            )
        else:
            self.gui.log(f"Failed to write BYPASS: {msg}", 'error')
            self.gui.show_error(
                "Write Failed",
                f"Failed to write BYPASS card.\n\n{msg}"
            )
        
        # Disconnect from card
        self.rfid.disconnect()
        self.gui.set_card_status("No Card", False)
    
    def clear_card(self):
        """Clear all data from card"""
        self.gui.log("Clearing card...", 'info')
        
        # Wait for card
        if not self.wait_for_card():
            self.gui.show_error(
                "No Card Detected",
                "Please place a card on the reader and try again."
            )
            return
        
        # Clear data
        success, msg = self.rfid.clear_card()
        
        if success:
            self.gui.log(msg, 'success')
            self.gui.show_success(
                "Success",
                "Card cleared successfully!"
            )
        else:
            self.gui.log(f"Failed to clear card: {msg}", 'error')
            self.gui.show_error(
                "Clear Failed",
                f"Failed to clear card.\n\n{msg}"
            )
        
        # Disconnect from card
        self.rfid.disconnect()
        self.gui.set_card_status("No Card", False)
    
    def run(self):
        """Start the application"""
        self.gui.log("=== CWT Thread Verification - Kanban Tool ===", 'info')
        self.gui.log("Ready to use. Please ensure ACR122U reader is connected.", 'info')
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        app = KanbanToolApp()
        app.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
