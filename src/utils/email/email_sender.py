import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests

from dotenv import load_dotenv

from logs.logger import logger


load_dotenv()


SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv(
    "RECEIVER_EMAIL", SENDER_EMAIL
)  # Defaults to sender if not set


def fetch_motivational_quote() -> str:
    """Return a motivational quote in HTML format."""
    try:
        resp = requests.get("https://zenquotes.io/api/random")
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                q = data[0].get("q", "Keep pushing forward.")
                a = data[0].get("a", "Anonymous")
                return f"<hr><blockquote><em>“{q}”<br>– {a}</em></blockquote>"
            logger.warning("Unexpected response structure from quote API.")
        else:
            logger.warning(f"Failed to fetch quote: Status {resp.status_code}")
    except Exception as e:
        logger.error(f"Error fetching quote: {e}")

    return (
        "<hr><blockquote><em>“You're not stuck. "
        "The API is.” – Monday</em></blockquote>"
    )


def send_job_listings_email() -> bool | None:
    """Send top 10 job listings via email."""
    logger.info("-" * 60)
    logger.info("Sending job listings via email...")

    # function doesn't work for now!!!
    # in the future email logic can be here
    vacancies = None
    if not vacancies:
        logger.info("No vacancies found")
        return None

    jobs = vacancies[:10]
    if not jobs:
        logger.info("No vacancies to send in email.")
        return False

    html = "<h2>Top 10 Job Vacancies 🏢</h2><ul>"
    for job in jobs:
        html += (
            f"<li><strong>{job.get('title', 'No title')}</strong> at "
            f"{job.get('company', 'Unknown company')}<br>"
            f"Rating: {job.get('score', 'No score')}<br>"
            f"<a href='{job.get('url', '')}'>Job Link</a></li><br>"
        )
    html += "</ul>" + fetch_motivational_quote()

    # Create email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Top 10 Job Listings 📩"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        logger.info("Job listings email sent successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


if __name__ == "__main__":
    send_job_listings_email()
