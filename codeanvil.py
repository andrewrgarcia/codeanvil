import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# User-configurable variables
GITHUB_USER = "your-username"
TOKEN = "your-github-token"  # GitHub personal access token (for private repositories and higher rate limits)

def fetch_all_repos():
    """Fetches all repositories for the specified user."""
    headers = {"Authorization": f"token {TOKEN}"}
    url = f"https://api.github.com/users/{GITHUB_USER}/repos"
    repos = []
    
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        repos.extend([repo['name'] for repo in data if not repo['fork']])  # Exclude forks
        url = response.links.get('next', {}).get('url')
    
    return repos

def fetch_commit_data(repo):
    """Fetches commit data for a single repository and returns a DataFrame of commit dates."""
    headers = {"Authorization": f"token {TOKEN}"}
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/commits"
    params = {"per_page": 100}
    commit_dates = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        for commit in data:
            commit_dates.append(commit['commit']['author']['date'])
        # Get the next page of results if available
        url = response.links.get('next', {}).get('url')

    return pd.DataFrame(commit_dates, columns=["date"])

def aggregate_commit_data():
    """Aggregates commit data across all repositories."""
    repos = fetch_all_repos()
    all_commit_dates = pd.DataFrame(columns=["date"])

    for repo in repos:
        print(f"Fetching commits for repository: {repo}")
        repo_commit_data = fetch_commit_data(repo)
        all_commit_dates = pd.concat([all_commit_dates, repo_commit_data])

    all_commit_dates["date"] = pd.to_datetime(all_commit_dates["date"]).dt.date
    return all_commit_dates

def calculate_metrics(df):
    """Calculates commit intensity metrics based on commit data."""
    daily_commits = df['date'].value_counts().sort_index()

    # Hammer Blows (Commit Frequency)
    hammer_blows = daily_commits.mean()

    # Activity Heat (Commit Depth)
    activity_heat = daily_commits.rolling(window=7, min_periods=1).sum().mean()

    # Anvil Strikes (Commit Variability)
    anvil_strikes = daily_commits.std()

    # Consistency Score (Commit Regularity)
    consistency_score = 1 / (daily_commits.diff().std() + 1)

    return hammer_blows, activity_heat, anvil_strikes, consistency_score

def plot_metrics(daily_commits, hammer_blows, activity_heat, anvil_strikes, consistency_score):
    """Generates and saves a plot of commit metrics over time."""
    plt.figure(figsize=(12, 6))
    daily_commits.plot(kind="line", label="Daily Commits", color="steelblue")
    plt.axhline(hammer_blows, color="orange", linestyle="--", label="Hammer Blows (Avg Frequency)")
    plt.title("CodeAnvil Activity Metrics Across All Repositories")
    plt.xlabel("Date")
    plt.ylabel("Commits")
    plt.legend()
    plt.savefig("codeanvil_activity.png")
    print(f"Metrics:\nHammer Blows: {hammer_blows}\nActivity Heat: {activity_heat}\nAnvil Strikes: {anvil_strikes}\nConsistency Score: {consistency_score}")

def main():
    all_commit_dates = aggregate_commit_data()
    hammer_blows, activity_heat, anvil_strikes, consistency_score = calculate_metrics(all_commit_dates)
    daily_commits = all_commit_dates['date'].value_counts().sort_index()
    plot_metrics(daily_commits, hammer_blows, activity_heat, anvil_strikes, consistency_score)

if __name__ == "__main__":
    main()

