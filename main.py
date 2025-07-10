from limit_prompt import prompt_email_limit
from list_prompt import list_emails
from fetch_emails import fetch_email_by_number
from search_emails import search_emails

def main():
    print("📬 Welcome to CLI Email Viewer")
    limit = prompt_email_limit()

    while True:
        print("\nChoose an option:")
        print("1️⃣  List Emails")
        print("2️⃣  Fetch Particular Email")
        print("3️⃣  Search Emails")
        print("0️⃣  Exit")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            list_emails(limit)
        elif choice == "2":
            try:
                number = int(input("Enter email number to fetch: "))
                fetch_email_by_number(limit, number)
            except ValueError:
                print("❌ Invalid number.")
        elif choice == "3":
            keyword = input("Enter keyword to search (subject/body): ")
            search_emails(keyword)
        elif choice == "0":
            print("👋 Exiting...")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
