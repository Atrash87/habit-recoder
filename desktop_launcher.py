"""
Habit Re:coder - Desktop Launcher
Automatically opens the app in default browser
"""

import webbrowser
import time
import threading
from app_desktop import app  # Use desktop version instead
import config

def open_browser():
    """Wait for server to start, then open browser"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("=" * 50)
    print("🎯 Habit Re:coder - Desktop Edition")
    print("=" * 50)
    print("\n✅ No account required - works offline!")
    print("✅ All your data stays on this computer")
    print("✅ Complete privacy\n")
    print("Starting application...")
    print("Your browser will open automatically.\n")
    print("To stop the app: Close this window or press Ctrl+C")
    print("=" * 50)
    
    # Open browser in separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run Flask app
    app.run(debug=False, use_reloader=False, port=5000)