import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
from PIL import Image, ImageTk
from db_config import DatabaseConfig

class PasswordManagerApp:
    def __init__(self, root):
        # Initialize the main window
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("500x400")

        # Set the application icon
        try:
            icon = Image.open("icons/logo.png")
            icon = ImageTk.PhotoImage(icon)
            self.root.iconphoto(True, icon)
        except:
            pass
        
        # Initialize database connection and password visibility state
        self.db = DatabaseConfig()
        self.password_visible = False
        
        # Set up the user interface and load existing passwords
        self.setup_ui()
        self.load_passwords()

    def setup_ui(self):
        # Create the main container with scrollbars
        # This allows the content to be scrollable if it exceeds the window size
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add vertical scrollbar
        main_scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL)
        main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create canvas for scrolling
        self.main_canvas = tk.Canvas(main_container, yscrollcommand=main_scrollbar.set)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbar to work with canvas
        main_scrollbar.config(command=self.main_canvas.yview)
        
        # Create main frame inside canvas
        self.main_frame = ttk.Frame(self.main_canvas, padding="10")
        self.main_canvas.create_window((0, 0), window=self.main_frame, anchor=tk.NW, width=self.main_canvas.winfo_reqwidth())
        
        # Create the password list and buttons
        self.create_password_tree()
        self.create_buttons()
        
        # Set up event handlers for resizing and scrolling
        self.main_frame.bind("<Configure>", self.on_frame_configure)
        self.main_canvas.bind("<Configure>", self.on_canvas_configure)
        self.root.bind("<Configure>", self.on_window_resize)

    def on_frame_configure(self, event=None):
        # Update the scrollable region when the frame size changes
        # This ensures all content remains accessible through scrolling
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        self.main_canvas.itemconfig(self.main_canvas.find_withtag("all")[0], width=self.main_canvas.winfo_width())

    def on_canvas_configure(self, event):
        # Update the canvas width when the window is resized
        # This ensures the content fills the available space
        self.main_canvas.itemconfig(self.main_canvas.find_withtag("all")[0], width=event.width)

    def on_window_resize(self, event):
        # Handle window resize events
        # Adjust the canvas width to account for the scrollbar
        if event.widget == self.root:
            self.main_canvas.configure(width=event.width - 30)

    def create_password_tree(self):
        # Create a frame to hold the treeview and its scrollbars
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add vertical scrollbar for the treeview
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add horizontal scrollbar for the treeview
        tree_scrollbar_h = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Define columns for the treeview
        columns = ("website", "email", "password", "notes")
        
        # Create the treeview widget
        # This displays the password entries in a table format
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", 
                                 yscrollcommand=tree_scrollbar.set, 
                                 xscrollcommand=tree_scrollbar_h.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars to work with the treeview
        tree_scrollbar.config(command=self.tree.yview)
        tree_scrollbar_h.config(command=self.tree.xview)
        
        # Set fixed column widths
        self.tree.column("website", width=100, minwidth=100)
        self.tree.column("email", width=100, minwidth=100)
        self.tree.column("password", width=100, minwidth=100)
        self.tree.column("notes", width=100, minwidth=100)
        
        # Set column headings
        self.tree.heading("website", text="Website")
        self.tree.heading("email", text="Email")
        self.tree.heading("password", text="Password")
        self.tree.heading("notes", text="Notes")

    def create_buttons(self):
        # Create a frame to hold all buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Create a container for the buttons to ensure proper alignment
        button_container = ttk.Frame(button_frame)
        button_container.pack(fill=tk.X, expand=True)
        
        # Add buttons for password management actions
        ttk.Button(button_container, text="Add", 
                  command=self.add_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_container, text="Edit", 
                  command=self.edit_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_container, text="Delete", 
                  command=self.delete_password).pack(side=tk.LEFT, padx=5)
        
        # Add button to toggle password visibility
        self.toggle_password_button = ttk.Button(button_container, 
                                               text="Show",
                                               command=self.toggle_password_visibility)
        self.toggle_password_button.pack(side=tk.LEFT, padx=5)
        
        # Add button to copy password to clipboard
        ttk.Button(button_container, text="Copy", 
                  command=self.copy_password).pack(side=tk.LEFT, padx=5)

    def toggle_password_visibility(self):
        # Get the selected password entry
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an entry first")
            return
            
        # Get the website name from the selected entry
        item = self.tree.item(selected[0])
        website = item["values"][0]
        
        # Retrieve the actual password from the database
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM passwords WHERE website = ?", (website,))
        result = cursor.fetchone()
        conn.close()
        
        # Toggle between showing and hiding the password
        if result:
            password = result[0]
            if self.password_visible:
                # Hide the password
                self.tree.set(selected[0], "password", "********")
                self.toggle_password_button["text"] = "Show"
            else:
                # Show the password
                self.tree.set(selected[0], "password", password)
                self.toggle_password_button["text"] = "Hide"
            self.password_visible = not self.password_visible

    def add_password(self):
        # Open the password dialog in add mode
        self.open_password_dialog()

    def edit_password(self):
        # Check if an entry is selected
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an entry first")
            return
        # Open the password dialog in edit mode
        self.open_password_dialog(selected[0])

    def delete_password(self):
        # Check if an entry is selected
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an entry first")
            return
        
        # Ask for confirmation before deleting
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete this entry?"):
            # Get the website name from the selected entry
            item = self.tree.item(selected[0])
            website = item["values"][0]
            
            # Delete the entry from the database
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM passwords WHERE website = ?", (website,))
            conn.commit()
            conn.close()
            
            # Refresh the password list
            self.load_passwords()

    def copy_password(self):
        # Check if an entry is selected
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an entry first")
            return
        
        # Get the website name from the selected entry
        item = self.tree.item(selected[0])
        website = item["values"][0]
        
        # Retrieve the password from the database
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM passwords WHERE website = ?", (website,))
        result = cursor.fetchone()
        conn.close()
        
        # Copy the password to the clipboard
        if result:
            password = result[0]
            pyperclip.copy(password)
            messagebox.showinfo("Info", "Password copied to clipboard")

    def open_password_dialog(self, item_id=None):
        # Create a new window for adding/editing passwords
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Password" if item_id is None else "Edit Password")
        dialog.geometry("400x300")
        dialog.minsize(350, 250)
        
        # Create input fields for password details
        ttk.Label(dialog, text="Website").grid(row=0, column=0, padx=5, pady=5)
        website_entry = ttk.Entry(dialog)
        website_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(dialog, text="Email").grid(row=1, column=0, padx=5, pady=5)
        email_entry = ttk.Entry(dialog)
        email_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(dialog, text="Password").grid(row=2, column=0, padx=5, pady=5)
        password_entry = ttk.Entry(dialog, show="*")
        password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Function to toggle password visibility in the dialog
        def toggle_password_visibility():
            if password_entry["show"] == "*":
                password_entry["show"] = ""
                show_password_button["text"] = "Hide"
            else:
                password_entry["show"] = "*"
                show_password_button["text"] = "Show"
        
        # Add button to toggle password visibility
        show_password_button = ttk.Button(dialog, text="Show", 
                                        command=toggle_password_visibility)
        show_password_button.grid(row=2, column=2, padx=5, pady=5)
        
        ttk.Label(dialog, text="Notes").grid(row=3, column=0, padx=5, pady=5)
        notes_entry = ttk.Entry(dialog)
        notes_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # Create buttons for saving or canceling
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Save", 
                  command=lambda: save()).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure the dialog layout
        dialog.grid_columnconfigure(1, weight=1)
        
        def save():
            # Get values from input fields
            website = website_entry.get()
            email = email_entry.get()
            password = password_entry.get()
            notes = notes_entry.get()
            
            # Validate required fields
            if not website or not password:
                messagebox.showwarning("Warning", "Website and password are required")
                return
            
            # Save the password entry to the database
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if item_id is None:
                # Insert new password entry
                cursor.execute("""
                    INSERT INTO passwords (website, email, password, notes)
                    VALUES (?, ?, ?, ?)
                """, (website, email, password, notes))
            else:
                # Update existing password entry
                cursor.execute("""
                    UPDATE passwords
                    SET website = ?, email = ?, password = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE website = ?
                """, (website, email, password, notes, self.tree.item(item_id)["values"][0]))
            
            # Save changes and close the connection
            conn.commit()
            conn.close()
            
            # Refresh the password list and close the dialog
            self.load_passwords()
            dialog.destroy()
        
        if item_id is not None:
            # Load existing values for editing
            values = self.tree.item(item_id)["values"]
            website_entry.insert(0, values[0])
            email_entry.insert(0, values[1])
            
            # Get the actual password from the database
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM passwords WHERE website = ?", (values[0],))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                password_entry.insert(0, result[0])
            else:
                password_entry.insert(0, values[2])
                
            notes_entry.insert(0, values[3])

    def load_passwords(self):
        # Retrieve all passwords from the database
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM passwords ORDER BY website")
        
        # Clear existing items from the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add each password entry to the treeview
        for row in cursor.fetchall():
            values = list(row[1:5])
            if not self.password_visible:
                values[2] = "********"
            self.tree.insert("", "end", values=values)
        
        # Close the database connection
        conn.close()

if __name__ == "__main__":
    # Create and run the application
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop() 