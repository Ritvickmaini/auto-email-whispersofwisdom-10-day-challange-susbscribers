import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# ------------------ CONFIG ------------------
API_URL = "https://whispersofwisdom.co.uk/wp-json/custom-api/v1/protected/10daychallenge"
API_TOKEN = "a53097d7d282f645f12df7333e5d9e3f5c8735b07d5774eb8b1c0c0a4d16c73d"

# Scopes: Sheets + Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SERVICE_ACCOUNT_FILE = "/etc/secrets/service_account.json"
SHEET_NAME = "whispersofwisdom-10 day challange susbscribers"        # Google Sheet file name
TAB_NAME = "Leads"          # Tab name inside the sheet

SMTP_SERVER = "mail.whispersofwisdom.co.uk"
SMTP_PORT = 587
EMAIL_USER = "santosh@whispersofwisdom.co.uk"
EMAIL_PASS = "hKBm[Q8F6l6T"

# ------------------ EMAIL TEMPLATES ------------------
EMAIL_SUBJECTS = [
    "Welcome to the Whispers of Wisdom 10 Day Challenge - Your journey starts now",
    "Whispers of Wisdom Challenge Day 1 - Clear the noise. Find your focus.",
    "Whispers of Wisdom Challenge Day 2 - Who you become matters more than what you achieve",
    "Whispers of Wisdom Challenge Day 3 - Turning setbacks into stepping stones",
    "Whispers of Wisdom Challenge Day 3 – A gift to continue your journey",
    "Whispers of Wisdom Challenge Day 4 - Find your strength in stillness",
    "Whispers of Wisdom Challenge Day 5 - Listening is the secret to leadership",
    "Whispers of Wisdom Challenge Day 6 - Change your lens, change your world",
    "Did you grab your free Companion Journal yet?",
    "Whispers of Wisdom Challenge Day 7 - Honesty—the key to unlocking your potential",
    "Whispers of Wisdom Challenge Day 8 - Intention: the secret to real success",
    "Whispers of Wisdom Challenge Day 9 - Renewal is not starting over—it’s starting wiser",
    "Whispers of Wisdom Challenge Day 10 - Success is found in whispers, not shouts",
    "Last chance to grab your free Whispers of Wisdom Journal",
]

