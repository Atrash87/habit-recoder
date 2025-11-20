from controllers.habit_controller import (
    get_all_habits, get_habit_logs, get_habit_streak, 
    get_completion_stats, is_completed_today
)
from controllers.journal_controller import get_all_journal_entries, get_all_tags
from datetime import datetime, timedelta
from collections import Counter

def debug_check():
    """Temporary debug function to check if everything is working"""
    print("=== DEBUG: report_controller is loaded correctly ===")
    print(f"generate_report_data function: {generate_report_data}")
    print(f"format_report_as_text function: {format_report_as_text}")

def generate_report_data(user_id, start_date=None, end_date=None):
    """Generate robust report data for AI analysis - handles empty data gracefully"""
    
    try:
        print(f"DEBUG: Starting report generation for user {user_id}")
        
        if not end_date:
            end_date = datetime.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        print(f"DEBUG: Date range: {start_date} to {end_date}")

        # Safely get habits
        try:
            print("DEBUG: Attempting to get habits...")
            habits = get_all_habits(user_id) or []
            print(f"DEBUG: Retrieved {len(habits)} habits")
        except Exception as e:
            print(f"DEBUG: Error getting habits: {str(e)}")
            habits = []

        report_data = {
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'period': f"{start_date} to {end_date}",
            'habits': [],
            'overall_stats': {},
            'patterns': {},
            'mood_analysis': {},
            'journal_insights': {},
            'journal_entries': []  # ADDED: Ensure this key exists
        }

             # If no habits, return minimal report WITH journal data
        if not habits:
            print("DEBUG: No habits found, but checking for journal entries...")
            
            # Get journal entries even if no habits exist
            try:
                journal_entries = get_all_journal_entries(user_id) or []
                filtered_journal = []
                for entry in journal_entries:
                    try:
                        entry_date = datetime.strptime(entry.entry_date, '%Y-%m-%d').date()
                        if start_date <= entry_date <= end_date:
                            filtered_journal.append(entry)
                    except:
                        continue
                
                # Include journal entries in report data
                journal_entries_data = []
                for entry in filtered_journal:
                    journal_entries_data.append({
                        'date': entry.entry_date,
                        'content': entry.content,
                        'tags': entry.tags
                    })
                
                report_data['journal_entries'] = journal_entries_data
                journal_count = len(filtered_journal)
                print(f"DEBUG: Found {journal_count} journal entries without habits")
            except Exception as e:
                print(f"DEBUG: Error getting journal entries without habits: {e}")
                journal_count = 0
                report_data['journal_entries'] = []
            
            report_data['overall_stats'] = {
                'total_habits': 0,
                'total_completions': 0,
                'overall_completion_rate': 0,
                'average_streak': 0,
                'longest_streak': 0,
                'completed_today': 0
            }
            report_data['patterns'] = {
                'day_performance': {day: 0 for day in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']},
                'best_days': ['Not enough data yet'],
                'worst_days': ['Not enough data yet']
            }
            report_data['mood_analysis'] = {
                'happy': 0,
                'neutral': 0,
                'stressed': 0,
                'most_common': 'N/A'
            }
            report_data['journal_insights'] = {
                'total_entries': journal_count,
                'most_common_tags': ['None'] if journal_count == 0 else ["Check journal entries"],
                'all_tags': []
            }
            return report_data

        # Continue with the actual logic for when there are habits...
        total_completions = 0
        total_possible = 0
        all_streaks = []
        completed_today_count = 0

        day_completions = {i: 0 for i in range(7)}
        day_totals = {i: 0 for i in range(7)}
        mood_counts = {'happy': 0, 'neutral': 0, 'stressed': 0}

        for habit in habits:
            try:
                print(f"DEBUG: Processing habit: {getattr(habit, 'name', 'Unnamed')}")
                logs = get_habit_logs(habit.id) or []
                stats = get_completion_stats(habit.id) or {'total_completions': 0}
                streak = get_habit_streak(habit.id) or 0
                print(f"DEBUG: Habit {habit.id} - logs: {len(logs)}, streak: {streak}")
            except Exception as e:
                print(f"DEBUG: Error processing habit {getattr(habit, 'id', 'unknown')}: {str(e)}")
                logs = []
                stats = {'total_completions': 0}
                streak = 0

            # Filter logs safely
            filtered_logs = []
            for log in logs:
                try:
                    log_date = datetime.strptime(log.completed_date, '%Y-%m-%d').date()
                    if start_date <= log_date <= end_date:
                        filtered_logs.append(log)
                except:
                    continue

            completions_in_period = len(filtered_logs)
            days_in_period = max((end_date - start_date).days + 1, 1)
            completion_rate = (completions_in_period / days_in_period * 100) if days_in_period else 0

            # Count moods safely
            for log in filtered_logs:
                if hasattr(log, 'mood') and log.mood and log.mood in mood_counts:
                    mood_counts[log.mood] += 1

            # Day of week completions
            for log in filtered_logs:
                try:
                    log_date = datetime.strptime(log.completed_date, '%Y-%m-%d').date()
                    day_completions[log_date.weekday()] += 1
                except:
                    continue

            # Day totals - FIXED: Count each day for each habit
            current_date = start_date
            while current_date <= end_date:
                day_totals[current_date.weekday()] += 1  # Each day counts for each habit
                current_date += timedelta(days=1)

            total_completions += completions_in_period
            total_possible += days_in_period
            all_streaks.append(streak)
            
            try:
                if is_completed_today(habit.id):
                    completed_today_count += 1
            except:
                pass

            # Add habit safely
            report_data['habits'].append({
                'name': getattr(habit, 'name', 'Unnamed Habit'),
                'icon': getattr(habit, 'icon', '') or '',
                'frequency': getattr(habit, 'frequency', 'Not set'),
                'target_time': getattr(habit, 'target_time', 'Not set') or 'Not set',
                'motivation': getattr(habit, 'motivation', '') or '',
                'challenges': getattr(habit, 'challenges', '') or '',
                'ai_notes': getattr(habit, 'ai_notes', '') or '',
                'completions': f"{completions_in_period}/{days_in_period}",
                'completion_rate': round(completion_rate, 1),
                'current_streak': streak,
                'total_completions': stats.get('total_completions', 0)
            })

        # Overall stats - FIXED: Safe calculations
        try:
            overall_completion_rate = (total_completions / total_possible * 100) if total_possible else 0
        except:
            overall_completion_rate = 0
            
        try:
            average_streak = (sum(all_streaks) / len(all_streaks)) if all_streaks else 0
        except:
            average_streak = 0
            
        try:
            longest_streak = max(all_streaks) if all_streaks else 0
        except:
            longest_streak = 0

        report_data['overall_stats'] = {
            'total_habits': len(habits),
            'total_completions': total_completions,
            'overall_completion_rate': round(overall_completion_rate, 1),
            'average_streak': round(average_streak, 1),
            'longest_streak': longest_streak,
            'completed_today': completed_today_count
        }

        # Day patterns - FIXED: Safe calculations
        day_names = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        day_performance = {}
        for i in range(7):
            if day_totals[i] > 0:
                day_performance[day_names[i]] = round((day_completions[i] / day_totals[i] * 100), 1)
            else:
                day_performance[day_names[i]] = 0
        
        sorted_days = sorted(day_performance.items(), key=lambda x: x[1], reverse=True)
        
        if total_completions > 0:
            best_days = [f"{day} ({rate}%)" for day, rate in sorted_days[:2]]
            worst_days = [f"{day} ({rate}%)" for day, rate in sorted_days[-2:]]
        else:
            best_days = ["Not enough data yet - complete more habits!"]
            worst_days = ["Keep tracking to see patterns"]
        
        report_data['patterns'] = {
            'day_performance': day_performance,
            'best_days': best_days,
            'worst_days': worst_days
        }

        # Mood analysis - FIXED: Safe calculations
        total_moods = sum(mood_counts.values())
        if total_moods > 0:
            mood_percentages = {k: round((v / total_moods) * 100, 1) for k, v in mood_counts.items()}
            most_common = max(mood_counts, key=mood_counts.get)
        else:
            mood_percentages = {'happy': 0, 'neutral': 0, 'stressed': 0}
            most_common = 'N/A - Add mood data when completing habits'
        
        report_data['mood_analysis'] = {
            **mood_percentages,
            'most_common': most_common
        }

        # Journal insights - FIXED: Include actual entries
        try:
            journal_entries = get_all_journal_entries(user_id) or []
            print(f"DEBUG: Found {len(journal_entries)} total journal entries")
        except Exception as e:
            print(f"DEBUG: Error getting journal entries: {e}")
            journal_entries = []
        
        filtered_journal = []
        for entry in journal_entries:
            try:
                entry_date = datetime.strptime(entry.entry_date, '%Y-%m-%d').date()
                if start_date <= entry_date <= end_date:
                    filtered_journal.append(entry)
                    print(f"DEBUG: Added journal entry for {entry_date}")
            except Exception as e:
                print(f"DEBUG: Error processing journal entry date: {e}")
                continue
        
        print(f"DEBUG: {len(filtered_journal)} journal entries in date range")
        
        try:
            all_journal_tags = get_all_tags(user_id) or []
        except:
            all_journal_tags = []

        tag_usage = []
        for entry in filtered_journal:
            if hasattr(entry, 'tags') and entry.tags:
                tags_list = [t.strip() for t in entry.tags.split(',')]
                tag_usage.extend(tags_list)
                print(f"DEBUG: Found tags: {tags_list}")
        
        tag_counter = Counter(tag_usage)
        most_common_tags = tag_counter.most_common(5)
        print(f"DEBUG: Most common tags: {most_common_tags}")

        # ENHANCED: Include actual journal entries in report data
        journal_entries_data = []
        for entry in filtered_journal:
            try:
                journal_entries_data.append({
                    'date': entry.entry_date,
                    'content': entry.content,
                    'tags': entry.tags
                })
                print(f"DEBUG: Added journal content for {entry.entry_date}")
            except Exception as e:
                print(f"DEBUG: Error adding journal entry to report: {e}")
                continue
        
        report_data['journal_insights'] = {
            'total_entries': len(filtered_journal),
            'most_common_tags': [f"{tag} ({count})" for tag, count in most_common_tags] if most_common_tags else ["No journal entries yet"],
            'all_tags': all_journal_tags
        }
        
        # ADDED: Include the actual journal entries for the report
        report_data['journal_entries'] = journal_entries_data
        print(f"DEBUG: Final journal entries in report: {len(journal_entries_data)}")

        print("DEBUG: Report generation completed successfully")
        return report_data
        
    except Exception as e:
        print(f"DEBUG: CRITICAL ERROR in generate_report_data: {str(e)}")
        # Return a basic error report that won't break format_report_as_text
        return {
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'period': 'Error period',
            'habits': [],
            'overall_stats': {
                'total_habits': 0,
                'total_completions': 0,
                'overall_completion_rate': 0,
                'average_streak': 0,
                'longest_streak': 0,
                'completed_today': 0
            },
            'patterns': {},
            'mood_analysis': {},
            'journal_insights': {},
            'journal_entries': []
        }

def format_report_as_text(report_data):
    """Convert report data dictionary into a safe, readable text with AI prompt"""
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
    
    # Check if just starting out
    if stats['total_completions'] == 0:
        lines.append("🌟 JUST GETTING STARTED!")
        lines.append("─" * 70)
        lines.append("You're at the beginning of your journey - exciting!")
        lines.append("Complete a few more habits to generate detailed insights.")
        lines.append("Keep going - consistency is key! 💪")
        lines.append("")
    elif stats['total_completions'] < 5:
        lines.append("🌱 BUILDING MOMENTUM!")
        lines.append("─" * 70)
        lines.append("Great start! Keep completing habits to see deeper patterns.")
        lines.append("After a week of tracking, you'll get much richer insights.")
        lines.append("")
    
    # Detailed Habit Breakdown
    if report_data['habits']:
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
    
    # Mood Analysis (only if there's data)
    mood = report_data['mood_analysis']
    if mood.get('happy', 0) + mood.get('neutral', 0) + mood.get('stressed', 0) > 0:
        lines.append("🎭 MOOD ANALYSIS")
        lines.append("─" * 70)
        lines.append(f"Happy: {mood['happy']}%")
        lines.append(f"Neutral: {mood['neutral']}%")
        lines.append(f"Stressed: {mood['stressed']}%")
        lines.append(f"Most Common Mood: {mood['most_common']}")
        lines.append("")
    
    # Weekly Patterns (only if there's data)
    if stats['total_completions'] >= 3:
        lines.append("📅 WEEKLY PATTERNS")
        lines.append("─" * 70)
        lines.append("Performance by Day:")
        for day, rate in report_data['patterns']['day_performance'].items():
            lines.append(f"  {day}: {rate}%")
        lines.append("")
        lines.append(f"Best Days: {', '.join(report_data['patterns']['best_days'])}")
        lines.append(f"Struggle Days: {', '.join(report_data['patterns']['worst_days'])}")
        lines.append("")
    
    # Journal Insights - FIXED: Show actual content
    journal = report_data['journal_insights']
    if journal['total_entries'] > 0:
        lines.append("📝 JOURNAL INSIGHTS")
        lines.append("─" * 70)
        lines.append(f"Total Journal Entries: {journal['total_entries']}")
        
        # Show most common tags if available
        if journal['most_common_tags'] and journal['most_common_tags'][0] != "No journal entries yet":
            lines.append(f"Most Common Tags: {', '.join(journal['most_common_tags'])}")
        
        # Show recent journal entries
        lines.append("")
        lines.append("📖 RECENT JOURNAL ENTRIES:")
        lines.append("")
        
        # Get the actual journal entries from report_data
        if 'journal_entries' in report_data and report_data['journal_entries']:
            # Show entries in reverse chronological order (newest first)
            sorted_entries = sorted(report_data['journal_entries'], 
                                  key=lambda x: x['date'], 
                                  reverse=True)[:5]  # Show last 5 entries
            
            for entry in sorted_entries:
                lines.append(f"📅 {entry['date']}:")
                # Show the full content (you can limit length if needed)
                content = entry['content']
                # Split content into lines for better formatting
                content_lines = content.split('\n')
                for line in content_lines:
                    if line.strip():  # Only show non-empty lines
                        lines.append(f"   {line}")
                
                if entry.get('tags') and entry['tags'].strip():
                    lines.append(f"   🏷️  Tags: {entry['tags']}")
                lines.append("")  # Empty line between entries
        else:
            lines.append("   No journal content available in the selected date range.")
            lines.append("   Try adjusting the report period to include your journal entries.")
        
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
    lines.append("You are a transformational habit coach. Analyze this habit data and provide:")
    lines.append("")
    lines.append("1. KEY INSIGHTS: What patterns do you see?")
    lines.append("2. STRENGTHS: What is working well?")
    lines.append("3. IMPROVEMENTS: Where can I do better?")
    lines.append("4. RECOMMENDATIONS: 3-5 specific, actionable steps")
    lines.append("5. HABIT SUGGESTIONS: What complementary habits would help?")
    lines.append("")
    lines.append("MY DATA:")
    lines.append("")
    lines.append(f"Period: {report_data['period']}")
    lines.append(f"Total Habits: {stats['total_habits']}")
    lines.append(f"Completion Rate: {stats['overall_completion_rate']}%")
    lines.append(f"Longest Streak: {stats['longest_streak']} days")
    lines.append("")
    
    if report_data['habits']:
        lines.append("HABITS I'M TRACKING:")
        lines.append("")
        for idx, habit in enumerate(report_data['habits'], 1):
            lines.append(f"{idx}. {habit['icon']} {habit['name']}")
            lines.append(f"   Completion Rate: {habit['completion_rate']}%")
            lines.append(f"   Current Streak: {habit['current_streak']} days")
            if habit['motivation']:
                lines.append(f"   Why: \"{habit['motivation']}\"")
            if habit['challenges']:
                lines.append(f"   Challenges: \"{habit['challenges']}\"")
            if habit['ai_notes']:
                lines.append(f"   Questions: \"{habit['ai_notes']}\"")
            lines.append("")
    
    if stats['total_completions'] >= 3:
        lines.append("PATTERNS:")
        lines.append(f"Best Days: {', '.join(report_data['patterns']['best_days'])}")
        lines.append(f"Struggle Days: {', '.join(report_data['patterns']['worst_days'])}")
        lines.append("")
    
    if mood.get('happy', 0) + mood.get('neutral', 0) + mood.get('stressed', 0) > 0:
        lines.append("MOOD TRENDS:")
        lines.append(f"Happy: {mood['happy']}%, Neutral: {mood['neutral']}%, Stressed: {mood['stressed']}%")
        lines.append("")
    
    # ADDED: Journal content in AI prompt
    if 'journal_entries' in report_data and report_data['journal_entries']:
        lines.append("MY JOURNAL ENTRIES:")
        lines.append("")
        # Sort by date (oldest first for context)
        sorted_entries = sorted(report_data['journal_entries'], key=lambda x: x['date'])
        for entry in sorted_entries:
            lines.append(f"Date: {entry['date']}")
            lines.append(f"Content: {entry['content']}")
            if entry.get('tags') and entry['tags'].strip():
                lines.append(f"Tags: {entry['tags']}")
            lines.append("")  # Empty line between entries
        lines.append("")
    
    lines.append("Please provide specific, actionable insights based on this data.")
    lines.append("")
    lines.append("═" * 70)
    lines.append("END OF PROMPT")
    lines.append("═" * 70)
    
    return "\n".join(lines)