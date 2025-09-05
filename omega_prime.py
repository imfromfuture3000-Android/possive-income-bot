#!/usr/bin/env python3
"""
OMEGA-PRIME — All-in-One Zero-Cost Crypto Hunter
- Scans airdrop/testnet/quest/bounty feeds
- Scores & logs to CSV + SQLite
- Optional: Telegram/Discord notifications
- Self-commits updates if run on GitHub Actions
"""

import os, hashlib, sqlite3, csv, requests, feedparser, subprocess
from datetime import datetime

# -----------------------------
# CONFIG (edit here if needed)
# -----------------------------
POLL_MINUTES = 15
CSV_PATH = "opportunities.csv"
DB_PATH = "omega.db"

FEEDS = [
    "https://airdrops.io/feed/",
    "https://www.reddit.com/r/airdrops/new/.rss",
    "https://cryptoslate.com/feed/",
    "https://blog.layer3.xyz/feed.xml",
    "https://medium.com/feed/tag/airdrop",
    "https://medium.com/feed/tag/testnet",
    "https://nitter.net/Layer3xyz/rss",
    "https://nitter.net/GalxeHQ/rss"
]

# Notifications (set True + add secrets)
NOTIFY = {
    "telegram": {
        "enabled": False,
        "bot_token": os.getenv("TG_BOT_TOKEN", ""),
        "chat_id": os.getenv("TG_CHAT_ID", "")
    },
    "discord": {
        "enabled": False,
        "webhook_url": os.getenv("DISCORD_WEBHOOK_URL", "")
    }
}

# -----------------------------
# DB Setup
# -----------------------------
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS opportunities (
    id TEXT PRIMARY KEY,
    source TEXT,
    title TEXT,
    url TEXT,
    published TEXT,
    summary TEXT,
    score INTEGER,
    reason TEXT,
    tags TEXT,
    fetched_at TEXT
)
""")
conn.commit()

# -----------------------------
# Core Functions
# -----------------------------
def hash_id(source, url):
    return hashlib.sha256((source + url).encode()).hexdigest()

def score_item(title, summary):
    text = (title + " " + summary).lower()
    score, tags, reasons = 0, [], []
    keywords = {
        "airdrop": 5,
        "testnet": 4,
        "quest": 3,
        "reward": 2,
        "bounty": 4,
        "grant": 2,
        "retrodrop": 5,
        "campaign": 2,
        "earn": 1
    }
    for word, val in keywords.items():
        if word in text:
            score += val
            tags.append(word)
            reasons.append(f"{word}+{val}")
    return score, tags, ";".join(reasons)

def save_item(item):
    # Save to DB
    cur.execute("""
    INSERT OR IGNORE INTO opportunities
    (id, source, title, url, published, summary, score, reason, tags, fetched_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item["id"], item["source"], item["title"], item["url"],
        item["published"], item["summary"], item["score"], item["reason"],
        ",".join(item["tags"]), item["fetched_at"]
    ))
    conn.commit()

    # Save to CSV
    write_header = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["id","source","title","url","published","summary","score","reason","tags","fetched_at"])
        writer.writerow([
            item["id"], item["source"], item["title"], item["url"],
            item["published"], item["summary"], item["score"], item["reason"],
            ",".join(item["tags"]), item["fetched_at"]
        ])

def notify(item):
    text = f"💡 New Opportunity: {item['title']}\n{item['url']}\nScore: {item['score']} | Tags: {','.join(item['tags'])}"
    if NOTIFY["telegram"]["enabled"] and NOTIFY["telegram"]["bot_token"] and NOTIFY["telegram"]["chat_id"]:
        requests.post(
            f"https://api.telegram.org/bot{NOTIFY['telegram']['bot_token']}/sendMessage",
            data={"chat_id": NOTIFY["telegram"]["chat_id"], "text": text}
        )
    if NOTIFY["discord"]["enabled"] and NOTIFY["discord"]["webhook_url"]:
        requests.post(NOTIFY["discord"]["webhook_url"], json={"content": text})

def fetch_feed(url):
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            uid = hash_id(url, entry.get("link", ""))
            cur.execute("SELECT id FROM opportunities WHERE id=?", (uid,))
            if cur.fetchone():
                continue
            item = {
                "id": uid,
                "source": url,
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", "").strip(),
                "score": 0,
                "reason": "",
                "tags": [],
                "fetched_at": datetime.utcnow().isoformat()
            }
            score, tags, reason = score_item(item["title"], item["summary"])
            item["score"], item["tags"], item["reason"] = score, tags, reason
            save_item(item)
            if score >= 3:
                notify(item)
            print(f"[+] {item['title']} -> Score {score} {tags}")
    except Exception as e:
        print(f"[!] Error {url}: {e}")

def run_once():
    print(f"\n=== OMEGA-PRIME {datetime.utcnow().isoformat()} ===")
    for url in FEEDS:
        fetch_feed(url)

def git_commit_push():
    """Auto-commit updates when running inside GitHub Actions"""
    try:
        subprocess.run(["git", "config", "user.name", "Omega-Prime Bot"])
        subprocess.run(["git", "config", "user.email", "bot@example.com"])
        subprocess.run(["git", "add", CSV_PATH, DB_PATH], check=False)
        subprocess.run(["git", "commit", "-m", "🤖 Update opportunities [skip ci]"], check=False)
        subprocess.run(["git", "push"], check=False)
    except Exception as e:
        print(f"[!] Git push failed: {e}")

if __name__ == "__main__":
    run_once()
    if os.getenv("GITHUB_ACTIONS") == "true":
        git_commit_push()
