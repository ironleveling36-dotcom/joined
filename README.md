# 🤖 Telegram Force-Join Bot

A professional Telegram bot with a **Force-Join verification system**, rich admin panel, and broadcast engine — built with Python + aiogram 3 + SQLite/PostgreSQL, ready to deploy on **Railway** in minutes.

---

## ✨ Features

### 👤 User Features
| Feature | Description |
|---|---|
| Force-Join Gate | Users must join all configured channels before using the bot |
| Instant Verify | One-click re-check; popup if still not joined |
| Clean UI | Inline buttons, HTML-formatted messages |
| Auto-register | Every user is stored on first interaction |

### 🛡 Admin Features
| Feature | Description |
|---|---|
| `/admin` Panel | Full inline admin menu |
| Stats | Live total / verified user counts + channel count |
| Add Channel | Dynamically add force-join channels |
| Remove Channel | Dynamically remove force-join channels |
| List Channels | View all configured channels with IDs |
| Block User | Permanently block a user by ID |
| Broadcast | Send text, photo, video, or document to all verified users |

---

## 🗂 Project Structure

```
telegram-forcejoin-bot/
├── main.py              # Entry point
├── config.py            # All configuration (reads .env)
├── database.py          # Async SQLAlchemy ORM + all DB helpers
├── keyboards.py         # All InlineKeyboardMarkup builders
├── messages.py          # Centralised message texts
├── middlewares.py       # Rate-limit + auto-register middlewares
├── utils.py             # Membership check, admin guard
├── handlers/
│   ├── user.py          # /start, verify, home, about, support
│   └── admin.py         # /admin, broadcast, channels, block
├── requirements.txt
├── Procfile
├── railway.toml
├── .env.example
└── .gitignore
```

---

## 🚀 Quick Start (Local)

```bash
# 1. Clone / download
git clone https://github.com/YOUR_USERNAME/telegram-forcejoin-bot.git
cd telegram-forcejoin-bot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env   # Fill in BOT_TOKEN, ADMIN_IDS, etc.

# 5. Run
python main.py
```

---

## ☁️ Deploy to Railway

### Step 1 – Push to GitHub
```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_USERNAME/telegram-forcejoin-bot.git
git push -u origin main
```

### Step 2 – Create Railway Project
1. Go to [railway.app](https://railway.app) → **New Project**
2. Select **Deploy from GitHub repo**
3. Choose your repo

### Step 3 – Set Environment Variables
In Railway → your service → **Variables**, add:

| Variable | Value |
|---|---|
| `BOT_TOKEN` | Your BotFather token |
| `BOT_USERNAME` | Your bot's username (no @) |
| `ADMIN_IDS` | Your Telegram user ID(s) |
| `BOT_NAME` | Display name for your bot |
| `DATABASE_URL` | Leave blank for SQLite, or add a PostgreSQL URL |

### Step 4 – Deploy
Railway auto-deploys on every push. Check **Logs** to confirm the bot is running.

> **Tip:** Add a Railway PostgreSQL plugin for persistent DB across redeploys.  
> Set `DATABASE_URL` to the plugin's `${{Postgres.DATABASE_URL}}` variable.

---

## ⚙️ Adding Force-Join Channels

1. Make your bot an **admin** of the channel (must have "Read messages" permission)
2. Get the channel's numeric ID (use [@username_to_id_bot](https://t.me/username_to_id_bot))
3. In the bot, send `/admin` → **➕ Add Channel**
4. Follow the format: `CHANNEL_ID | https://t.me/channelname | Channel Display Name`

---

## 🔒 Security Notes

- Only user IDs listed in `ADMIN_IDS` can access the admin panel
- Rate limiting (default 3 seconds) is enforced on all users
- Blocked users are excluded from broadcasts
- Database uses async I/O — safe for high concurrency

---

## 📦 Tech Stack

| Layer | Tech |
|---|---|
| Bot Framework | [aiogram 3](https://docs.aiogram.dev/) |
| Database ORM | [SQLAlchemy 2 async](https://docs.sqlalchemy.org/en/20/) |
| SQLite driver | [aiosqlite](https://github.com/omnilib/aiosqlite) |
| Config | [python-dotenv](https://github.com/theskumar/python-dotenv) |
| Hosting | [Railway](https://railway.app) |

---

## 📝 License

MIT — free for personal and commercial use.
