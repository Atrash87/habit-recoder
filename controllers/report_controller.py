from controllers.habit_controller import (
    get_all_habits, get_habit_logs, get_habit_streak, 
    get_completion_stats, is_completed_today
)
from controllers.journal_controller import get_all_journal_entries, get_all_tags
from datetime import datetime, timedelta
from collections import Counter

def generate_report_data(user_id, start_date=None, end_date=None):
    """Generate comprehensive report data for AI analysis"""
    
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)  # Default to last 30 days
    
    habits = get_all_habits(user_id)  # Pass user_id here
    report_data = {
        'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'period': f"{start_date} to {end_date}",
        'habits': [],
        'overall_stats': {},
        'patterns': {},
        'journal_insights': {}
    }
    
    # Overall statistics
    total_habits = len(habits)
    total_completions = 0
    total_possible = 0
    all_streaks = []
    completed_today_count = 0
    
    # Day of week analysis
    day_completions = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}  # Monday = 0
    day_totals = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    
    # Mood analysis
    mood_counts = {'happy': 0, 'neutral': 0, 'stressed': 0}
    
    # Process each habit
    for habit in habits:
        logs = get_habit_logs(habit.id)
        stats = get_completion_stats(habit.id)
        streak = get_habit_streak(habit.id)
        
        # Filter logs by date range
        filtered_logs = [
            log for log in logs 
            if start_date <= datetime.strptime(log.completed_date, '%Y-%m-%d').date() <= end_date
        ]
        
        completions_in_period = len(filtered_logs)
        days_in_period = (end_date - start_date).days + 1
        completion_rate = (completions_in_period / days_in_period * 100) if days_in_period > 0 else 0
        
        # Count moods
        for log in filtered_logs:
            if log.mood:
                mood_counts[log.mood] = mood_counts.get(log.mood, 0) + 1
        
        # Day of week pattern
        for log in logs:
            log_date = datetime.strptime(log.completed_date, '%Y-%m-%d').date()
            day_of_week = log_date.weekday()
            day_completions[day_of_week] += 1
        
        # Calculate day totals
        current_date = start_date
        while current_date <= end_date:
            day_totals[current_date.weekday()] += 1
            current_date += timedelta(days=1)
        
        total_completions += completions_in_period
        total_possible += days_in_period
        all_streaks.append(streak)
        
        if is_completed_today(habit.id):
            completed_today_count += 1
        
        # Find best time of day
        best_time = "Not set"
        if habit.target_time:
            best_time = habit.target_time
        
        habit_data = {
            'name': habit.name,
            'icon': habit.icon or '',
            'frequency': habit.frequency,
            'target_time': habit.target_time or 'Not set',
            'motivation': habit.motivation or '',
            'challenges': habit.challenges or '',
            'ai_notes': habit.ai_notes or '',
            'completions': f"{completions_in_period}/{days_in_period}",
            'completion_rate': round(completion_rate, 1),
            'current_streak': streak,
            'total_completions': stats['total_completions'],
            'best_time': best_time
        }
        
        report_data['habits'].append(habit_data)
    
    # Calculate overall stats
    overall_completion_rate = (total_completions / total_possible * 100) if total_possible > 0 else 0
    average_streak = sum(all_streaks) / len(all_streaks) if all_streaks else 0
    longest_streak = max(all_streaks) if all_streaks else 0
    
    report_data['overall_stats'] = {
        'total_habits': total_habits,
        'total_completions': total_completions,
        'overall_completion_rate': round(overall_completion_rate, 1),
        'average_streak': round(average_streak, 1),
        'longest_streak': longest_streak,
        'completed_today': completed_today_count
    }
    
    # Day of week patterns
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_performance = {}
    for day_num, day_name in enumerate(day_names):
        if day_totals[day_num] > 0:
            rate = (day_completions[day_num] / day_totals[day_num]) * 100
            day_performance[day_name] = round(rate, 1)
        else:
            day_performance[day_name] = 0
    
    # Find best and worst days
    sorted_days = sorted(day_performance.items(), key=lambda x: x[1], reverse=True)
    best_days = [f"{day} ({rate}%)" for day, rate in sorted_days[:2]]
    worst_days = [f"{day} ({rate}%)" for day, rate in sorted_days[-2:]]
    
    report_data['patterns'] = {
        'day_performance': day_performance,
        'best_days': best_days,
        'worst_days': worst_days
    }
    
    # Mood analysis
    total_moods = sum(mood_counts.values())
    mood_percentages = {}
    if total_moods > 0:
        for mood, count in mood_counts.items():
            mood_percentages[mood] = round((count / total_moods) * 100, 1)
    
    report_data['mood_analysis'] = {
        'happy': mood_percentages.get('happy', 0),
        'neutral': mood_percentages.get('neutral', 0),
        'stressed': mood_percentages.get('stressed', 0),
        'most_common': max(mood_counts, key=mood_counts.get) if total_moods > 0 else 'N/A'
    }
    
    # Journal insights
    journal_entries = get_all_journal_entries()
    
    # Filter journal entries by date range
    filtered_journal = [
        entry for entry in journal_entries
        if start_date <= datetime.strptime(entry.entry_date, '%Y-%m-%d').date() <= end_date
    ]
    
    all_journal_tags = get_all_tags()
    
    # Count tag usage
    tag_usage = []
    for entry in filtered_journal:
        if entry.tags:
            tags = [tag.strip() for tag in entry.tags.split(',')]
            tag_usage.extend(tags)
    
    tag_counter = Counter(tag_usage)
    most_common_tags = tag_counter.most_common(5)
    
    report_data['journal_insights'] = {
        'total_entries': len(filtered_journal),
        'most_common_tags': [f"{tag} ({count})" for tag, count in most_common_tags],
        'all_tags': all_journal_tags
    }
    
    return report_data