EMAIL_BODIES = [
    # Email 1 - Welcome
    """<p>Hi {name},</p>
    <p>Thank you for signing up for the 10-Day “Whispers of Wisdom” Challenge!</p>
    <p>Over the next 10 days, you’ll receive one short, powerful email each morning. Each message includes:<br>
    - A thought-provoking insight — a whisper of wisdom to shift your mindset.<br>
    - A simple daily action — something you can apply immediately.<br>
    - A reflection — helping you build clarity, confidence, and lasting habits.</p>
    <p>By the end of the challenge, you’ll have:<br>
    • A stronger, more focused mindset.<br>
    • Simple habits you can carry forward.<br>
    • A renewed sense of clarity and purpose.</p>
    <p><b>Your Call to Action:</b><br>
    • Each day, take 5 minutes to complete the reflection or action step.<br>
    • Reply to my emails if you’d like to share your progress.<br>
    • Keep an eye out for tomorrow’s first Whisper: “The Power of Clarity.”</p>
    <p>Here’s to the journey ahead,<br>Santosh Kumar</p>
    <p>P.S. You don’t need to prepare anything — just open tomorrow’s email, read, reflect, and take action.</p>""",

    # Email 2 - Day 1
    """<p>Hi {name},</p>
    <p><i>“The smallest whisper of clarity can silence the loudest noise of confusion.”</i></p>
    <p>Clarity is often more powerful than endless information. It gives you the confidence to cut through the noise and focus on what really matters.</p>
    <p><b>Your Action Today:</b> Write down your top 3 priorities for today. Let go of everything else.</p>
    <p>Clarity creates focus. Focus creates results.</p>
    <p>To more clarity,<br>Santosh Kumar</p>""",

    # Email 3 - Day 2
    """<p>Hi {name},</p>
    <p><i>“True success begins not in what you achieve, but in who you become along the journey.”</i></p>
    <p>Real success is not measured only in trophies, titles, or bank balances. It’s measured in growth, resilience, and integrity.</p>
    <p><b>Your Action Today:</b> Ask yourself: Am I becoming the person I want to be? Write down one small action that brings you closer.</p>
    <p>Becoming with you,<br>Santosh Kumar</p>""",

    # Email 4 - Day 3
    """<p>Hi {name},</p>
    <p><i>“Every setback carries a seed of wisdom, waiting for you to nurture it into strength.”</i></p>
    <p>Failures are not the end—they’re lessons in disguise. Each one gives us new tools, new strength, and a deeper resilience.</p>
    <p><b>Your Action Today:</b> Think of one recent setback. Write down the lesson it taught you.</p>
    <p>With strength,<br>Santosh Kumar</p>""",

    # Email 5 - Gift
    """<p>Hi {name},</p>
    <p>I hope you’ve been enjoying the little nuggets of wisdom and putting them into action.</p>
    <p>To help you keep the momentum going, I’ve created a <b>Whispers of Wisdom Companion Journal</b> you can download for free.</p>
    <p><a href="#">[Download your free journal now]</a></p>
    <p>With gratitude,<br>Santosh Kumar</p>""",

    # Email 6 - Day 4
    """<p>Hi {name},</p>
    <p><i>“Stillness is not the absence of movement, but the presence of awareness.”</i></p>
    <p>Peace isn’t about escaping life—it’s about being fully present in it.</p>
    <p><b>Your Action Today:</b> Spend 5 quiet minutes just observing your breath.</p>
    <p>With calm,<br>Santosh Kumar</p>""",

    # Email 7 - Day 5
    """<p>Hi {name},</p>
    <p><i>“Great leaders are not those who speak the loudest, but those who listen the deepest.”</i></p>
    <p>True leadership is built on connection, not control. Listening creates trust, and trust creates influence.</p>
    <p><b>Your Action Today:</b> In your next conversation, listen without planning your reply.</p>
    <p>Listening with you,<br>Santosh Kumar</p>""",

    # Email 8 - Day 6
    """<p>Hi {name},</p>
    <p><i>“Your perspective shapes your reality—change the lens, and you change your world.”</i></p>
    <p>Life rarely changes until we do.</p>
    <p><b>Your Action Today:</b> Reframe one challenge you face. Ask: What gift or lesson does this hold?</p>
    <p>To new ways of seeing,<br>Santosh Kumar</p>""",

    # Email 9 - Reminder
    """<p>Hi {name},</p>
    <p>I noticed you haven’t downloaded your Whispers of Wisdom Companion Journal yet.</p>
    <p><a href="#">[Get your free journal now]</a></p>
    <p>Cheering you on,<br>Santosh Kumar</p>""",

    # Email 10 - Day 7
    """<p>Hi {name},</p>
    <p><i>“Honesty with yourself is the first step towards unlocking your hidden potential.”</i></p>
    <p><b>Your Action Today:</b> Write down one truth about yourself you’ve been avoiding.</p>
    <p>With truth,<br>Santosh Kumar</p>""",

    # Email 11 - Day 8
    """<p>Hi {name},</p>
    <p><i>“In both life and business, intention is the compass that turns effort into achievement.”</i></p>
    <p><b>Your Action Today:</b> Set one clear intention for today.</p>
    <p>With purpose,<br>Santosh Kumar</p>""",

    # Email 12 - Day 9
    """<p>Hi {name},</p>
    <p><i>“Renewal is not starting over; it’s starting wiser.”</i></p>
    <p><b>Your Action Today:</b> Choose one area of your life that needs renewal. Restart it smarter this time.</p>
    <p>Renewing with you,<br>Santosh Kumar</p>""",

    # Email 13 - Day 10
    """<p>Hi {name},</p>
    <p><i>“Success whispers to those who dare to pause, reflect, and act with purpose.”</i></p>
    <p><b>Your Action Today:</b> Take 10 minutes to pause. Ask: Am I chasing success, or creating it with purpose?</p>
    <p>To your success,<br>Santosh Kumar</p>""",

    # Email 14 - Final Call
    """<p>Hi {name},</p>
    <p>This is the final call — the Whispers of Wisdom Companion Journal is still waiting for you.</p>
    <p><a href="#">[Download your free journal before it’s gone]</a></p>
    <p>To your continued growth,<br>Santosh Kumar</p>""",
]

