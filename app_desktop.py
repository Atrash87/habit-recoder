from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from database.db_helper import init_db, get_connection
from datetime import datetime, timedelta
import config

print("🚀 Initializing Habit Re:coder Desktop...")

# Create Flask app FIRST
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Initialize database
print("📊 Initializing database...")
init_db()

# Desktop mode - single user (no login required)
DESKTOP_USER_ID = 1

print("📁 Importing controllers...")
# Import controllers AFTER app is defined
from controllers.habit_controller import (
    create_habit, get_all_habits, get_habit_by_id, 
    delete_habit, mark_habit_complete, get_habit_streak,
    is_completed_today, get_habit_logs, get_completion_stats,
    update_habit
)
from controllers.journal_controller import (
    create_or_update_journal_entry, get_journal_entry_by_date,
    get_all_journal_entries, search_journal_entries,
    get_all_tags, delete_journal_entry
)
from controllers.report_controller import generate_report_data, format_report_as_text

print("✅ Controllers imported successfully")

# Create desktop user
print("👤 Setting up desktop user...")
conn = get_connection()
cursor = conn.cursor()
try:
    cursor.execute('SELECT id FROM users WHERE id = ?', (DESKTOP_USER_ID,))
    if not cursor.fetchone():
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        password_hash = bcrypt.generate_password_hash('desktop').decode('utf-8')
        cursor.execute(
            'INSERT INTO users (id, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
            (DESKTOP_USER_ID, 'desktop@local', password_hash, 0)
        )
        conn.commit()
        print("✅ Desktop user created")
except Exception as e:
    print(f"ℹ️ User already exists or error: {e}")
finally:
    conn.close()

print("✅ Desktop app ready!")

# ============================================
# SIMPLE SHUTDOWN HANDLER (SAFE)
# ============================================

@app.route('/shutdown')
def shutdown():
    """Simple shutdown route - just shows message"""
    return """
    <html>
        <head>
            <title>App Closed</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .message { 
                    background: rgba(255,255,255,0.1); 
                    padding: 40px; 
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.2);
                }
                .btn {
                    display: inline-block;
                    padding: 12px 30px;
                    background: white;
                    color: #667eea;
                    text-decoration: none;
                    border-radius: 25px;
                    margin: 10px;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="message">
                <h1>👋 Application Closed</h1>
                <p>You can safely close this browser tab.</p>
                <p>The app will continue running in the background.</p>
                <br>
                <a href="/" class="btn">↩️ Back to App</a>
                <br><br>
                <small>To fully quit: Close this window and stop the app from system tray or task manager</small>
            </div>
        </body>
    </html>
    """

# ============================================
# ROUTES (Your existing routes)
# ============================================

@app.route('/')
def index():
    """Home page - show all habits and today's journal"""
    try:
        habits = get_all_habits(DESKTOP_USER_ID)
        today = datetime.now().strftime('%A, %B %d, %Y')
        today_date = datetime.now().date()
        
        habits_data = []
        total_habits = len(habits)
        completed_today = 0
        
        for habit in habits:
            is_complete = is_completed_today(habit.id)
            if is_complete:
                completed_today += 1
                
            habits_data.append({
                'habit': habit,
                'streak': get_habit_streak(habit.id),
                'completed_today': is_complete
            })
        
        completion_percentage = (completed_today / total_habits * 100) if total_habits > 0 else 0
        journal_entry = get_journal_entry_by_date(DESKTOP_USER_ID, today_date)
        dark_mode = session.get('dark_mode', False)
        
        return render_template('index_desktop.html', 
                             habits_data=habits_data, 
                             today=today,
                             today_date=today_date,
                             completion_percentage=round(completion_percentage),
                             completed_today=completed_today,
                             total_habits=total_habits,
                             journal_entry=journal_entry,
                             dark_mode=dark_mode,
                             app_name=config.APP_NAME)
    except Exception as e:
        print(f"Error in index route: {e}")
        return f"Error loading page: {e}", 500

