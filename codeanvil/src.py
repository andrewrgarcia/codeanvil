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
                for commit in event["payload"]["commits"]:
                    commit_date = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                    if commit_date < cutoff_date:
                        # Stop if the event is older than the cutoff date
                        return pd.DataFrame(recent_commits, columns=["date"])
                    recent_commits.append(commit_date.date())

        # Pagination: Get the next page if available
        url = response.links.get('next', {}).get('url')
    
    return pd.DataFrame(recent_commits, columns=["date"])

def calculate_dynamic_metrics(df):
    """Calculates dynamic metrics based on recent commit data."""
    daily_commits = df['date'].value_counts().sort_index()
    
    # Recency-Weighted Pulse: Poisson-weighted commit frequency, emphasizing recent commits
    weighted_counts = daily_commits * np.exp(-0.1 * np.arange(len(daily_commits)))
    pulse = weighted_counts.mean()

    # Dynamic Activity Heat: Weighted by recent commit depth using EMA
    heat_weighted = daily_commits.ewm(span=7, min_periods=1).mean()
    activity_heat = heat_weighted.mean()

    # Adaptive Strikes: Logarithmic scoring on time intervals to capture pace changes
    time_intervals = daily_commits.index.to_series().diff().dt.days.fillna(1)
    strikes = np.log1p(time_intervals).std()

    # Stochastic Consistency Score: Penalizes irregular gaps
    gaps_penalty = 1 / (np.exp(time_intervals.mean()) + 1)
    consistency_score = gaps_penalty * 100

    return pulse, activity_heat, strikes, consistency_score

def plot_dynamic_metrics(daily_commits, pulse, activity_heat, strikes, consistency_score):
    """Generates and saves a plot of dynamic commit metrics over recent activity."""
    plt.figure(figsize=(12, 6))
    daily_commits.plot(kind="line", label="Daily Commits", color="steelblue")
    plt.axhline(pulse, color="orange", linestyle="--", label="Recency-Weighted Pulse")
    plt.title("CodeAnvil Recent Activity Metrics (Last 30 Days)")
    plt.xlabel("Date")
    plt.ylabel("Commits")
    plt.legend()
    plt.savefig("codeanvil_activity_dynamic.png")
    print(f"Metrics:\nPulse: {pulse}\nActivity Heat: {activity_heat}\nStrikes: {strikes}\nConsistency Score: {consistency_score}")

def main():
    # Collect recent activity data for the last week and month using events
    recent_week = fetch_recent_commits_from_events(since_days=7)
    recent_month = fetch_recent_commits_from_events(since_days=30)
    
    print("Weekly Metrics:")
    weekly_pulse, weekly_heat, weekly_strikes, weekly_consistency = calculate_dynamic_metrics(recent_week)
    plot_dynamic_metrics(recent_week['date'].value_counts(), weekly_pulse, weekly_heat, weekly_strikes, weekly_consistency)

    print("Monthly Metrics:")
    monthly_pulse, monthly_heat, monthly_strikes, monthly_consistency = calculate_dynamic_metrics(recent_month)
    plot_dynamic_metrics(recent_month['date'].value_counts(), monthly_pulse, monthly_heat, monthly_strikes, monthly_consistency)

if __name__ == "__main__":
    main()