# ------------------ GOOGLE SHEETS SETUP ------------------
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build("drive", "v3", credentials=creds)
sheet_service = build("sheets", "v4", credentials=creds)
sheet = sheet_service.spreadsheets()

def get_sheet_id(sheet_name):
    results = drive_service.files().list(
        q=f"name='{sheet_name}' and mimeType='application/vnd.google-apps.spreadsheet'",
        fields="files(id, name)"
    ).execute()
    files = results.get("files", [])
    if not files:
        raise Exception(f"No Google Sheet found with name {sheet_name}")
    return files[0]["id"]

SPREADSHEET_ID = get_sheet_id(SHEET_NAME)

# ------------------ FUNCTIONS ------------------
def fetch_leads_from_api():
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()
    data = response.json()

    leads = []
    if data.get("status") == "success":
        for entry in data.get("data", []):
            form_entry = entry.get("Form_Entry", {})
            name = form_entry.get("Your Name", "").strip()
            email = form_entry.get("Email", "").strip()
            if name and email:
                leads.append({"name": name, "email": email})
    return leads


def append_leads_to_sheet(leads):
    if not leads:
        return

    # Get existing emails from the sheet
    existing_data = get_sheet_data()
    existing_emails = set(row[1].strip().lower() for row in existing_data if len(row) > 1 and row[1].strip())

    # Filter out duplicates
    new_leads = [lead for lead in leads if lead["email"].strip().lower() not in existing_emails]

    if not new_leads:
        print("No new leads to add.")
        return

    values = [[lead["name"], lead["email"], ""] for lead in new_leads]
    body = {"values": values}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{TAB_NAME}!A:C",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()
    print(f"Added {len(new_leads)} new lead(s) to the sheet.")

def get_sheet_data():
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{TAB_NAME}!A:C"
    ).execute()
    return result.get("values", [])[1:]  # skip header

import imaplib

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    # ---- Send via SMTP ----
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    # ---- Save in "Sent" folder via IMAP ----
    try:
        imap = imaplib.IMAP4_SSL(SMTP_SERVER)  # often same server for IMAP
        imap.login(EMAIL_USER, EMAIL_PASS)
        imap.append("INBOX.Sent", '', imaplib.Time2Internaldate(time.time()), str(msg).encode("utf-8"))
        imap.logout()
        print(f"Saved email to Sent: {to_email}")
    except Exception as e:
        print("⚠️ Could not save email to Sent:", e)


def batch_update_status(updates):
    body = {"values": updates}
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{TAB_NAME}!C2",
        valueInputOption="RAW",
        body=body
    ).execute()

# ------------------ MAIN LOOP ------------------
if __name__ == "__main__":
    while True:
        leads = fetch_leads_from_api()
        if leads:
            append_leads_to_sheet(leads)

        data = get_sheet_data()
        updates = []

        for row in data:
            row = row + [""] * (3 - len(row))
            name, email, status = row
            if not email:
                continue

            if status == "":
                email_count = 0
            else:
                email_count = int(status.split("-")[-1])

            if email_count < len(EMAIL_SUBJECTS):
                subject = EMAIL_SUBJECTS[email_count]
                body = EMAIL_BODIES[email_count].format(name=name)
                send_email(email, subject, body)
                new_status = f"Email Sent -{email_count+1}"
                updates.append([new_status])
            else:
                updates.append([status])

        if updates:
            batch_update_status(updates)

        print("Sleeping for 24 hours...")
        time.sleep(86400)
