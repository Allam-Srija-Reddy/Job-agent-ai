import os
import base64
import pickle
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import gspread
from tavily import TavilyClient
from crewai.tools import tool

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_creds():
    creds = None
    if os.path.exists('token.pkl'):
        with open('token.pkl', 'rb') as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pkl', 'wb') as f:
            pickle.dump(creds, f)
    return creds


@tool("Search Jobs")
def search_jobs(query: str) -> str:
    """Search for job postings using Tavily. Input should be a job search query string."""
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        results = client.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )
        jobs = []
        for r in results.get('results', []):
            jobs.append({
                'title': r.get('title', 'N/A'),
                'url': r.get('url', 'N/A'),
                'content': r.get('content', 'N/A')[:500]
            })
        return json.dumps(jobs, indent=2)
    except Exception as e:
        return f"Error searching jobs: {str(e)}"


@tool("Send Email")
def send_email(to_email: str, subject: str, body: str, resume_path: str = None) -> str:
    """Send an email with optional resume attachment via Gmail API."""
    try:
        creds = get_google_creds()
        service = build('gmail', 'v1', credentials=creds)

        msg = MIMEMultipart()
        msg['From'] = os.getenv("SENDER_EMAIL")
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        if resume_path and os.path.exists(resume_path):
            with open(resume_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(resume_path)}"')
            msg.attach(part)

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId='me', body={'raw': raw}).execute()
        return f"Email sent successfully to {to_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"


@tool("Track Application")
def track_application(data: str) -> str:
    """Track a job application in Google Sheets. Input should be JSON with keys: name, role, company, status, email, date."""
    try:
        creds = get_google_creds()
        gc = gspread.authorize(creds)

        try:
            sh = gc.open("Job Applications Tracker")
            worksheet = sh.sheet1
        except:
            sh = gc.create("Job Applications Tracker")
            worksheet = sh.sheet1
            worksheet.append_row([
                "Name", "Role", "Company", "Status",
                "Email Sent To", "Date Applied", "Notes"
            ])
            sh.share(os.getenv("SENDER_EMAIL"), perm_type='user', role='writer')

        info = json.loads(data)
        worksheet.append_row([
            info.get("name", ""),
            info.get("role", ""),
            info.get("company", ""),
            info.get("status", "Applied"),
            info.get("email", ""),
            info.get("date", datetime.now().strftime("%Y-%m-%d")),
            info.get("notes", "")
        ])
        return f"Application tracked successfully in Google Sheets"
    except Exception as e:
        return f"Error tracking application: {str(e)}"


@tool("Read Resume")
def read_resume(file_path: str) -> str:
    """Read and extract text from a PDF resume file."""
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text[:3000]
    except Exception as e:
        return f"Error reading resume: {str(e)}"
