"""
CWT Thread Verification System - GUI Module
Tkinter-based graphical user interface for Kanban card management
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from typing import Callable, Optional

from config import (
    APP_TITLE, APP_VERSION, APP_WIDTH, APP_HEIGHT,
    COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, COLOR_INFO, COLOR_BG
)


class KanbanGUI:
    """Main GUI window for Kanban card tool"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.resizable(False, False)
        
        # Callbacks to be set by main application
        self.on_write_kanban: Optional[Callable] = None
        self.on_read_kanban: Optional[Callable] = None
        self.on_write_bypass: Optional[Callable] = None
        self.on_clear_card: Optional[Callable] = None
        
        # Status variables
        self.reader_status = tk.StringVar(value="Not Connected")
        self.card_status = tk.StringVar(value="No Card")
        
        # Thread input variables
        self.thread1_var = tk.StringVar()
        self.thread2_var = tk.StringVar()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Create sections
        self._create_header(main_frame)
        self._create_status_section(main_frame)
        self._create_input_section(main_frame)
        self._create_button_section(main_frame)
        self._create_log_section(main_frame)
    
    def _create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(
            header_frame,
            text="CWT Thread Verification",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0)
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Kanban Card Management Tool",
            font=('Arial', 10)
        )
        subtitle_label.grid(row=1, column=0)
        
        version_label = ttk.Label(
            header_frame,
            text=f"Version {APP_VERSION}",
            font=('Arial', 8),
            foreground='gray'
        )
        version_label.grid(row=2, column=0)
    
    def _create_status_section(self, parent):
        """Create status indicators section"""
        status_frame = ttk.LabelFrame(parent, text="Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Reader status
        ttk.Label(status_frame, text="Reader:").grid(row=0, column=0, sticky=tk.W)
        reader_label = ttk.Label(
            status_frame,
            textvariable=self.reader_status,
            font=('Arial', 10, 'bold')
        )
        reader_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Card status
        ttk.Label(status_frame, text="Card:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        card_label = ttk.Label(
            status_frame,
            textvariable=self.card_status,
            font=('Arial', 10, 'bold')
        )
        card_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
    
    def _create_input_section(self, parent):
        """Create thread input section"""
        input_frame = ttk.LabelFrame(parent, text="Thread Codes", padding="10")
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Thread 1 input
        ttk.Label(input_frame, text="Thread 1:").grid(row=0, column=0, sticky=tk.W)
        thread1_entry = ttk.Entry(
            input_frame,
            textvariable=self.thread1_var,
            font=('Arial', 11),
            width=30
        )
        thread1_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        # Thread 1 length indicator
        thread1_length = ttk.Label(input_frame, text="0/16", foreground='gray')
        thread1_length.grid(row=0, column=2, padx=(5, 0))
        
        # Update length indicator
        def update_thread1_length(*args):
            length = len(self.thread1_var.get())
            thread1_length.config(
                text=f"{length}/16",
                foreground='red' if length > 16 else 'gray'
            )
        self.thread1_var.trace('w', update_thread1_length)
        
        # Thread 2 input
        ttk.Label(input_frame, text="Thread 2:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        thread2_entry = ttk.Entry(
            input_frame,
            textvariable=self.thread2_var,
            font=('Arial', 11),
            width=30
        )
        thread2_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))
        
        # Thread 2 length indicator
        thread2_length = ttk.Label(input_frame, text="0/16", foreground='gray')
        thread2_length.grid(row=1, column=2, padx=(5, 0), pady=(10, 0))
        
        # Update length indicator
        def update_thread2_length(*args):
            length = len(self.thread2_var.get())
            thread2_length.config(
                text=f"{length}/16",
                foreground='red' if length > 16 else 'gray'
            )
        self.thread2_var.trace('w', update_thread2_length)
        
        # Example text
        example_label = ttk.Label(
            input_frame,
            text="Example: TH-001, TH-RED-100, etc. (Max 16 characters)",
            font=('Arial', 8),
            foreground='gray'
        )
        example_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
    
    def _create_button_section(self, parent):
        """Create action buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)
        
        # Write Kanban button
        write_btn = ttk.Button(
            button_frame,
            text="📝 Write Kanban",
            command=self._handle_write_kanban
        )
        write_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Read Kanban button
        read_btn = ttk.Button(
            button_frame,
            text="📖 Read Kanban",
            command=self._handle_read_kanban
        )
        read_btn.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Write Bypass button
        bypass_btn = ttk.Button(
            button_frame,
            text="⚡ Write Bypass",
            command=self._handle_write_bypass
        )
        bypass_btn.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Clear Card button
        clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Clear Card",
            command=self._handle_clear_card
        )
        clear_btn.grid(row=0, column=3, sticky=(tk.W, tk.E))
    
    def _create_log_section(self, parent):
        """Create log display section"""
        log_frame = ttk.LabelFrame(parent, text="Activity Log", padding="10")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Configure parent to expand log section
        parent.rowconfigure(4, weight=1)
        
        # Scrolled text widget for log
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=('Consolas', 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for colored output
        self.log_text.tag_config('success', foreground=COLOR_SUCCESS)
        self.log_text.tag_config('error', foreground=COLOR_ERROR)
        self.log_text.tag_config('warning', foreground=COLOR_WARNING)
        self.log_text.tag_config('info', foreground=COLOR_INFO)
    
    def _handle_write_kanban(self):
        """Handle Write Kanban button click"""
        if self.on_write_kanban:
            thread1 = self.thread1_var.get().strip()
            thread2 = self.thread2_var.get().strip()
            
            if not thread1 or not thread2:
                messagebox.showwarning(
                    "Invalid Input",
                    "Please enter both Thread 1 and Thread 2 codes."
                )
                return
            
            if len(thread1) > 16 or len(thread2) > 16:
                messagebox.showerror(
                    "Invalid Input",
                    "Thread codes must be 16 characters or less."
                )
                return
            
            self.on_write_kanban(thread1, thread2)
    
    def _handle_read_kanban(self):
        """Handle Read Kanban button click"""
        if self.on_read_kanban:
            self.on_read_kanban()
    
    def _handle_write_bypass(self):
        """Handle Write Bypass button click"""
        if self.on_write_bypass:
            result = messagebox.askyesno(
                "Confirm Bypass",
                "This will write a bypass card that skips verification.\n\n"
                "Are you sure you want to continue?"
            )
            if result:
                self.on_write_bypass()
    
    def _handle_clear_card(self):
        """Handle Clear Card button click"""
        if self.on_clear_card:
            result = messagebox.askyesno(
                "Confirm Clear",
                "This will erase all data from the card.\n\n"
                "Are you sure you want to continue?"
            )
            if result:
                self.on_clear_card()
    
    def log(self, message: str, level: str = 'info'):
        """
        Add message to log display
        
        Args:
            message: Message to log
            level: Log level ('info', 'success', 'warning', 'error')
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, full_message, level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def set_reader_status(self, status: str, connected: bool = False):
        """Update reader status indicator"""
        self.reader_status.set(status)
    
    def set_card_status(self, status: str, present: bool = False):
        """Update card status indicator"""
        self.card_status.set(status)
    
    def set_thread_values(self, thread1: str, thread2: str):
        """Set thread input values"""
        self.thread1_var.set(thread1)
        self.thread2_var.set(thread2)
    
    def clear_inputs(self):
        """Clear thread input fields"""
        self.thread1_var.set("")
        self.thread2_var.set("")
    
    def show_error(self, title: str, message: str):
        """Show error dialog"""
        messagebox.showerror(title, message)
    
    def show_success(self, title: str, message: str):
        """Show success dialog"""
        messagebox.showinfo(title, message)
    
    def show_warning(self, title: str, message: str):
        """Show warning dialog"""
        messagebox.showwarning(title, message)
