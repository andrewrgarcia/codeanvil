import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# Read input parameters from environment variables
GITHUB_USER = os.getenv("GITHUB_USER")
TOKEN = os.getenv("TOKEN")
SINCE_DAYS = int(os.getenv("SINCE_DAYS", "30"))

def fetch_recent_commits(since_days=30):
    headers = {"Authorization": f"token {TOKEN}"}
    url = f"https://api.github.com/users/{GITHUB_USER}/events"
    cutoff_date = datetime.now() - timedelta(days=since_days)
    recent_commits = []

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
    df = fetch_recent_commits(since_days)
    daily_commits = df['date'].value_counts().sort_index()
    
    commit_speed = daily_commits * np.exp(-0.1 * np.arange(len(daily_commits)))
    commit_energy = daily_commits.ewm(span=7, min_periods=1).mean()
    time_gaps = daily_commits.index.to_series().diff().dt.days.fillna(1)

    metrics = {
        'days': since_days,
        'daily_commits': daily_commits,
        'commit_speed': commit_speed.mean(),
        'commit_energy': commit_energy.mean(),
        'time_gaps': time_gaps.mean(),
        'consistency_score': 1 / (np.exp(time_gaps.mean()) + 1) * 100
    }

    return metrics

def plot_metrics(metrics):
    plt.style.use("cyberpunk")
    plt.figure(figsize=(14, 8))
    
    metrics['daily_commits'].plot(label="Daily Commits", linewidth=2)
    plt.title(f"GitHub Activity Metrics for {GITHUB_USER}")
    plt.xlabel("Date")
    plt.ylabel("Commits")
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.3)

    plt.savefig("activity_plot.png", bbox_inches="tight")

def main():
    metrics = calculate_metrics(since_days=SINCE_DAYS)
    plot_metrics(metrics)

if __name__ == "__main__":
    main()
