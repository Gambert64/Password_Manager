# Password Manager

A simple password manager application with a graphical user interface. Store and manage your passwords securely.

## Features

- Store website credentials (website, email, password, notes)
- View, edit, and delete password entries
- Copy passwords to clipboard
- Toggle password visibility
- Responsive interface with scrollable content

## Requirements

- Python 3.x
- Required packages:
  - Pillow==10.2.0
  - pyperclip==1.8.2

## Installation

1. Clone this repository or download the files
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python password_manager.py
```

## Database

Passwords are stored locally in an SQLite database created in the `data/` folder. The database is automatically created when you first run the application.

## Security Note

This application stores passwords in plain text. However, since all data is stored locally on your device and not transmitted over the internet, it remains relatively secure for personal use. For storing highly sensitive information, using an encrypted password manager is recommended.
