# Telegram Branch Regex Searcher

A Python + Docker tool to **search messages in Telegram channels or supergroups** using a **regular expression**.  
Supports searching **across the entire channel** or **within a specific forum topic (branch)**.

> Built with [Telethon](https://github.com/LonamiWebs/Telethon) and runs fully inside Docker.

---

## 0) Create a Telegram Application (API ID / API HASH)

Before running this project, you need a Telegram API key:

1. Go to **https://my.telegram.org** → *API development tools*.
2. Log in with your phone number.
3. Create a new app (App title and short name can be anything).
4. Save your **API ID** and **API HASH** — you’ll need them later.

⚠ **Important:** Never commit your API keys. Store them in `.env`.

---

## 1) Project Structure

```
telegram-branch-regex-searcher/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
└── src/
    └── search_telegram.py
```

---

## 2) Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/)
- A Telegram account
- The channel name or username to search in  
  (e.g., `--channel "купила баба порося"`)
- If you want to search in a specific **forum topic (branch)**, you need its title.

---

## 3) Configure Environment Variables

1. Copy `.env.example` to `.env`
2. Edit `.env` and set your Telegram credentials:

```
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=0123456789abcdef0123456789abcdef
TELEGRAM_SESSION=telegram_search
```

- `TELEGRAM_SESSION` is the local session file name stored inside the container.

---

## 4) Build and Run with Docker

### Option A: Using Docker Compose (recommended)

```bash
docker compose up --build
```

The first time you run this, you’ll need to authenticate via Telegram.  
A confirmation code will be sent to your Telegram account.

#### Example: Search the entire channel
```bash
docker compose run --rm app --channel "купила баба порося" --regex "порося|свин(ка|і)"
```

#### Example: Search inside a specific forum topic (branch)
```bash
docker compose run --rm app --channel "My Forum Chat" --branch "Announcements" --regex "(?i)deadline|schedule"
```

### Option B: Using raw Docker

```bash
docker build -t tg-search .
docker run --rm -it --env-file .env tg-search --help
```

---

## 5) Command-Line Arguments

| Argument      | Required | Description |
|--------------|----------|-------------|
| `--channel`  | ✅ Yes   | Name of the channel or supergroup (string, supports Unicode & spaces) |
| `--regex`    | ✅ Yes   | Regular expression for matching messages |
| `--branch`   | ❌ No    | Title of the **forum topic** (branch). If omitted, searches the entire channel |

---

## 6) Output

- All results are saved to a `.txt` file in the `out/` folder.
- File name format:

```
channelName_branchName_timestamp.txt
```

- Example:
```
kupila_baba_porosya_ALL_20250903_183000.txt
```

- Each message is separated by a divider:

```
==================================================
[DATE UTC] 2025-09-03 16:35:42
[MSG ID] 12345
[LINK] https://t.me/channel/12345
Message text here...
==================================================
```

---

## 7) Forum Topics (Branches)

- Branch search works **only in supergroups with topics enabled**.
- If `--branch` is omitted, the script scans **all messages**.
- Branches are matched by **title**.  
  If multiple topics partially match, the **exact match** is preferred.

---

## 8) Troubleshooting

| Problem | Solution |
|--------|----------|
| **Auth required** | The first run will ask for a confirmation code sent via Telegram |
| **Private channels** | Make sure your account is a member of the channel |
| **Branch not found** | Ensure the chat has topics enabled and double-check the title |
| **Regex issues** | Uses Python's `re` module. Add `(?i)` for case-insensitive matches |

---

## 9) License

MIT © 2025  
Feel free to use, modify, and contribute.

---

## Example Full Command

```bash
docker compose run --rm app --channel "Tech News Hub" --branch "AI Updates" --regex "(?i)openai"
```

Output will be stored in `out/tech_news_hub_ai_updates_20250903_183000.txt`.
