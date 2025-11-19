from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import sqlite3
from datetime import datetime
import os

landing_app = Flask(__name__, template_folder='landing_templates')
landing_app.config['SECRET_KEY'] = 'landing-page-secret-key'

# Database for email collection
DOWNLOADS_DB = 'downloads.db'

def init_downloads_db():
    """Initialize downloads database"""
    conn = sqlite3.connect(DOWNLOADS_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            platform TEXT,
            subscribed BOOLEAN DEFAULT 1,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_downloads_db()

@landing_app.route('/')
def home():
    """Landing page"""
    return render_template('landing.html')

@landing_app.route('/download', methods=['POST'])
def download():
    """Handle download with optional email"""
    email = request.form.get('email', '').strip()
    platform = request.form.get('platform', 'windows')
    subscribe = request.form.get('subscribe', 'yes')
    
    # Store email if provided
    if email:
        conn = sqlite3.connect(DOWNLOADS_DB)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO downloads (email, platform, subscribed) VALUES (?, ?, ?)',
            (email, platform, subscribe == 'yes')
        )
        conn.commit()
        conn.close()
        print(f"Email saved: {email}")
    
    # Redirect to download file
    return redirect(url_for('download_file', platform=platform))

@landing_app.route('/download/<platform>')
def download_file(platform):
    """Serve download file"""
    downloads_folder = 'downloads'
    
    files = {
        'windows': 'HabitRecoder-Windows.exe',
        'mac': 'HabitRecoder-Mac.app.zip',
        'linux': 'HabitRecoder-Linux'
    }
    
    filename = files.get(platform, files['windows'])
    filepath = os.path.join(downloads_folder, filename)
    
    print(f"Looking for file: {filepath}")
    print(f"File exists: {os.path.exists(filepath)}")
    
    if os.path.exists(filepath):
        print(f"Sending file: {filename}")
        return send_file(filepath, as_attachment=True, download_name=filename)
    else:
        print(f"File not found: {filepath}")
        flash(f'Download file not ready yet for {platform}. Please check back soon!', 'error')
        return redirect('/')

@landing_app.route('/admin/emails')
def admin_emails():
    """View collected emails"""
    conn = sqlite3.connect(DOWNLOADS_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM downloads ORDER BY downloaded_at DESC')
    downloads = cursor.fetchall()
    conn.close()
    
    return render_template('admin_downloads.html', downloads=downloads)

@landing_app.route('/admin/export')
def admin_export():
    """Export emails as CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    conn = sqlite3.connect(DOWNLOADS_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM downloads ORDER BY downloaded_at DESC')
    downloads = cursor.fetchall()
    conn.close()
    
    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Email', 'Platform', 'Subscribed', 'Downloaded At'])
    
    for download in downloads:
        writer.writerow(download)
    
    output = si.getvalue()
    
    response = make_response(output)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=habit_recoder_downloads_{datetime.now().date()}.csv'
    
    return response

if __name__ == '__main__':
    print("=" * 50)
    print("Habit Re:coder Landing Page")
    print("=" * 50)
    print("\nStarting server...")
    print("Visit: http://127.0.0.1:8000")
    print("Admin: http://127.0.0.1:8000/admin/emails")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)
    landing_app.run(debug=True, port=8000)