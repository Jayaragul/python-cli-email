from limit_prompt import prompt_email_limit
from list_prompt import list_emails
from fetch_emails import fetch_email_by_number
from search_emails import semantic_search_emails
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

def parse_date(input_str):
    try:
        return datetime.strptime(input_str.strip(), "%Y-%m-%d")
    except ValueError:
        return None

def main():
    print("📬 Welcome to CLI Email Viewer")

    # Step 1: Get number of emails to load
    limit = prompt_email_limit()

    # Step 2: Optional filters
    print("\nOptional Filters (Press Enter to skip):")
    from_date = parse_date(input("📅 From date (YYYY-MM-DD): ") or "")
    to_date = parse_date(input("📅 To date (YYYY-MM-DD): ") or "")
    from_addr = input("📨 Filter by sender email: ").strip() or None

    while True:
        print("\nChoose an option:")
        print("1️⃣  List Emails")
        print("2️⃣  Fetch Particular Email")
        print("3️⃣  Search Emails (Semantic)")
        print("0️⃣  Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            list_emails(limit, from_date, to_date, from_addr)

        elif choice == "2":
            try:
                number = int(input("Enter email number to fetch: "))
                if number <= 0:
                    print("❌ Invalid number. Must be > 0.")
                    continue
                fetch_email_by_number(limit, number)
            except ValueError:
                print("❌ Please enter a valid number.")

        elif choice == "3":
            keyword = input("Enter keyword to search (semantic): ").strip()
            if keyword:
                semantic_search_emails(keyword, limit, from_date, to_date, from_addr)
            else:
                print("❗ Please enter a keyword.")

        elif choice == "0":
            print("👋 Exiting...")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
