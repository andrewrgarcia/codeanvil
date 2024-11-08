import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
from codeanvil.keys.config_arg import GITHUB_USER, TOKEN
import mplcyberpunk

def fetch_recent_commits_from_events(since_days=30):
    """Fetches recent commit data for the user across all repos (including private) using GitHub Events API."""
    # Warn if the requested range exceeds 31 days due to GitHub API limitations
    if since_days > 31:
        print("Warning: GitHub Events API may not return complete data beyond 31 days.")

    headers = {"Authorization": f"token {TOKEN}"}
    url = f"https://api.github.com/users/{GITHUB_USER}/events"
    recent_commits = []
    cutoff_date = datetime.now() - timedelta(days=since_days)

    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        events = response.json()
        
        for event in events:
            if event["type"] == "PushEvent":
                repo_name = event["repo"]["name"]
                for commit in event["payload"]["commits"]:
                    commit_date = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                    if commit_date < cutoff_date:
                        return pd.DataFrame(recent_commits, columns=["repository", "date"])
                    recent_commits.append((repo_name, commit_date.date()))

        url = response.links.get('next', {}).get('url')
    
    return pd.DataFrame(recent_commits, columns=["repository", "date"])

def calculate_metrics(since_days=30):
    df = fetch_recent_commits_from_events(since_days)

    """Calculates dynamic metrics based on recent commit data."""
    daily_commits = df['date'].value_counts().sort_index()
    
    commit_speed = daily_commits * np.exp(-0.1 * np.arange(len(daily_commits)))
    commit_energy = daily_commits.ewm(span=7, min_periods=1).mean()
    time_gaps = daily_commits.index.to_series().diff().dt.days.fillna(1)

    fundamentals = {
        'days': since_days,
        'daily_commits': daily_commits, 
        'commit_speed': commit_speed, 
        'commit_energy': commit_energy, 
        'time_gaps': time_gaps
    }

    metrics = fundamentals
    metrics['pulse'] = fundamentals['commit_speed'].mean()
    metrics['activity_heat'] = fundamentals['commit_energy'].mean()
    gaps_penalty = 1 / (np.exp(fundamentals['time_gaps'].mean()) + 1)
    metrics['consistency_score'] = gaps_penalty * 100

    return df, metrics

def plot_metrics(metrics, title="Activity Metrics", figsize=(14, 8), show_plot=True):
    """Generates and saves a plot of dynamic commit metrics over recent activity."""
    plt.style.use("cyberpunk")
    plt.figure(figsize=figsize)
    metrics['daily_commits'].plot(label="Daily Commits", linewidth=2)
    metrics['commit_energy'].plot(label="Commit Energy")

    summary_text = (
        f"Days: {metrics['days']}    "
        f"Commits: {sum(metrics['daily_commits']):.2f}    "
        f"Pulse: {metrics['pulse']:.2f}    "
        f"Activity Heat: {metrics['activity_heat']:.2f}    "
        f"Consistency Score: {metrics['consistency_score']:.2f}"
    )
    
    plt.title(f"CodeAnvil {title}")
    plt.xlabel(f"Date\n{summary_text}\nhttps://github.com/andrewrgarcia/codeanvil", fontsize=10)
    plt.ylabel("Commits")
    plt.legend()
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.subplots_adjust(bottom=0.3)
    plot_filename = f"codeanvil_activity_{title.replace(' ', '_').lower()}.png"
    plt.savefig(plot_filename, bbox_inches="tight")
    print(f"{title} saved as {plot_filename}")

    if show_plot:
        plt.tight_layout()
        plt.show()

def activity_summary(df, metrics, period="Week"):
    """Displays a summary of active repositories, total commits, and detailed calculated metrics for a specified period."""
    print(f"\n{period} Activity Summary:")
    
    activity_summary = df.groupby("repository")["date"].max()
    print(activity_summary)

    print("\nMetrics Summary:")
    metrics['total_commits'] = np.sum(metrics['daily_commits'])
    
    metric_descriptions = {
        'total_commits': 'Total Commits',
        'pulse': 'Pulse (mean commit speed)',
        'activity_heat': 'Activity Heat (mean commit depth)',
        'consistency_score': 'Consistency Score (regularity of commits)'
    }
    
    print(f'Period: {period}')
    for metric, description in metric_descriptions.items():
        if metric in metrics:
            print(f"{description}: {metrics[metric]:.2f}")
    print()

def weekly_activity(show_plot=True):
    recent_week, weekly_metrics = calculate_metrics(since_days=7)
    activity_summary(recent_week, weekly_metrics, "Weekly")
    plot_metrics(weekly_metrics, f"Weekly Activity Metrics for {GITHUB_USER}", show_plot=show_plot)

def monthly_activity(show_plot=True):
    recent_month, monthly_metrics = calculate_metrics(since_days=30)
    activity_summary(recent_month, monthly_metrics, "Monthly")
    plot_metrics(monthly_metrics, f"Monthly Activity Metrics for {GITHUB_USER}", show_plot=show_plot)

def custom_activity(days, show_plot=True):
    recent_custom, custom_metrics = calculate_metrics(days)
    activity_summary(recent_custom, custom_metrics, f"Last {days} Days")
    plot_metrics(custom_metrics, f"Activity Metrics for {GITHUB_USER}", show_plot=show_plot)

if __name__ == "__main__":
    weekly_activity()
    monthly_activity()
    custom_activity(14)  # Example for custom analysis of the last 14 days
