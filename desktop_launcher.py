"""
Habit Re:coder - Desktop Launcher
Automatically opens the app in default browser
"""

import webbrowser
import time
import threading
import sys
import os

# Import the app DIRECTLY (not as subprocess)
from app_desktop import app

def open_browser():
    """Wait for server to start, then open browser"""
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    print("🌐 Opening browser...")
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("=" * 60)
    print("🎯 HABIT RE:CODER - DESKTOP EDITION")
    print("=" * 60)
    print("\n✅ No account required - works offline!")
    print("✅ All your data stays on this computer")
    print("✅ Complete privacy\n")
    print("Starting application...")
    print("Your browser will open automatically.\n")
    print("To stop the app:")
    print("  • Close this window, OR")
    print("  • Press Ctrl+C")
    print("=" * 60)
    print()
    
    # Open browser in separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run Flask app
    try:
        app.run(debug=False, use_reloader=False, port=5000, host='127.0.0.1')
    except KeyboardInterrupt:
        print("\n\n👋 Habit Re:coder closed. Goodbye!")
        sys.exit(0)