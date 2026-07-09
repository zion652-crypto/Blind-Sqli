# Blind SQL Injection Extractor (Boolean-Based)

A small Python tool that automates **boolean-based blind SQL injection** — extracting data from a database one character at a time, using only a true/false signal in the application's response, with no visible errors or direct data output.

Built while learning web application security through PortSwigger's Web Security Academy. Shared here for educational purposes and to document my own learning process.

> ⚠️ **For authorized testing only.** Use this exclusively against systems you own, or environments you have explicit written permission to test (such as PortSwigger's own lab environments). Running this against systems you don't have permission to test is illegal.

---

## What is boolean-based blind SQL injection?

Most SQL injection examples show an application leaking data directly — an error message, or extra rows appearing on a page. **Blind** injection is different: the application gives you **no visible sign at all** that anything happened. No error, no extra data.

The only thing you have to work with is a single **true/false signal** — some small difference in the application's behavior depending on whether your injected condition was true or false. Everything else about the response looks identical.

## The core idea, with a scenario

Imagine a hotel booking site. When you're logged in, your dashboard shows a small widget: **"You have 2 upcoming bookings."** When you're *not* logged in (or your session is invalid), that widget simply doesn't appear — the rest of the page looks exactly the same either way.

Now suppose the site has a hidden SQL injection point in a cookie, and the actual query behind the scenes looks like this:

```sql
SELECT * FROM sessions WHERE session_id = 'your_cookie_value'
```

If you inject a condition into that cookie value:

```
your_cookie_value' AND '1'='1
```

The query effectively becomes: *"give me the session matching this ID, AND check that 1 equals 1."* Since `1=1` is always true, this doesn't change anything — the session is still found, and the **"You have 2 upcoming bookings"** widget still appears.

Now try:

```
your_cookie_value' AND '1'='2
```

`1=2` is always false. The `AND` means *both* sides must be true for the row to match — so now the query returns **nothing**, even though your original session ID was valid. The session lookup fails, and the widget **disappears** — even though nothing else about the page changed.

**That disappearing widget is your true/false signal.** You never see an error. You never see raw data. You just see one small thing appear or vanish depending on whether your injected condition was true or false. That's the entire foundation of blind injection: turning "can I see the data?" into "can I ask a yes/no question and observe the answer indirectly?"

## From one true/false answer to extracting a whole password

A single true/false answer isn't very useful on its own. The technique becomes powerful when you ask **many small true/false questions in a row**, each one narrowing down one character of a password.

Instead of asking "is the password `hunter2`?" (a huge, low-probability guess), you ask much smaller, specific questions:

```sql
(SELECT SUBSTRING(password, 1, 1) FROM users WHERE username='administrator') = 'a'
```

This asks: *"Is the 1st character of the administrator's password the letter 'a'?"* True or false, same signal as before (widget appears or doesn't).

If false, try `'b'`, then `'c'`, and so on, until one returns true. Once found, move to position 2, and repeat. Character by character, the full password gets reconstructed — using nothing but a long sequence of true/false answers.

## What this script does

1. Confirms the injection point is exploitable via a sanity check (a condition you already know the answer to)
2. Iterates through each character position of a target column (e.g. `password`)
3. For each position, tries every character in a charset until the true signal appears
4. Builds the extracted value character by character, printing progress live

## Requirements

- Python 3
- `requests` library:
```bash
pip install requests
```

## Usage

```bash
python3 blind_sqli_v2.py
```

You'll be prompted for:

| Prompt | What to enter |
|---|---|
| Target URL | The base URL of the vulnerable page |
| TrackingId cookie value | A **fresh, currently valid** cookie value, grabbed from your browser right before running |
| TRUE signal | Text that appears **only** when your injected condition is true — found by manually testing `' AND '1'='1` vs `' AND '1'='2` first and comparing the two responses |
| Table / column names | The table and columns you're extracting from |
| Target username | The account whose data you're extracting |

## Important limitations

- **You must confirm the vulnerability exists manually first.** This script exploits a known injection point — it doesn't discover one. Test `' AND '1'='1` vs `' AND '1'='2` by hand and confirm a visible difference before using this tool.
- **Assumes the injection point is a cookie named `TrackingId`.** For a different injection point (URL parameter, POST body, a different cookie name), the `check()` function's request-building logic needs to be adapted accordingly.
- **Linear character guessing.** Tries characters roughly A–Z, 0–9 in sequence — average ~18 requests per character. A binary-search approach (asking "is the character's value greater than 'm'?" instead of guessing letters one at a time) would significantly reduce request count — a planned improvement.
- **No rate limiting.** Sends requests as fast as the target responds. Real-world targets may have rate limiting or WAFs that would need to be accounted for.

## Why boolean-based blind injection matters

Most modern, reasonably well-built applications don't leak errors or display raw database output the way older or poorly-configured apps do. That means classic error-based or UNION-based SQL injection often isn't available. Blind injection — inferring data purely from behavioral differences — is frequently the *only* way SQL injection actually gets exploited against real, production applications, which makes it one of the more practically important techniques to understand, even though it's slower and less immediately visible than other forms of SQLi.

---

*Built as part of my personal security learning journey. Feedback and contributions welcome.*
