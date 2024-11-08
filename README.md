![](codeanvil.webp)

# CodeAnvil - Track Your GitHub Activity Across All Repositories

**CodeAnvil** is a Python tool for analyzing and visualizing GitHub commit activity across all repositories in a user’s account. CodeAnvil calculates intensity metrics that reflect coding rhythm, depth, and regularity, and generates a visualization of your GitHub activity.

## Features

- **Pulse**: Measures the average commit frequency across all repositories, showing the "heartbeat" of activity.
- **Activity Heat**: Calculates contribution depth based on rolling commits.
- **Consistency Score**: Shows the regularity of contributions over time.

![](img/codeanvil_activity_monthly_activity_metrics_for_andrewrgarcia.png)

## Project Structure

```plaintext
./codeanvil/
├── src.py                    # Contains main logic for fetching, aggregating, and analyzing commit data
├── __init__.py               # Initializes the codeanvil package
└── keys/
    ├── config.py             # Stores user-configurable variables like GitHub username and token
    └── __init__.py

./script.py                   # Entry point script to execute CodeAnvil
```

## Setup

1. **Install Dependencies**: Make sure you have Python installed, then run:

   ```bash
   pip install -r requirements.txt
   ```

2. **Set Your GitHub Account Details**:
   - Open `codeanvil/keys/config.py`.
   - Replace `GITHUB_USER` with your GitHub username.
   - (Optional) Add your GitHub token to `TOKEN` if you need access to private repos or higher rate limits. See instructions below on how to create a token.

### Obtaining a GitHub Personal Access Token

1. **Go to GitHub Settings**:
   - Navigate to [GitHub’s Personal Access Tokens page](https://github.com/settings/tokens).
   
2. **Generate New Token**:
   - Click on **"Generate new token"** in the top right corner.

![](img/gh_token.png)

3. **Configure Token Permissions**:
   - Enter a name for your token (e.g., "CodeAnvil Token").
   - Set the expiration date as needed.
   - Under **"Select scopes"**, check the box for `repo` (for accessing private repositories if needed) and `read:user` to read public repository data.

![](img/gh_scopes_1.png)
![](img/gh_scopes_2.png)

4. **Generate and Save the Token**:
   - Click **"Generate token"** at the bottom of the page.
   - Copy the token **immediately** and save it securely, as you won’t be able to see it again.

5. **Add Token to CodeAnvil**:
   - Open `codeanvil/keys/config.py` and replace `TOKEN` with your new token. This will allow the script to authenticate with GitHub and retrieve commit data across all repositories.

3. **Run CodeAnvil**:

   ```bash
   python script.py
   ```

4. **View Results**:
   - The script generates a `codeanvil_activity.png` image in the same directory.
   - Embed this image in your README or website with Markdown:

     ```markdown
     ![CodeAnvil Activity](codeanvil_activity.png)
     ```

## Dependencies

CodeAnvil requires `requests`, `pandas`, `matplotlib`, and `numpy`.

## License

This project is licensed under the MIT License.
