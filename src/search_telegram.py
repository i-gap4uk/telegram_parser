import argparse
import asyncio
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

from telethon import TelegramClient, functions
from tqdm.asyncio import tqdm

SEP = "=" * 50

def slugify(value: str) -> str:
    """Convert string to safe filename format."""
    value = value.strip()
    value = re.sub(r"\s+", "_", value, flags=re.UNICODE)
    value = re.sub(r"[^0-9A-Za-zА-Яа-яЁёІіЇїЄєҐґ_+-]", "", value, flags=re.UNICODE)
    if not value:
        value = "unknown"
    return value[:80]

def normalize_text(text: str) -> str:
    """Normalize Unicode text for comparison."""
    return unicodedata.normalize("NFKC", text).casefold()

async def find_forum_topic(client: TelegramClient, entity, branch_query: str) -> Optional[Tuple[int, int, str]]:
    """Return (topic_id, top_message_id, title) for the best matching forum topic.
    
    NOTE: The GetForumTopicsRequest expects the 'channel' keyword, not 'peer'.
    """
    try:
        res = await client(functions.channels.GetForumTopicsRequest(
            channel=entity,
            q=branch_query,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=100
        ))
    except Exception:
        # Returning None is a good way to handle the failure.
        return None

    best = None
    bq_norm = normalize_text(branch_query)
    for t in res.topics or []:
        title = t.title or ""
        title_norm = normalize_text(title)
        if title_norm == bq_norm:
            return (t.id, t.top_message, title)
        if best is None and bq_norm in title_norm:
            best = (t.id, t.top_message, title)
    return best

async def run(channel: str, branch: Optional[str], regex: str):
    api_id = int(os.environ["TELEGRAM_API_ID"])
    api_hash = os.environ["TELEGRAM_API_HASH"]
    session_name = os.environ.get("TELEGRAM_SESSION", "telegram_search")

    client = TelegramClient(f"session/{session_name}", api_id, api_hash)
    await client.start()

    entity = await client.get_entity(channel)
    pattern = re.compile(regex, flags=re.UNICODE)

    out_dir = Path("out")
    out_dir.mkdir(parents=True, exist_ok=True)

    topic_id = None
    top_msg_id = None
    topic_title = None

    if branch:
        topic_info = await find_forum_topic(client, entity, branch)
        if topic_info:
            topic_id, top_msg_id, topic_title = topic_info
            print(f"[√] Branch found: {topic_title}")
        else:
            print(f"[!] Branch '{branch}' not found or chat does not support topics. Searching the entire channel.")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    ch_slug = slugify(channel)
    br_slug = slugify(topic_title or branch or "ALL")
    out_path = out_dir / f"{ch_slug}_{br_slug}_{timestamp}.txt"

    found = 0
    total_checked = 0

    # CORRECTED LOGIC: Use the reply_to parameter with the topic_id to search within the forum topic.
    if topic_id:
        messages = client.iter_messages(entity, reply_to=topic_id, reverse=True)
    else:
        messages = client.iter_messages(entity, reverse=True)

    async for msg in tqdm(messages, desc="Searching messages"):
        total_checked += 1
        text = msg.message or ""
        if not text:
            continue
        if pattern.search(text):
            found += 1
            url = None
            try:
                url = msg.message_link
            except Exception:
                url = None

            with out_path.open("a", encoding="utf-8") as f:
                f.write(SEP + "\n")
                f.write(f"[DATE UTC] {msg.date.astimezone(timezone.utc)}\n")
                f.write(f"[MSG ID] {msg.id}\n")
                if url:
                    f.write(f"[LINK] {url}\n")
                f.write(text.strip() + "\n")
                f.write(SEP + "\n")
                f.write("\n")

    print(f"[√] Total messages checked: {total_checked}")
    print(f"[√] Messages found: {found}")
    print(f"[→] Results saved to: {out_path.resolve()}")

def main():
    parser = argparse.ArgumentParser(
        description="Search messages in a Telegram channel/chat using regex. Supports forum topics (threads)."
    )
    parser.add_argument("--channel", required=True, help="Channel or supergroup name (string, supports spaces/Cyrillic).")
    parser.add_argument("--branch", required=False, help="Forum topic (branch) name. If not specified, searches the entire channel.")
    parser.add_argument("--regex", required=True, help="Regular expression (Python re).")
    args = parser.parse_args()

    try:
        asyncio.run(run(args.channel, args.branch, args.regex))
    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")

if __name__ == "__main__":
    main()
