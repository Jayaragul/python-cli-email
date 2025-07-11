import email
import numpy as np
from imap_client import get_imap_connection
from sentence_transformers import SentenceTransformer
import faiss
from email import message_from_bytes

# Load MPNet model
model = SentenceTransformer("all-mpnet-base-v2")

def extract_email_body(msg_obj):
    """Extract plain text from an email message object."""
    body = ""
    if msg_obj.is_multipart():
        for part in msg_obj.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
                except:
                    continue
    else:
        try:
            body = msg_obj.get_payload(decode=True).decode(errors="ignore")
        except:
            pass
    return body

def semantic_search_emails(query, limit=20):
    """Perform semantic search on the last N emails using MPNet + FAISS (cosine similarity)."""
    try:
        imap = get_imap_connection()
        imap.select("inbox")
        status, data = imap.search(None, "ALL")
        email_ids = data[0].split()

        if not email_ids:
            print("📭 No emails found.")
            return

        # Select the most recent N email IDs
        email_ids = email_ids[-limit:]
        emails, texts = [], []

        print(f"\n📥 Fetching last {limit} emails...\n")
        for eid in reversed(email_ids):
            _, msg_data = imap.fetch(eid, "(RFC822)")
            for resp in msg_data:
                if isinstance(resp, tuple):
                    msg_obj = message_from_bytes(resp[1])
                    subject = msg_obj.get("Subject", "")
                    sender = msg_obj.get("From", "")
                    date = msg_obj.get("Date", "")
                    body = extract_email_body(msg_obj)

                    combined = f"{subject}\n{body}".strip().replace("\r", "")
                    emails.append({
                        "subject": subject,
                        "from": sender,
                        "date": date,
                        "preview": body[:300],
                        "combined": combined
                    })
                    texts.append(combined)

        print("🧠 Encoding with MPNet...")
        vectors = model.encode(texts, show_progress_bar=False)
        vectors = np.array(vectors)
        vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)  # Normalize

        query_vec = model.encode([query])
        query_vec = query_vec / np.linalg.norm(query_vec, axis=1, keepdims=True)

        index = faiss.IndexFlatIP(vectors.shape[1])  # Inner Product = Cosine
        index.add(vectors)

        D, I = index.search(query_vec, k=min(5, len(emails)))  # Top 5 results

        print(f"\n🔍 Top semantic matches for: '{query}'\n")
        results = sorted(zip(D[0], I[0]), key=lambda x: -x[0])  # Highest score = best

        for rank, (score, idx) in enumerate(results, 1):
            mail = emails[idx]
            print("=" * 60)
            print(f"🏅 Rank    : {rank}")
            print(f"📧 Subject : {mail['subject']}")
            print(f"👤 From    : {mail['from']}")
            print(f"🕒 Date    : {mail['date']}")
            print(f"📄 Preview : {mail['preview'].strip()}...")
            print(f"📊 Score   : {score:.4f}\n")

        imap.logout()

    except Exception as e:
        print(f"❌ Error: {e}")
