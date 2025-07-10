import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

def get_imap_connection():
    imap = imaplib.IMAP4_SSL(os.getenv("IMAP_HOST"), int(os.getenv("IMAP_PORT")))
    imap.login(os.getenv("IMAP_USER"), os.getenv("IMAP_PASSWORD"))
    imap.select("inbox")
    return imap