@app.route('/toggle_dark_mode')
def toggle_dark_mode():
    """Toggle dark mode"""
    session['dark_mode'] = not session.get('dark_mode', False)
    return redirect(request.referrer or url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add_habit():
    """Add new habit"""
    if request.method == 'POST':
        name = request.form.get('name')
        frequency = request.form.get('frequency')
        target_time = request.form.get('target_time')
        icon = request.form.get('icon')
        motivation = request.form.get('motivation')
        challenges = request.form.get('challenges')
        ai_notes = request.form.get('ai_notes')
        
        if name and frequency:
            create_habit(DESKTOP_USER_ID, name, frequency, target_time, icon, motivation, challenges, ai_notes)
            flash('Habit added successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please fill in all required fields', 'error')
    
    dark_mode = session.get('dark_mode', False)
    return render_template('add_habit.html', dark_mode=dark_mode, app_name=config.APP_NAME)

@app.route('/habit/<int:habit_id>')
def view_habit(habit_id):
    """View detailed habit information"""
    habit = get_habit_by_id(habit_id)
    if not habit:
        flash('Habit not found', 'error')
        return redirect(url_for('index'))
    
    logs = get_habit_logs(habit_id)
    stats = get_completion_stats(habit_id)
    streak = get_habit_streak(habit_id)
    
    dark_mode = session.get('dark_mode', False)
    return render_template('view_habit.html', habit=habit, logs=logs, stats=stats, streak=streak, dark_mode=dark_mode, app_name=config.APP_NAME)

@app.route('/edit/<int:habit_id>', methods=['GET', 'POST'])
def edit_habit(habit_id):
    """Edit existing habit"""
    habit = get_habit_by_id(habit_id)
    if not habit:
        flash('Habit not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        frequency = request.form.get('frequency')
        target_time = request.form.get('target_time')
        icon = request.form.get('icon')
        motivation = request.form.get('motivation')
        challenges = request.form.get('challenges')
        ai_notes = request.form.get('ai_notes')
        
        if name and frequency:
            update_habit(habit_id, name, frequency, target_time, icon, motivation, challenges, ai_notes)
            flash('Habit updated successfully!', 'success')
            return redirect(url_for('view_habit', habit_id=habit_id))
        else:
            flash('Please fill in all required fields', 'error')
    
    dark_mode = session.get('dark_mode', False)
    return render_template('edit_habit.html', habit=habit, dark_mode=dark_mode, app_name=config.APP_NAME)

@app.route('/complete/<int:habit_id>', methods=['GET', 'POST'])
def complete_habit(habit_id):
    """Mark habit as complete with mood and note"""
    if request.method == 'POST':
        mood = request.form.get('mood')
        note = request.form.get('note')
        
        success = mark_habit_complete(habit_id, mood, note)
        if success:
            flash('Habit marked as complete! 🎉', 'success')
        else:
            flash('Already completed today!', 'info')
        
        return redirect(url_for('index'))
    
    habit = get_habit_by_id(habit_id)
    if not habit:
        flash('Habit not found', 'error')
        return redirect(url_for('index'))
    
    dark_mode = session.get('dark_mode', False)
    return render_template('complete_habit.html', habit=habit, dark_mode=dark_mode, app_name=config.APP_NAME)

@app.route('/delete/<int:habit_id>')
def delete_habit_route(habit_id):
    """Delete a habit"""
    delete_habit(habit_id)
    flash('Habit deleted', 'info')
    return redirect(url_for('index'))

@app.route('/journal', methods=['GET'])
def journal():
    """View all journal entries"""
    search_term = request.args.get('search', '')
    
    if search_term:
        entries = search_journal_entries(DESKTOP_USER_ID, search_term)
    else:
        entries = get_all_journal_entries(DESKTOP_USER_ID)
    
    all_tags = get_all_tags(DESKTOP_USER_ID)
    dark_mode = session.get('dark_mode', False)
    
    return render_template('journal.html', entries=entries, all_tags=all_tags, search_term=search_term, dark_mode=dark_mode, app_name=config.APP_NAME)

@app.route('/journal/save', methods=['POST'])
def save_journal():
    """Save or update journal entry"""
    entry_date = request.form.get('entry_date')
    content = request.form.get('content')
    tags = request.form.get('tags')
    
    if entry_date and content:
        create_or_update_journal_entry(DESKTOP_USER_ID, entry_date, content, tags)
        flash('Journal entry saved!', 'success')
    else:
        flash('Please fill in the content', 'error')
    
    if request.form.get('from_dashboard'):
        return redirect(url_for('index'))
    
    return redirect(url_for('journal'))

@app.route('/journal/delete/<entry_date>')
def delete_journal(entry_date):
    """Delete a journal entry"""
    delete_journal_entry(DESKTOP_USER_ID, entry_date)
    flash('Journal entry deleted', 'info')
    return redirect(url_for('journal'))

@app.route('/generate_report')
def generate_report():
    """Generate and download text report"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        print(f"📊 Generating report for user {DESKTOP_USER_ID}...")
        
        # Get report data
        report_data = generate_report_data(DESKTOP_USER_ID, start_date, end_date)
        
        # Check if there's any data
        if not report_data or report_data.get('overall_stats', {}).get('total_habits', 0) == 0:
            report_text = f"""
═══════════════════════════════════════════════════
    🎯 HABIT TRACKER REPORT
       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════

🌟 WELCOME TO HABIT RE:CODER!

You haven't tracked any habits yet in the period:
{start_date} to {end_date}

START YOUR JOURNEY:
1. Add your first habit from the dashboard
2. Mark it complete when you do it
3. Come back here to see your progress!

Remember: Every journey begins with a single step! 💪
            """
        else:
            # Format normally if data exists
            report_text = format_report_as_text(report_data)
        
        print("✅ Report generated successfully")
        
        # Prepare response as downloadable text file
        response = make_response(report_text)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=habit_recoder_report_{end_date}.txt'
        return response

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        
        # Return user-friendly error
        error_text = f"""
ERROR GENERATING REPORT

An error occurred while creating your report.

Error details: {str(e)}

Please try again. If the problem persists, contact support.
        """
        response = make_response(error_text)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        return response, 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("🌐 Starting Flask server on http://localhost:5000")
    print("💡 To stop: Close this window or use Ctrl+C")
    app.run(debug=False, use_reloader=False, port=5000)