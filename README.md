# Daily Email Report Automation

The **Daily Email Report Automation** is a Python-based tool that automates the process of fetching, summarizing, and reporting emails received between 12:01 AM and 9:01 AM BDT daily. It integrates Gmail, Google Sheets, and Slack APIs, using Grok AI to summarize email content. Summaries are stored in a Google Sheet and sent as a notification to a Slack channel, streamlining daily communication monitoring.

## Table of Contents
- [Purpose](#purpose)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Setup Requirements](#setup-requirements)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Purpose
The **Daily Email Report Automation** simplifies the task of reviewing and summarizing emails received overnight (12:01 AM to 9:01 AM BDT). It fetches emails from Gmail, generates concise summaries using Grok AI, updates a Google Sheet with the results, and sends a notification to a Slack channel. This tool is ideal for teams or individuals who need a daily digest of important emails without manual effort.

### Why Use This Project?
- **Automation**: Saves time by automatically fetching and summarizing emails.
- **AI Summaries**: Uses Grok AI to create concise, readable email summaries.
- **Multi-Platform Integration**: Connects Gmail, Google Sheets, and Slack for a seamless workflow.
- **Reliability**: Includes error handling and logging for robust operation.
- **Convenience**: Provides a batch script (`run_daily_report.bat`) for easy execution on Windows.

## Features
- **Email Fetching**: Retrieves emails from Gmail received between 12:01 AM and 9:01 AM BDT, excluding spam and trash.
- **AI-Powered Summaries**: Uses Grok AI to summarize email content into 1-2 sentences (max 130 words).
- **Google Sheets Integration**: Clears and updates a specified Google Sheet range with email subjects and summaries.
- **Slack Notifications**: Sends a daily report to a Slack channel with up to 5 email summaries and a total count.
- **Timezone Awareness**: Handles Bangladesh Time (BDT, UTC+6) for precise email filtering.
- **Logging**: Outputs detailed logs to `log.txt` and the console for debugging and monitoring.

## Installation
Follow these steps to set up the project locally:

1. **Clone the Repository**:
   ```
   git clone https://github.com/username/daily-email-report.git
   cd daily-email-report
   ```
2. **Set Up a Virtual Environment (recommended):**

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. **Install Dependencies:**
```
pip install -r requirements.txt

```
4. **Set Up Environment Variables:**

- **Create a .env file in the root directory with:**
```

SLACK_BOT_TOKEN=your_slack_bot_token
GROQ_API_KEY=your_groq_api_key

```
* Obtain a Slack Bot Token from your Slack workspace (create a bot with chat:write scope).

* Get a Grok API key from xAI.

## Set Up Google API Credentials:
- Download credentials.json from the Google Cloud Console for a Desktop app with Gmail and Google Sheets APIs enabled.
- Place credentials.json in the project root.
- Ensure the following scopes are enabled:
  - https://www.googleapis.com/auth/gmail.readonly
  - https://www.googleapis.com/auth/spreadsheets

## Configure Google Sheet:
- Create a Google Sheet and note its Spreadsheet ID (found in the URL: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit).
- Update the SPREADSHEET_ID in main.py if different from the default (1QQ8bZUodwLTs_lc8Vxry_EoPIhdGb8kaHtQN19ScfAc).
- Ensure the Sheet has a tab named Sheet1 (or update SHEET_RANGE in main.py).

## Run the Application:
- On Windows, double-click run_daily_report.bat or run:
```
.\run_daily_report.bat
```
- On Linux/Mac, run:
```
python main.py
```

# Usage
##### Run the Script:
- Execute run_daily_report.bat (Windows) or python main.py (Linux/Mac).
- On first run, authenticate with Google via a browser prompt to grant access to Gmail and Sheets APIs.
##### What It Does:
- Fetches emails received between 12:01 AM and 9:01 AM BDT.
- Summarizes email content using Grok AI.
- Updates a Google Sheet (Sheet1!A:B) with email subjects and summaries.
- Sends a Slack notification to the #mydaily-report channel with up to 5 summaries and the total email count.
##### Monitor Output:
- Check log.txt for detailed logs of email fetching, summarization, Sheet updates, and Slack notifications.
- Console output provides real-time feedback on the process.
##### Scheduling:
- Schedule the script to run daily (e.g., via Windows Task Scheduler or a cron job) to automate daily reporting.

# Project Structure

```
daily-email-report/
├── app.py                   # Main script for email fetching, summarization, and reporting
├── credentials.json          # Google API credentials (not tracked in Git)
├── token.json                # Google API token (generated after authentication, not tracked)
├── log.txt                   # Log file for debugging and monitoring
├── run_daily_report.bat      # Batch script for running the agent on Windows
├── .env                      # Environment variables (API keys)
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Dependencies

```
google-auth-oauthlib
google-api-python-client
slack-sdk
groq
python-dotenv
pytz
```
```
pip install google-auth-oauthlib google-api-python-client slack-sdk groq python-dotenv pytz
```

# Setup Requirements
- Google Cloud Project: Enable Gmail and Google Sheets APIs, and download credentials.json for a Desktop app.
- Grok API Key: Obtain from xAI for email summarization.
- Slack Workspace: Create a bot with chat:write scope and add it to the #mydaily-report channel.
- Google Sheet: A Sheet with a Sheet1 tab and the correct Spreadsheet ID.
- Python 3.8+: Ensure Python is installed.
- Internet Connection: Required for API calls.

## Logging
- All actions and errors are logged to log.txt and the console.

### Logs include:
- Google authentication status
- Email fetching and summarization details
- Google Sheet updates
- Slack notification status
- Error messages with troubleshooting tips

### Notes on Project Files
- **credentials.json**: Not tracked in Git; users must download it from Google Cloud Console.
- **token.json**: Generated after Google authentication; not tracked to avoid exposing sensitive data.
- **log.txt**: Stores logs (replaces `print` statements for file-based logging in a production setup).
- **run_daily_report.bat**: A batch file for Windows users to run the script easily (assumed to contain `python main.py`).
- **.env**: Stores sensitive API keys, not tracked in Git.
- **requirements.txt**: Lists all dependencies for easy installation.