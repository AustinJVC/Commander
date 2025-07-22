# Commander Bot 🤖

Commander is a feature-rich, event-driven Discord bot built with `discord.py` and designed to enhance your server experience with utility tools, fun interactions, welcome images, server logging, and external API integrations. It’s modular, stat-tracked, and production-ready for communities that want both personality and polish.

---

## 🔧 Features

| Category    | Description                                                                 |
|-------------|-----------------------------------------------------------------------------|
| Fun         | `/joke`, `/meme`, `/cocktail`, `/eightball`, `/bored`, `/qotd`              |
| Utility     | `/weather` command with rich embeds and error handling                      |
| Events      | Welcome messages, message edit/delete logs, voice channel tracking          |
| Visuals     | Dynamic welcome images with user avatars and server branding                |
| Analytics   | SlowStats integration for usage metrics and event tracking                  |
| Modular     | Extensible `cogs/` architecture, clean service separation, async compatible |

---

## 📦 Project Structure

```
.
├── bot.py                # Entrypoint and main event loop
├── cogs/                 # Discord cogs for commands and listeners
│   ├── fun.py
│   ├── utility.py
│   └── events.py
├── services/             # Modular service layer (APIs, embeds, etc.)
│   ├── activity_service.py
│   ├── cocktail_service.py
│   ├── eightball_service.py
│   ├── joke_service.py
│   ├── meme_service.py
│   ├── qotd_service.py
│   ├── weather_service.py
│   ├── welcome_service.py
│   ├── send_event.py
│   └── send_metrics.py
├── res/welcomeMessages/  # Welcome image backgrounds
├── logs/                # Rotating log files
└── .env                 # Environment configuration
```

---

## ⚙️ Setup & Installation

### 1. Install dependencies
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Environment Variables (`.env`)
```
DISCORD_BOT_TOKEN=your_discord_token_here
DISCORD_BOT_STATUS=watching you stay inside!
WEATHER_API_KEY=your_openweathermap_api_key
LOG_CHANNEL_ID=123456789012345678
SLOWSTATS_COMMANDER_API_KEY=your_slowstats_api_key
SLOWSTATS_COMMANDER_PROJECT_ID=your_slowstats_project_id
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### 3. Launch the bot
```bash
python bot.py
```

The bot will log all runtime activity to `logs/discord_bot.log`.

---

## 🧠 Commands

| Command       | Description                                      |
|---------------|--------------------------------------------------|
| `/cocktail`   | Returns a random cocktail recipe                 |
| `/eightball`  | Ask a yes/no question and get a magic response   |
| `/joke`       | Fetches a safe-for-work joke                     |
| `/meme`       | Retrieves a SFW meme from Reddit                 |
| `/qotd`       | Quote of the day from ZenQuotes                  |
| `/bored`      | Activity suggestions from the Bored API          |
| `/weather`    | Current weather data for a city                  |
| `/test_welcome` | Preview your own welcome image                |

---

## 📊 Metrics & Event Tracking

All command usage and key events (e.g., joins/leaves, errors, slash command usage) are sent to [SlowStats](https://theslow.net). This includes:

- `send_metrics.py` → total server/member counts on ready
- `send_event.py` → embedded webhook support for Discord logs and events

---

## 🎨 Welcome Image Generation

Welcome images are rendered using `easy-pil` and support avatar centering, custom background rotation, and dynamic font fallback. Assets are pulled from `res/welcomeMessages/`.

If the image generator fails to load fonts or backgrounds, the feature will automatically disable without crashing the bot.

---

## 📜 Logging

All logs are written to `logs/discord_bot.log` and formatted with timestamps and module info. Server-specific logs (e.g., message edits, deletions, joins, voice updates) are optionally sent to a channel defined via `LOG_CHANNEL_ID`.

---

## 🧩 Extending the Bot

To add a new command:
1. Create a new Cog in `cogs/`
2. Register a slash command with `@app_commands.command`
3. Use `send_event()` optionally to track analytics
4. Add business logic in `services/` if external API usage is needed
5. Import and load your cog via `bot.py`'s dynamic loader

---

## 🛡️ Error Handling Philosophy

- All API responses are validated for content-type and required fields
- Safe fallbacks and inline logs are provided for bad data
- Discord error codes (e.g., 401, 404) return user-friendly messages
- Unhandled exceptions in cogs/services are logged with `exc_info=True`

---

## 📄 License

MIT License – free to use, modify, and deploy. Just don’t be a weirdo and resell it without changing anything.

---

## 💬 Final Notes

- Requires Python 3.10+
- Built for long-term maintainability
- Fully async/await compliant
- Feel free to fork and adapt for your own community

---

**Made with caffeine, memes, and emotional damage.**
