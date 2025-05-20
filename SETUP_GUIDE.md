# Detailed Setup Guide

## System Requirements
- Python 3.8 or higher
- Operating System: Windows 10+, macOS 10.15+, or Linux
- Minimum 2GB RAM
- Network: Local network access (for testing)

## Installation Steps

### 1. Python Setup
```bash
# Check Python version
python3 --version  # Should be 3.8 or higher

# Create virtual environment
python3 -m venv env

# Activate virtual environment
# On Windows:
env\Scripts\activate
# On macOS/Linux:
source env/bin/activate
```

### 2. Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Verify installations
python3 -c "import customtkinter; print('CustomTkinter version:', customtkinter.__version__)"
python3 -c "from PIL import Image; print('Pillow version:', Image.__version__)"
```

### 3. Network Configuration
- Default ports used:
  - Game Server: 4337
  - Lifeline Server: 4338

If these ports are in use:
1. Open `src/utils/config.py`
2. Modify `GAME_SERVER_PORT` and `LIFELINE_SERVER_PORT`
3. Ensure firewall allows these ports

### 4. Running the Application

#### Start Order
1. Lifeline Server
2. Game Server
3. Contestant GUI

```bash
# Terminal 1 - Lifeline Server
cd src
python3 lifeline_server.py

# Terminal 2 - Game Server
cd src
python3 game_server.py

# Terminal 3 - Contestant GUI
cd src
python3 contestant_gui.py
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Check if ports are in use
# On Windows:
netstat -ano | findstr :4337
netstat -ano | findstr :4338
# On macOS/Linux:
lsof -i :4337
lsof -i :4338

# Kill process if needed (replace PID)
# Windows:
taskkill /PID <PID> /F
# macOS/Linux:
kill -9 <PID>
```

2. **GUI Issues**
- If GUI doesn't appear:
  - Check Tkinter installation
  - Verify display server (X11/Wayland on Linux)
  - Try running with `python3 -X utf8 contestant_gui.py`

3. **Network Connection Failed**
- Verify all servers are running
- Check firewall settings
- Ensure localhost is accessible
- Try `ping localhost` to verify network

4. **Dependencies Issues**
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# If CustomTkinter fails:
pip install --upgrade customtkinter
```

## Testing the Setup

1. **Network Test**
```bash
# In src/utils directory
python3 -c "
import socket
s = socket.socket()
try:
    s.bind(('localhost', 4337))
    print('Port 4337 available')
except:
    print('Port 4337 in use')
s.close()
"
```

2. **GUI Test**
```bash
# In src directory
python3 -c "
import customtkinter
root = customtkinter.CTk()
root.title('Test Window')
root.geometry('300x200')
label = customtkinter.CTkLabel(root, text='GUI Test')
label.pack()
root.after(2000, root.destroy)
root.mainloop()
"
```

## Development Environment

For the best development experience:
- Use VS Code with Python extension
- Enable Python linting
- Set up auto-formatting with Black
- Configure debugger for Python

## Additional Resources
- CustomTkinter Documentation: https://customtkinter.tomschimansky.com/
- Python Socket Programming: https://docs.python.org/3/howto/sockets.html
- Tkinter Tutorial: https://docs.python.org/3/library/tkinter.html 