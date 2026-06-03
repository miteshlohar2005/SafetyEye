import smtplib
from email.message import EmailMessage
import time
import threading

# Simple rate limiter: don't send email for same violation type within 60 seconds
last_sent = {}

def send_alert_email(to_email, subject, body, image_path=None, sender_email="", sender_password=""):
    """
    Sends an email alert. 
    image_path: Path to the image file to attach.
    """
    if not sender_email or not sender_password or not to_email:
        return False, "Credentials missing"

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(body)

    if image_path:
        try:
            with open(image_path, 'rb') as f:
                img_data = f.read()
                msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename='violation.jpg')
        except Exception as e:
            print(f"Could not attach image: {e}")

    try:
        # Assuming Gmail for now, can be configured
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)

def async_send_email(violation_types, image_path, config):
    """
    Wrapper to send email in a thread with rate limiting.
    config: dict with 'email_enabled', 'sender_email', 'sender_password', 'receiver_email'
    """
    if not config.get('email_enabled'):
        return

    # Check cooldown
    current_time = time.time()
    # Create a unique key for this batch of violations
    key = ",".join(sorted(violation_types))
    
    if key in last_sent and (current_time - last_sent[key] < 60):
        return # Skip if sent recently

    last_sent[key] = current_time
    
    subject = f"🚨 SAFETY VIOLATION DETECTED: {key.upper()}"
    body = f"A safety violation was detected at {time.ctime()}.\n\nViolations: {', '.join(violation_types)}\n\nPlease take immediate action."

    # Threading to not block UI
    t = threading.Thread(target=send_alert_email, args=(
        config.get('receiver_email'),
        subject,
        body,
        image_path,
        config.get('sender_email'),
        config.get('sender_password')
    ))
    t.start()
