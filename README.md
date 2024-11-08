# CodeAnvil - Track Your GitHub Activity Across All Repositories

**CodeAnvil** is a Python tool for analyzing and visualizing GitHub commit activity across all repositories in a user’s account. CodeAnvil calculates intensity metrics that reflect coding rhythm, depth, and regularity, and generates a visualization of your GitHub activity.

## Features

- **Hammer Blows**: Measures average commit frequency across all repositories.
- **Activity Heat**: Calculates contribution depth based on rolling commits.
- **Anvil Strikes**: Tracks variability in commit frequency across repositories.
- **Consistency Score**: Shows the regularity of contributions over time.

## Setup

1. **Install Dependencies**: Make sure you have Python installed, then run:

   ```bash
   pip install -r requirements.txt
   ```

2. **Set Your GitHub Account Details**:
   - Open `codeanvil.py`.
   - Replace `GITHUB_USER` with your GitHub username.
   - (Optional) Add your GitHub token to `TOKEN` if you need access to private repos or higher rate limits.

3. **Run CodeAnvil**:

   ```bash
   python codeanvil.py
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

