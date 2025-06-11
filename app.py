import os
import base64
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/spreadsheets']

# Configuration
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL = '#mydaily-report'
SPREADSHEET_ID = '1QQ8bZUodwLTs_lc8Vxry_EoPIhdGb8kaHtQN19ScfAc'
SHEET_RANGE = 'Sheet1!A:B'
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Validate environment variables
if not SLACK_BOT_TOKEN or not GROQ_API_KEY:
    print("Error: SLACK_BOT_TOKEN and GROQ_API_KEY must be set in .env file.")
    exit(1)

groq_client = Groq(api_key=GROQ_API_KEY)


def authenticate_google():
    """Authenticate with Google APIs."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        print("Google authentication required. Running local server for authentication...")
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def get_gmail_service():
    """Create Gmail API service."""
    return build('gmail', 'v1', credentials=authenticate_google())


def get_sheets_service():
    """Create Google Sheets API service."""
    return build('sheets', 'v4', credentials=authenticate_google())


def summarize_text(text, max_length=130):
    """Summarize text into 1-2 sentences."""
    if not text:
        return "No readable content."
    try:
        prompt = f"Summarize the following text in 1-2 sentences (max {max_length} words):\n\n{text}"
        completion = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_length,
            stream=False
        )
        summary = completion.choices[0].message.content.strip()
        return summary[:50000]  # Truncate to avoid cell size limit
    except Exception as e:
        print(f"Error summarizing with Groq: {e}")
        return text[:max_length]


def extract_body(payload):
    """Extract email body, handling multipart."""
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] in ['text/plain', 'text/html']:
                body = base64.urlsafe_b64decode(
                    part['body']['data']).decode('utf-8')
                break
            elif part['mimeType'] == 'multipart':
                body = extract_body(part)
                if body:
                    break
    elif payload['mimeType'] in ['text/plain', 'text/html']:
        body = base64.urlsafe_b64decode(
            payload['body']['data']).decode('utf-8')
    return body


def get_emails():
    """Fetch emails between 12:01 AM and 9:01 AM BDT, with pagination."""
    service = get_gmail_service()

    # Define Bangladesh timezone (UTC+6)
    bdt_tz = pytz.timezone('Asia/Dhaka')

    # Get current date in BDT
    now_bdt = datetime.now(bdt_tz)
    current_date = now_bdt.date()

    # Define time range in BDT
    start_time_bdt = datetime.combine(current_date, datetime.min.time(
    ), tzinfo=bdt_tz) + timedelta(minutes=1)  # 12:01 AM BDT
    end_time_bdt = datetime.combine(current_date, datetime.min.time(
    ), tzinfo=bdt_tz) + timedelta(hours=9, minutes=1)  # 9:01 AM BDT

    # Convert to UTC for Gmail API
    start_time_utc = start_time_bdt.astimezone(pytz.UTC)
    end_time_utc = end_time_bdt.astimezone(pytz.UTC)

    # Convert to Unix timestamps
    start_timestamp = int(start_time_utc.timestamp())
    end_timestamp = int(end_time_utc.timestamp())

    # Gmail API query using timestamps
    query = f'after:{start_timestamp} before:{end_timestamp} -in:spam -in:trash'
    print(f"Fetching emails with query: {query}")

    email_data = []
    total_emails = 0
    page_token = None
    page_number = 1

    while True:
        try:
            request = service.users().messages().list(
                userId='me', q=query, maxResults=100, pageToken=page_token)
            results = request.execute()
            messages = results.get('messages', [])
            total_emails += len(messages)
            print(
                f"Page {page_number} (Token: {page_token}): Found {len(messages)} emails, Total so far: {total_emails}")

            for message in messages:
                try:
                    msg = service.users().messages().get(
                        userId='me', id=message['id']).execute()
                    headers = msg['payload']['headers']
                    subject = next((header['value'] for header in headers if header['name'].lower(
                    ) == 'subject'), 'No Subject')

                    body = extract_body(msg['payload'])
                    summarized_body = summarize_text(body)
                    email_data.append([subject, summarized_body])
                    print(f"Processed email: {subject}")
                except Exception as e:
                    print(f"Error processing email {message['id']}: {e}")
                    continue

            page_token = results.get('nextPageToken')
            print(f"Next page token: {page_token}")
            page_number += 1
            if not page_token:
                print("All emails have been fetched.")
                break

            # Add a delay to avoid hitting Gmail API rate limits
            time.sleep(1)

        except Exception as e:
            print(f"Error fetching email page {page_number}: {e}")
            break

    print(f"Total emails processed: {total_emails}")
    return email_data


def clear_google_sheet():
    """Clear the Sheet range before writing."""
    service = get_sheets_service()
    try:
        service.spreadsheets().values().clear(
            spreadsheetId=SPREADSHEET_ID, range='Sheet1!A:B').execute()
        print("Cleared Google Sheet range Sheet1!A:B.")
    except Exception as e:
        print(f"Error clearing Google Sheet: {e}")


def update_google_sheet(data):
    """Update Google Sheet with email summaries."""
    service = get_sheets_service()
    if not data:
        data = [
            ["No emails", f"No emails found on {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}"]]
    body = {'values': data}
    print(f"Updating Google Sheet with {len(data)} rows.")

    try:
        # Verify spreadsheet
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID).execute()
        print(f"Spreadsheet found: {spreadsheet['properties']['title']}")
        sheets = spreadsheet.get('sheets', [])
        print("Available sheet tabs:", [
              sheet['properties']['title'] for sheet in sheets])

        # Clear Sheet
        clear_google_sheet()

        # Write data
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE,
            valueInputOption='RAW',
            body=body
        ).execute()
        print("Google Sheet updated successfully.")
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")
        raise


def send_slack_message(email_data):
    """Send Slack notification with email summaries."""
    client = WebClient(token=SLACK_BOT_TOKEN)
    if not email_data:
        message = "No new emails found. Google Sheet updated with placeholder."
    else:
        message = f"Daily Report: Processed {len(email_data)} emails and updated Google Sheet.\n\nSummaries:\n"
        for i, (subject, summary) in enumerate(email_data[:5], 1):
            message += f"{i}. {subject}: {summary}\n"
        if len(email_data) > 5:
            message += f"...and {len(email_data) - 5} more emails."
    try:
        print(f"Sending message to {SLACK_CHANNEL}")
        client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
        print("Message sent successfully to Slack.")
    except SlackApiError as e:
        print(f"Error sending to Slack: {e.response['error']}")
        raise


def main():
    """Run daily reporting automation."""
    print("Starting daily report automation...")
    email_data = get_emails()
    update_google_sheet(email_data)
    send_slack_message(email_data)
    print("Daily report completed successfully.")


if __name__ == '__main__':
    main()
