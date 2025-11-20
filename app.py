from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database.db_helper import init_db
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
from controllers.user_controller import (
    create_user, get_user_by_email, get_user_by_id, 
    verify_password, get_all_users, delete_user
)
from controllers.report_controller import generate_report_data
from datetime import datetime, timedelta
from functools import wraps
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True only if using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize database on first run
init_db()

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(int(user_id))

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not email or not password:
            flash('Email and password are required.', 'error')
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
        elif get_user_by_email(email):
            flash('Email already registered. Please login.', 'error')
        else:
            # Create user
            user_id = create_user(email, password)
            if user_id:
                flash('Account created successfully! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration failed. Please try again.', 'error')
    
    dark_mode = session.get('dark_mode', False)
    return render_template('register.html', dark_mode=dark_mode, app_name=config.APP_NAME)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = get_user_by_email(email)
        
        if user and verify_password(user, password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {email}!', 'success')
            
            # Redirect to next page or home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    
    dark_mode = session.get('dark_mode', False)
    return render_template('login.html', dark_mode=dark_mode, app_name=config.APP_NAME)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ============================================
# MAIN APPLICATION ROUTES
# ============================================

@app.route('/')
@login_required
def index():
    """Home page - show all habits and today's journal"""
    habits = get_all_habits(current_user.id)
    today = datetime.now().strftime('%A, %B %d, %Y')
    today_date = datetime.now().date()
    
    # Add streak and completion info to each habit
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
    
    # Calculate completion percentage
    completion_percentage = (completed_today / total_habits * 100) if total_habits > 0 else 0
    
    # Get today's journal entry
    journal_entry = get_journal_entry_by_date(current_user.id, today_date)
    
    # Get dark mode preference
    dark_mode = session.get('dark_mode', False)
    
    return render_template('index.html', 
                         habits_data=habits_data, 
                         today=today,
                         today_date=today_date,
                         completion_percentage=round(completion_percentage),
                         completed_today=completed_today,
                         total_habits=total_habits,
                         journal_entry=journal_entry,
                         dark_mode=dark_mode,
                         app_name=config.APP_NAME)

@app.route('/toggle_dark_mode')
def toggle_dark_mode():
    """Toggle dark mode"""
    session['dark_mode'] = not session.get('dark_mode', False)
    return redirect(request.referrer or url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
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
            create_habit(current_user.id, name, frequency, target_time, icon, motivation, challenges, ai_notes)
            flash('Habit added successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please fill in all required fields', 'error')
    
    dark_mode = session.get('dark_mode', False)
    return render_template('add_habit.html', dark_mode=dark_mode, app_name=config.APP_NAME)

@app.route('/habit/<int:habit_id>')
@login_required
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
@login_required
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
@login_required
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
    
    # GET request - show form
    habit = get_habit_by_id(habit_id)
    if not habit:
        flash('Habit not found', 'error')
        return redirect(url_for('index'))
    
    dark_mode = session.get('dark_mode', False)
    return render_template('complete_habit.html', habit=habit, dark_mode=dark_mode, app_name=config.APP_NAME)

@app.route('/delete/<int:habit_id>')
@login_required
def delete_habit_route(habit_id):
    """Delete a habit"""
    delete_habit(habit_id)
    flash('Habit deleted', 'info')
    return redirect(url_for('index'))

# ============================================
# JOURNAL ROUTES
# ============================================

@app.route('/journal', methods=['GET'])
@login_required
def journal():
    """View all journal entries"""
    search_term = request.args.get('search', '')
    
    if search_term:
        entries = search_journal_entries(current_user.id, search_term)
    else:
        entries = get_all_journal_entries(current_user.id)
    
    all_tags = get_all_tags(current_user.id)
    dark_mode = session.get('dark_mode', False)
    
    return render_template('journal.html', entries=entries, all_tags=all_tags, search_term=search_term, dark_mode=dark_mode, app_name=config.APP_NAME)

@app.route('/journal/save', methods=['POST'])
@login_required
def save_journal():
    """Save or update journal entry"""
    entry_date = request.form.get('entry_date')
    content = request.form.get('content')
    tags = request.form.get('tags')
    
    if entry_date and content:
        create_or_update_journal_entry(current_user.id, entry_date, content, tags)
        flash('Journal entry saved!', 'success')
    else:
        flash('Please fill in the content', 'error')
    
    # Check if coming from dashboard
    if request.form.get('from_dashboard'):
        return redirect(url_for('index'))
    
    return redirect(url_for('journal'))

@app.route('/journal/delete/<entry_date>')
@login_required
def delete_journal(entry_date):
    """Delete a journal entry"""
    delete_journal_entry(current_user.id, entry_date)
    flash('Journal entry deleted', 'info')
    return redirect(url_for('journal'))

# ============================================
# REPORT GENERATION
# ============================================

@app.route('/generate_report')
@login_required
def generate_report():
    """Generate and download text report"""
    # Generate report for last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    report_data = generate_report_data(current_user.id, start_date, end_date)  # Add current_user.id
    report_text = format_report_as_text(report_data)
    
    # Create text file response
    response = make_response(report_text)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=habit_recoder_report_{end_date}.txt'
    
    return response

# ============================================
# ADMIN ROUTES
# ============================================

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Admin panel - view all users"""
    users = get_all_users()
    dark_mode = session.get('dark_mode', False)
    return render_template('admin_users.html', users=users, dark_mode=dark_mode, app_name=config.APP_NAME)

@app.route('/admin/export_users')
@login_required
@admin_required
def admin_export_users():
    """Export user emails as CSV"""
    users = get_all_users()
    
    # Create CSV content
    csv_lines = ['Email,Signed Up,Admin']
    for user in users:
        csv_lines.append(f'{user.email},{user.created_at},{"Yes" if user.is_admin else "No"}')
    
    csv_content = '\n'.join(csv_lines)
    
    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=habit_recoder_users_{datetime.now().date()}.csv'
    
    return response

@app.route('/admin/delete_user/<int:user_id>')
@login_required
@admin_required
def admin_delete_user(user_id):
    """Delete a user (admin only)"""
    if user_id == current_user.id:
        flash('You cannot delete your own admin account!', 'error')
    else:
        delete_user(user_id)
        flash('User deleted successfully', 'success')
    
    return redirect(url_for('admin_users'))

if __name__ == '__main__':
    app.run(debug=config.DEBUG)