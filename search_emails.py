import sys
import faiss
import email
import numpy as np
from datetime import datetime
from email import message_from_bytes
from sentence_transformers import SentenceTransformer
from imap_client import get_imap_connection
from filer import apply_filters  # Make sure this is implemented

# Load once
model = SentenceTransformer("all-mpnet-base-v2")

def extract_email_body(msg_obj):
    """Safely extract plain text body from an email message object."""
    body = ""
    if msg_obj.is_multipart():
        for part in msg_obj.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
                except Exception:
                    continue
    else:
        try:
            body = msg_obj.get_payload(decode=True).decode(errors="ignore")
        except Exception:
            pass
    return body


def semantic_search_emails(query, limit=20, from_date=None, to_date=None, sender=None):
    """
    Semantic search across last N emails using MPNet + FAISS.
    Applies optional filters: from_date, to_date, sender.
    """
    try:
        imap = get_imap_connection()
        imap.select("inbox")
        status, data = imap.search(None, "ALL")
        email_ids = data[0].split()

        if not email_ids:
            print("📭 Inbox is empty.")
            return

        email_ids = email_ids[-limit:]  # pick last `limit` emails
        raw_emails, texts = [], []

        print(f"\n📥 Fetching last {limit} emails...\n")
        for eid in reversed(email_ids):
            _, msg_data = imap.fetch(eid, "(RFC822)")
            for resp in msg_data:
                if isinstance(resp, tuple):
                    try:
                        msg_obj = message_from_bytes(resp[1])
                        subject = msg_obj.get("Subject", "")
                        sender_ = msg_obj.get("From", "")
                        date = msg_obj.get("Date", "")
                        body = extract_email_body(msg_obj)

                        combined = f"{subject}\n{body}".strip().replace("\r", "")
                        if len(combined) > 20:
                            raw_emails.append({
                                "subject": subject,
                                "from": sender_,
                                "date": date,
                                "preview": body[:300],
                                "combined": combined
                            })
                            texts.append(combined)
                    except Exception:
                        continue

        if not raw_emails:
            print("⚠️ No valid emails found.")
            return

        # Apply filters
        filtered_emails = apply_filters(raw_emails, from_date, to_date, sender)

        if not filtered_emails:
            print("❌ No emails matched your filters. Exiting.")
            sys.exit(0)

        texts = [e["combined"] for e in filtered_emails]

        # Embedding
        print("🧠 Embedding emails with MPNet...")
        vectors = model.encode(texts, show_progress_bar=False)
        vectors = np.array(vectors)
        vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

        # Query encoding
        print("🔎 Embedding your query...")
        query_vec = model.encode([query])
        query_vec = query_vec / np.linalg.norm(query_vec, axis=1, keepdims=True)

        # Search
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        D, I = index.search(query_vec, k=min(5, len(filtered_emails)))

        print(f"\n🔍 Top matches for query: '{query}'\n")
        results = sorted(zip(D[0], I[0]), key=lambda x: -x[0])

        for rank, (score, idx) in enumerate(results, 1):
            mail = filtered_emails[idx]
            print("=" * 60)
            print(f"🏅 Rank    : {rank}")
            print(f"📧 Subject : {mail['subject']}")
            print(f"👤 From    : {mail['from']}")
            print(f"🕒 Date    : {mail['date']}")
            print(f"📄 Preview : {mail['preview'].strip()}...")
            print(f"📊 Score   : {score:.4f}\n")

        imap.logout()

    except Exception as e:
        print(f"❌ Semantic search failed: {e}")