def format_report_as_text(report_data):
    """Format report data as a text file with AI prompt"""
    
    lines = []
    
    # Header
    lines.append("═" * 70)
    lines.append("    🎯 HABIT TRACKER - TRANSFORMATION ANALYSIS REPORT")
    lines.append(f"         Generated: {report_data['generated_date']}")
    lines.append(f"         Period: {report_data['period']}")
    lines.append("═" * 70)
    lines.append("")
    
    # Quick Overview
    lines.append("📋 QUICK OVERVIEW")
    lines.append("─" * 70)
    stats = report_data['overall_stats']
    lines.append(f"Total Habits Tracked: {stats['total_habits']}")
    lines.append(f"Total Completions: {stats['total_completions']}")
    lines.append(f"Overall Completion Rate: {stats['overall_completion_rate']}%")
    lines.append(f"Longest Current Streak: {stats['longest_streak']} days")
    lines.append(f"Average Streak: {stats['average_streak']} days")
    lines.append(f"Completed Today: {stats['completed_today']}/{stats['total_habits']}")
    lines.append("")
    
    # Detailed Habit Breakdown
    lines.append("📊 DETAILED HABIT BREAKDOWN")
    lines.append("─" * 70)
    for idx, habit in enumerate(report_data['habits'], 1):
        lines.append("")
        lines.append(f"{idx}. {habit['icon']} {habit['name']}")
        lines.append(f"   Frequency: {habit['frequency']}")
        lines.append(f"   Target Time: {habit['target_time']}")
        lines.append(f"   Completions: {habit['completions']} ({habit['completion_rate']}%)")
        lines.append(f"   Current Streak: {habit['current_streak']} days")
        lines.append(f"   Total All-Time Completions: {habit['total_completions']}")
        
        if habit['motivation']:
            lines.append(f"   ")
            lines.append(f"   💡 Why it matters: {habit['motivation']}")
        
        if habit['challenges']:
            lines.append(f"   ⚠️  Challenges: {habit['challenges']}")
        
        if habit['ai_notes']:
            lines.append(f"   🤖 Questions for AI: {habit['ai_notes']}")
    
    lines.append("")
    lines.append("")
    
    # Mood Analysis
    lines.append("🎭 MOOD ANALYSIS")
    lines.append("─" * 70)
    mood = report_data['mood_analysis']
    lines.append(f"Happy: {mood['happy']}%")
    lines.append(f"Neutral: {mood['neutral']}%")
    lines.append(f"Stressed: {mood['stressed']}%")
    lines.append(f"Most Common Mood: {mood['most_common']}")
    lines.append("")
    
    # Weekly Patterns
    lines.append("📅 WEEKLY PATTERNS")
    lines.append("─" * 70)
    patterns = report_data['patterns']
    lines.append("Performance by Day:")
    for day, rate in patterns['day_performance'].items():
        lines.append(f"  {day}: {rate}%")
    lines.append("")
    lines.append(f"Best Days: {', '.join(patterns['best_days'])}")
    lines.append(f"Struggle Days: {', '.join(patterns['worst_days'])}")
    lines.append("")
    
    # Journal Insights
    lines.append("📝 JOURNAL INSIGHTS")
    lines.append("─" * 70)
    journal = report_data['journal_insights']
    lines.append(f"Total Journal Entries: {journal['total_entries']}")
    if journal['most_common_tags']:
        lines.append(f"Most Common Tags: {', '.join(journal['most_common_tags'])}")
    lines.append("")
    lines.append("")
    
    # AI Prompt Section
    lines.append("═" * 70)
    lines.append("    🤖 COPY EVERYTHING BELOW FOR AI ANALYSIS")
    lines.append("═" * 70)
    lines.append("")
    lines.append("Paste this into ChatGPT/Claude/Gemini:")
    lines.append("")
    lines.append("─" * 70)
    lines.append("")
    
    # AI Prompt
    ai_prompt = f"""You are a transformational habit coach and behavioral psychologist specializing in life change. This person isn't just tracking habits - they're trying to change their life trajectory.

Your role:
1. Be honest and insightful (not just encouraging)
2. Question their approach if needed
3. Suggest better habits if theirs won't achieve their goals
4. Identify blind spots and self-sabotage patterns
5. Recommend complementary habits that accelerate transformation
6. Give hard truths when needed (with compassion)

Analyze this data and provide:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PART 1: STRATEGIC ASSESSMENT
- Are they tracking the RIGHT habits for their goals?
- Is something missing that would accelerate progress?
- Are there misaligned priorities?

PART 2: DEEP PATTERN ANALYSIS
- What psychological patterns emerge from their data?
- Where is self-sabotage showing up?
- What do completion patterns reveal about their personality?

PART 3: THE HARD TRUTHS
- What are they avoiding that they need to hear?
- Where are they lying to themselves?
- What fundamental shift is needed?

PART 4: COMPLEMENTARY HABITS
- What 2-3 habits should they ADD to amplify results?
- What habit stacks would create momentum?
- What keystone habit would unlock everything else?

PART 5: SPECIFIC INTERVENTIONS
- For each struggling habit: WHY it's failing (real reason)
- Specific strategy changes (not generic advice)
- Timeline: What to expect week-by-week

PART 6: TRANSFORMATION ROADMAP
- Where will they be in 90 days if they continue current path?
- What needs to change to reach their actual goal?
- The ONE thing that would change everything

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MY DATA:

PERIOD ANALYZED: {report_data['period']}

OVERALL PERFORMANCE:
- Total Habits: {stats['total_habits']}
- Completion Rate: {stats['overall_completion_rate']}%
- Longest Streak: {stats['longest_streak']} days
- Average Streak: {stats['average_streak']} days

HABITS I'M TRACKING:
"""
    
    lines.append(ai_prompt)
    
    # Add each habit with full context
    for idx, habit in enumerate(report_data['habits'], 1):
        lines.append("")
        lines.append(f"{idx}. {habit['icon']} {habit['name']}")
        lines.append(f"   Completion Rate: {habit['completion_rate']}%")
        lines.append(f"   Current Streak: {habit['current_streak']} days")
        lines.append(f"   Target Time: {habit['target_time']}")
        
        if habit['motivation']:
            lines.append(f"   ")
            lines.append(f"   Why it matters: \"{habit['motivation']}\"")
        
        if habit['challenges']:
            lines.append(f"   Expected challenges: \"{habit['challenges']}\"")
        
        if habit['ai_notes']:
            lines.append(f"   Questions for AI: \"{habit['ai_notes']}\"")
    
    lines.append("")
    lines.append("PERFORMANCE PATTERNS:")
    lines.append(f"• Best Days: {', '.join(patterns['best_days'])}")
    lines.append(f"• Struggle Days: {', '.join(patterns['worst_days'])}")
    lines.append("")
    
    lines.append("EMOTIONAL PATTERNS:")
    lines.append(f"• Happy: {mood['happy']}% of completions")
    lines.append(f"• Neutral: {mood['neutral']}% of completions")
    lines.append(f"• Stressed: {mood['stressed']}% of completions")
    lines.append(f"• Most common mood: {mood['most_common']}")
    lines.append("")
    
    if journal['most_common_tags']:
        lines.append("JOURNAL THEMES:")
        lines.append(f"• Total journal entries: {journal['total_entries']}")
        lines.append(f"• Common themes: {', '.join(journal['most_common_tags'])}")
        lines.append("")
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("Please provide thorough, honest, and insightful analysis.")
    lines.append("I need real guidance, not generic motivation.")
    lines.append("Tell me what I'm not seeing about myself and my journey.")
    lines.append("")
    lines.append("═" * 70)
    lines.append("END OF PROMPT - Copy everything from 'You are a")
    lines.append("transformational habit coach...' to here")
    lines.append("═" * 70)
    
    return "\n".join(lines)