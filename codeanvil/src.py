import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
from codeanvil.keys.config_arg import GITHUB_USER, TOKEN

def fetch_recent_commits_from_events(since_days=30):
    """Fetches recent commit data for the user across all repos using GitHub Events API."""
    headers = {"Authorization": f"token {TOKEN}"}
    url = f"https://api.github.com/users/{GITHUB_USER}/events/public"
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

def calculate_dynamic_metrics(df):
    """Calculates dynamic metrics based on recent commit data."""
    daily_commits = df['date'].value_counts().sort_index()
    
    commit_speed = daily_commits * np.exp(-0.1 * np.arange(len(daily_commits)))
    commit_energy = daily_commits.ewm(span=7, min_periods=1).mean()
    time_gaps = daily_commits.index.to_series().diff().dt.days.fillna(1)

    fundamentals = {'daily_commits': daily_commits, 'commit_speed': commit_speed, 'commit_energy': commit_energy, 'time_gaps': time_gaps }

    metrics = fundamentals
    metrics['pulse'] = fundamentals['commit_speed'].mean()
    metrics['activity_heat'] = fundamentals['commit_energy'].mean()
    metrics['strikes'] = np.log1p(fundamentals['time_gaps']).std()
    gaps_penalty = 1 / (np.exp(fundamentals['time_gaps'].mean()) + 1)
    metrics['consistency_score'] = gaps_penalty * 100

    return metrics

def plot_dynamic_metrics(metrics, title="Activity Metrics"):
    """Generates and saves a plot of dynamic commit metrics over recent activity."""
    plt.figure(figsize=(12, 6))
    metrics['daily_commits'].plot(label="Daily Commits", linewidth=2, color="steelblue")
    metrics['commit_speed'].plot(label="Commit Speed", linestyle="--")
    metrics['commit_energy'].plot(label="Commit Energy", linestyle=":")
    metrics['time_gaps'].plot(label="Time Gaps", linestyle="-.")
    plt.axhline(metrics['pulse'], color="orange", linestyle="--", label="Pulse")
    plt.title(f"CodeAnvil {title}")
    plt.xlabel("Date")
    plt.ylabel("Commits")
    plt.legend()
    plt.savefig(f"codeanvil_activity_{title.replace(' ', '_').lower()}.png")
    print(f"{title} saved as codeanvil_activity_{title.replace(' ', '_').lower()}.png")



def display_activity_summary(df, period="Week"):
    """Displays a summary of active repositories and commits for a specified period."""
    print(f"\n{period} Activity Summary:")
    print(df.groupby("repository")["date"].max())

def weekly_activity():
    """Fetch, analyze, and plot weekly GitHub activity metrics."""
    recent_week = fetch_recent_commits_from_events(since_days=7)
    display_activity_summary(recent_week, "Weekly")
    weekly_metrics = calculate_dynamic_metrics(recent_week)
    plot_dynamic_metrics(weekly_metrics, "Weekly Activity Metrics")

def monthly_activity():
    """Fetch, analyze, and plot monthly GitHub activity metrics."""
    recent_month = fetch_recent_commits_from_events(since_days=30)
    display_activity_summary(recent_month, "Monthly")
    monthly_metrics = calculate_dynamic_metrics(recent_month)
    plot_dynamic_metrics(monthly_metrics, "Monthly Activity Metrics")

def custom_activity(days):
    """Fetch, analyze, and plot GitHub activity metrics for a custom time period."""
    recent_custom = fetch_recent_commits_from_events(since_days=days)
    display_activity_summary(recent_custom, f"Last {days} Days")
    custom_metrics = calculate_dynamic_metrics(recent_custom)
    plot_dynamic_metrics(custom_metrics, f"Activity Metrics (Last {days} Days)")

if __name__ == "__main__":
    weekly_activity()
    monthly_activity()
    custom_activity(14)  # Example for custom analysis of the last 14 days
