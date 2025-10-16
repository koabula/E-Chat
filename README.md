# E-Chat
[中文](README_CN.md) | [English](README.md)

---

An instant messaging software based on email protocols

## Project Introduction

E-Chat is an email instant messaging client that implements real-time communication through SMTP/IMAP protocols. The software features a modern interface design and provides a smooth chatting experience.

## System Requirements

- Python 3.8 or higher
- Windows/macOS/Linux

## Installation Instructions

1. Clone the project to local
```bash
git clone https://github.com/koabula/E-Chat.git
cd E-Chat
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the program
```bash
python main.py
```

## Project Structure

```
E-Chat/
├── main.py              # Program entry point
├── requirements.txt     # Dependencies list
├── src/                 # Core source code
│   ├── app.py          # Main application class
│   ├── config_manager.py    # Configuration management
│   ├── database_manager.py  # Database management
│   ├── email_manager.py     # Email sending/receiving management
│   ├── language_manager.py  # Multi-language management
│   ├── message_parser.py    # Message parsing
│   └── utils.py            # Utility functions
└─── ui/                  # User interface
    ├── main_window.py      # Main window
    ├── chat_interface.py   # Chat interface
    ├── chat_list.py        # Contact list
    ├── sidebar.py          # Sidebar
    ├── settings_window.py  # Settings window
    └── components/         # UI components
```

## Usage Instructions

1. **Initial Configuration**: After starting the program, configure email server information in settings
2. **Add Contacts**: Add chat contacts through the sidebar
3. **Send Messages**: Type messages in the chat interface and send
4. **Receive Messages**: The program automatically polls for new messages

## Configuration Requirements

The following email server information needs to be configured:
- SMTP server address and port
- IMAP server address and port
- Email account and password (some email providers may require authorization codes)

## License

This project is open source under the MIT License. See [LICENSE](LICENSE) file for details.

## Version History

- **v1.0.0** - Initial version with basic chat functionality implementation
