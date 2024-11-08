import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
from codeanvil.keys.config_arg import GITHUB_USER, TOKEN
import mplcyberpunk

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

def calculate_metrics(since_days=30):

    df = fetch_recent_commits_from_events(since_days)

    """Calculates dynamic metrics based on recent commit data."""
    daily_commits = df['date'].value_counts().sort_index()
    
    commit_speed = daily_commits * np.exp(-0.1 * np.arange(len(daily_commits)))     # freq (Poisson dist.)
    commit_energy = daily_commits.ewm(span=7, min_periods=1).mean()     # depth
    time_gaps = daily_commits.index.to_series().diff().dt.days.fillna(1)

    fundamentals = {'daily_commits': daily_commits, 'commit_speed': commit_speed, 'commit_energy': commit_energy, 'time_gaps': time_gaps }

    metrics = fundamentals
    metrics['pulse'] = fundamentals['commit_speed'].mean()
    metrics['activity_heat'] = fundamentals['commit_energy'].mean()
    metrics['strikes'] = np.log1p(fundamentals['time_gaps']).std()
    gaps_penalty = 1 / (np.exp(fundamentals['time_gaps'].mean()) + 1)
    metrics['consistency_score'] = gaps_penalty * 100

    return df, metrics


def plot_metrics(metrics, title="Activity Metrics", figsize=(14, 8), show_plot=True):
    """Generates and saves a plot of dynamic commit metrics over recent activity."""
    plt.style.use("cyberpunk")
    plt.figure(figsize=figsize)  # Increase width and height for better readability
    # Plotting some fundamental metrics
    metrics['daily_commits'].plot(label="Daily Commits", linewidth=2)
    metrics['commit_energy'].plot(label="Commit Energy")

    # Creating the summary text to display in the xlabel
    summary_text = (
        f"Pulse: {metrics['pulse']:.2f}    "
        f"Activity Heat: {metrics['activity_heat']:.2f}    "
        f"Strikes: {metrics['strikes']:.2f}    "
        f"Consistency Score: {metrics['consistency_score']:.2f}"
    )
    
    # Set the title and labels, placing summary_text in the xlabel
    plt.title(f"CodeAnvil {title}")
    plt.xlabel(f"Date\n{summary_text}", fontsize=10)
    plt.ylabel("Commits")
    plt.legend()

    # Rotate date labels on the x-axis
    plt.xticks(rotation=45, ha='right', fontsize=8)
    
    # Adjust layout to ensure space for xlabel and rotated date labels
    plt.subplots_adjust(bottom=0.3)

    # Save or show the plot
    plot_filename = f"codeanvil_activity_{title.replace(' ', '_').lower()}.png"

    plt.savefig(plot_filename, bbox_inches="tight")
    print(f"{title} saved as {plot_filename}")

    if show_plot:
        plt.tight_layout()
        plt.show()


def activity_summary(df, metrics, period="Week"):
    """Displays a summary of active repositories, commits, and calculated metrics for a specified period."""
    
    # Display the last commit date for each active repository
    print(f"\n{period} Activity Summary:")
    activity_summary = df.groupby("repository")["date"].max()
    print(activity_summary)

    # Display calculated metrics
    print("\nMetrics Summary:")
    for metric in ['pulse', 'activity_heat', 'strikes', 'consistency_score']:
        print(f"{metric.replace('_', ' ').capitalize()}: {metrics[metric]:.2f}")


def weekly_activity(show_plot=True):
    """Fetch, analyze, and plot weekly GitHub activity metrics."""
    recent_week, weekly_metrics = calculate_metrics(since_days=7)
    activity_summary(recent_week, weekly_metrics, "Weekly")
    plot_metrics(weekly_metrics, "Weekly Activity Metrics for {GITHUB_USER}", show_plot=show_plot)

def monthly_activity(show_plot=True):
    """Fetch, analyze, and plot monthly GitHub activity metrics."""
    recent_month, monthly_metrics = calculate_metrics(since_days=30)
    activity_summary(recent_month, monthly_metrics, "Monthly")
    plot_metrics(monthly_metrics, f"Monthly Activity Metrics for {GITHUB_USER}", show_plot=show_plot)

def custom_activity(days, show_plot=True):
    """Fetch, analyze, and plot GitHub activity metrics for a custom time period."""
    recent_custom, custom_metrics = calculate_metrics(days)
    activity_summary(recent_custom, custom_metrics, f"Last {days} Days")
    plot_metrics(custom_metrics, f"Activity Metrics (Last {days} Days) for {GITHUB_USER}", show_plot=show_plot)

if __name__ == "__main__":
    weekly_activity()
    monthly_activity()
    custom_activity(14)  # Example for custom analysis of the last 14 days
