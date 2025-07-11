from limit_prompt import prompt_email_limit
from list_prompt import list_emails
from fetch_emails import fetch_email_by_number
from search_emails import semantic_search_emails  # 🔄 updated import

def main():
    print("📬 Welcome to CLI Email Viewer")
    limit = prompt_email_limit()

    while True:
        print("\nChoose an option:")
        print("1️⃣  List Emails")
        print("2️⃣  Fetch Particular Email")
        print("3️⃣  Search Emails (Semantic)")
        print("0️⃣  Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            list_emails(limit)

        elif choice == "2":
             try:
                  number = int(input("Enter email number to fetch: "))
                  if number <= 0:
                    print("❌ Invalid number. Please enter a number greater than 0.")
                    continue  # go back to the menu
                  fetch_email_by_number(limit, number)
             except ValueError:
                    print("❌ Invalid input. Please enter a valid number.")


        elif choice == "3":
            keyword = input("Enter keyword to search (semantic): ").strip()
            if keyword:
                semantic_search_emails(keyword, limit)  # 🔍 now semantic
            else:
                print("❗ Please enter a keyword.")

        elif choice == "0":
            print("👋 Exiting...")
            break

        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
