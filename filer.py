from datetime import datetime
from email.utils import parsedate_to_datetime

def apply_filters(emails, from_date=None, to_date=None, sender=None):
    filtered = []
    for mail in emails:
        try:
            mail_date = parsedate_to_datetime(mail.get("date")).date()
            if from_date and mail_date < from_date:
                continue
            if to_date and mail_date > to_date:
                continue
            if sender and sender.lower() not in mail.get("from", "").lower():
                continue
            filtered.append(mail)
        except Exception:
            continue
    return filtered
