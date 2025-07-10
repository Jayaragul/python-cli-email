def prompt_email_limit():
    while True:
        try:
            limit = int(input("Enter how many latest emails to fetch (e.g., 10, 20): "))
            if limit > 0:
                return limit
        except ValueError:
            pass
        print("❌ Invalid input. Please enter a positive number.")
