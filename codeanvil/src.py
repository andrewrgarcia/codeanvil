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
            # Filter for push events only
            if event["type"] == "PushEvent":
                repo_name = event["repo"]["name"]
                for commit in event["payload"]["commits"]:
                    commit_date = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                    if commit_date < cutoff_date:
                        return pd.DataFrame(recent_commits, columns=["repository", "date"])
                    recent_commits.append((repo_name, commit_date.date()))

        # Pagination: Get the next page if available
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

    metrics['pulse'] = fundamentals['commit_speed'].mean()              # Recency-Weighted Pulse: Poisson-weighted commit frequency, emphasizing recent commits

    metrics['activity_heat'] = fundamentals['commit_energy'].mean()            # Dynamic Activity Heat: Weighted by recent commit depth using EMA

    metrics['strikes'] = np.log1p(fundamentals['time_gaps']).std()         # Adaptive Strikes: Logarithmic scoring on time intervals to capture pace changes

    gaps_penalty = 1 / (np.exp(fundamentals['time_gaps'].mean()) + 1)

    metrics['consistency_score'] = gaps_penalty * 100      # Stochastic Consistency Score: Penalizes irregular gaps

    return metrics

def plot_dynamic_metrics(metrics):
    """Generates and saves a plot of dynamic commit metrics over recent activity."""
    plt.figure(figsize=(12, 6))
    metrics['daily_commits'].plot(kind="line", label="Daily Commits", color="steelblue")

    metrics['commit_speed'].plot(kind="line", label="Daily Commits", color="steelblue")
    metrics['commit_energy'].plot(kind="line", label="Daily Commits", color="steelblue")
    metrics['time_gaps'].plot(kind="line", label="Daily Commits", color="steelblue")

    # plt.axhline(pulse, color="orange", linestyle="--", label="Recency-Weighted Pulse")
    plt.title("CodeAnvil Recent Activity Metrics (Last 30 Days)")
    plt.xlabel("Date")
    plt.ylabel("Commits")
    plt.legend()
    plt.savefig("codeanvil_activity_dynamic.png")
    # print(f"Metrics:\nPulse: {pulse}\nActivity Heat: {activity_heat}\nStrikes: {strikes}\nConsistency Score: {consistency_score}")

def main(metrics):
    # Collect recent activity data for the last week and month using events
    recent_week = fetch_recent_commits_from_events(since_days=7)
    recent_month = fetch_recent_commits_from_events(since_days=30)
    
    # Display recent repositories and commits
    print("\nRecent Activity Summary:")
    print("\nLast Week's Active Repositories and Commits:")
    print(recent_week.groupby("repository")["date"].max())
    print("\nLast Month's Active Repositories and Commits:")
    print(recent_month.groupby("repository")["date"].max())

    # Weekly metrics and plot
    print("\nWeekly Metrics:")
    metrics = calculate_dynamic_metrics(recent_week)
    plot_dynamic_metrics(metrics)

    # Monthly metrics and plot
    print("\nMonthly Metrics:")
    metrics = calculate_dynamic_metrics(recent_month)
    plot_dynamic_metrics(metrics)

    # Summary of calculated metrics
    print("\nMetrics Summary:")
    print(f"Weekly Pulse: {weekly_pulse:.2f}")
    print(f"Weekly Activity Heat: {weekly_heat:.2f}")
    print(f"Weekly Strikes: {weekly_strikes:.2f}")
    print(f"Weekly Consistency Score: {weekly_consistency:.2f}")
    print("\n")
    print(f"Monthly Pulse: {monthly_pulse:.2f}")
    print(f"Monthly Activity Heat: {monthly_heat:.2f}")
    print(f"Monthly Strikes: {monthly_strikes:.2f}")
    print(f"Monthly Consistency Score: {monthly_consistency:.2f}")

if __name__ == "__main__":
    main()
