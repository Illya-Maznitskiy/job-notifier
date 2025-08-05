import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from pathlib import Path
import requests

from dotenv import load_dotenv

from logs.logger import logger


load_dotenv()  # Load .env file

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv(
    "RECEIVER_EMAIL", SENDER_EMAIL
)  # Defaults to sender if not set

FILTERED_FILE = (
    Path(__file__).resolve().parent.parent
    / "storage"
    / "filtered_vacancies.json"
)


def fetch_motivational_quote():
    """
    Fetch a motivational quote from zenquotes.io
    Returns a formatted HTML string or fallback string on failure
    """
    try:
        response = requests.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                quote = data[0].get("q", "Keep pushing forward.")
                author = data[0].get("a", "Anonymous")
                return f"<hr><blockquote><em>“{quote}”<br>– {author}</em></blockquote>"
            else:
                logger.warning("Unexpected response structure from quote API.")
        else:
            logger.warning(
                f"Failed to fetch quote: Status {response.status_code}"
            )
    except Exception as e:
        logger.error(f"Error fetching quote: {e}")

    # fallback for broken internet and broken dreams
    return "<hr><blockquote><em>“You're not stuck. The API is.” – Monday, local sarcasm distributor</em></blockquote>"


def send_job_listings_email():
    logger.info("-" * 60)
    logger.info("Sending job listings via email...")

    if not FILTERED_FILE.exists():
        logger.warning(f"Vacancies file not found: {FILTERED_FILE}")
        return False

    with open(FILTERED_FILE, "r", encoding="utf-8") as f:
        vacancies = json.load(f)

    # Prepare first 10 jobs summary
    jobs_to_send = vacancies[:10]

    if not jobs_to_send:
        logger.info("No vacancies to send in email.")
        return False

    # Build HTML email content
    html_content = "<h2>Top 10 Job Vacancies 🏢</h2><ul>"
    for job in jobs_to_send:
        title = job.get("title", "No title")
        company = job.get("company", "Unknown company")
        url = job.get("url", "")
        score = job.get("score", "No score")
        html_content += (
            f"<li><strong>{title}</strong> at {company}<br>"
            f"Rating: {score}<br>"
            f"<a href='{url}'>Job Link</a></li><br>"
        )
    html_content += "</ul>"
    html_content += fetch_motivational_quote()

    # Create email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Top 10 Job Listings 📩"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure connection
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        logger.info("Job listings email sent successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


if __name__ == "__main__":
    send_job_listings_email()
