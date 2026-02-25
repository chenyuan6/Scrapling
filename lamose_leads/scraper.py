"""
Lamose Lead Scraper
-------------------
Finds business emails from public sources for outreach.

Usage:
    python scraper.py --source google_maps --query "e-commerce brands Toronto" --limit 50
    python scraper.py --source instagram --handles @brand1 @brand2
    python scraper.py --source website --urls urls.txt
"""

import re
import csv
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from scrapling.fetchers import Fetcher, StealthyFetcher

# ── Regex to extract emails from raw HTML/text ──────────────────────────────
EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)

# Emails to filter out (noise)
SKIP_DOMAINS = {
    "example.com", "sentry.io", "wix.com", "squarespace.com",
    "wordpress.com", "shopify.com", "gmail.com", "yahoo.com",
    "hotmail.com", "placeholder.com", "yourdomain.com",
}


def clean_emails(raw: list[str]) -> list[str]:
    seen = set()
    out = []
    for e in raw:
        e = e.lower().strip()
        domain = e.split("@")[-1]
        if domain in SKIP_DOMAINS:
            continue
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out


def extract_emails(text: str) -> list[str]:
    return clean_emails(EMAIL_RE.findall(text))


# ── Source: Scrape a list of websites directly ───────────────────────────────
def scrape_websites(urls: list[str]) -> list[dict]:
    fetcher = Fetcher(auto_match=False)
    results = []

    for url in urls:
        url = url.strip()
        if not url:
            continue
        print(f"  Fetching: {url}")
        try:
            page = fetcher.get(url, timeout=15)
            if page is None:
                print(f"    [skip] No response")
                continue

            emails = extract_emails(page.html_content)

            # Try /contact page if no emails found on homepage
            if not emails and not url.rstrip("/").endswith("/contact"):
                contact_url = url.rstrip("/") + "/contact"
                print(f"    Trying contact page: {contact_url}")
                try:
                    contact_page = fetcher.get(contact_url, timeout=10)
                    if contact_page:
                        emails = extract_emails(contact_page.html_content)
                except Exception:
                    pass

            results.append({
                "source": url,
                "emails": ", ".join(emails) if emails else "",
                "email_count": len(emails),
                "scraped_at": datetime.now().isoformat(),
            })
            print(f"    Found {len(emails)} email(s): {emails}")

        except Exception as e:
            print(f"    [error] {e}")
            results.append({
                "source": url,
                "emails": "",
                "email_count": 0,
                "scraped_at": datetime.now().isoformat(),
            })

    return results


# ── Source: Google search "site:domain email" ────────────────────────────────
def scrape_google_search(query: str, limit: int = 30) -> list[dict]:
    """
    Searches Google for the query and collects links, then scrapes each site.
    Uses StealthyFetcher to avoid bot detection on Google.
    """
    fetcher = StealthyFetcher(auto_match=False)
    results = []
    collected_urls = []

    pages_needed = (limit // 10) + 1
    for page_num in range(pages_needed):
        start = page_num * 10
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&start={start}"
        print(f"  Google search page {page_num + 1}: {search_url}")

        try:
            page = fetcher.get(search_url, timeout=20)
            if page is None:
                break

            # Extract result links
            links = page.css("a[href]")
            for link in links:
                href = link.attrib.get("href") or ""
                if href.startswith("http") and "google.com" not in href:
                    collected_urls.append(href)
                if len(collected_urls) >= limit:
                    break

        except Exception as e:
            print(f"    [error] Google search: {e}")
            break

    print(f"  Collected {len(collected_urls)} URLs from search")
    results = scrape_websites(collected_urls[:limit])
    return results


# ── Source: Read URLs from a text file ───────────────────────────────────────
def scrape_from_file(filepath: str) -> list[dict]:
    urls = Path(filepath).read_text().splitlines()
    print(f"  Loaded {len(urls)} URLs from {filepath}")
    return scrape_websites(urls)


# ── Output: Save to CSV ──────────────────────────────────────────────────────
def save_csv(results: list[dict], output_path: str):
    if not results:
        print("No results to save.")
        return

    fieldnames = ["source", "emails", "email_count", "scraped_at"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    total_emails = sum(r["email_count"] for r in results)
    print(f"\n✓ Saved {len(results)} records ({total_emails} emails total) → {output_path}")


# ── CLI ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Lamose Lead Scraper")
    parser.add_argument("--source", choices=["website", "google", "file"], required=True,
                        help="Scraping source type")
    parser.add_argument("--urls", nargs="+", help="Direct URLs to scrape (for --source website)")
    parser.add_argument("--query", help="Search query (for --source google)")
    parser.add_argument("--limit", type=int, default=30, help="Max results from Google search")
    parser.add_argument("--file", help="Path to .txt file with URLs (for --source file)")
    parser.add_argument("--output", default="leads_output.csv", help="Output CSV filename")
    args = parser.parse_args()

    print(f"\n=== Lamose Lead Scraper ===")
    print(f"Source: {args.source} | Output: {args.output}\n")

    results = []

    if args.source == "website":
        if not args.urls:
            print("Error: --urls required for --source website")
            return
        results = scrape_websites(args.urls)

    elif args.source == "google":
        if not args.query:
            print("Error: --query required for --source google")
            return
        results = scrape_google_search(args.query, args.limit)

    elif args.source == "file":
        if not args.file:
            print("Error: --file required for --source file")
            return
        results = scrape_from_file(args.file)

    save_csv(results, args.output)


if __name__ == "__main__":
    main()
