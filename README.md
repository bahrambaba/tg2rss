# Telegram to RSS Feed

Convert any public Telegram channel to a valid RSS feed.

## 🚀 Quick Start

### Local Usage

```bash
# Install dependencies
pip install requests

# Generate feeds
python generate_feeds.py

# Feeds will be in feeds/rss/ directory
```

### GitHub Actions

1. Fork this repository
2. Edit `generate_feeds.py` and add your channels to `CHANNELS` list
3. Enable GitHub Pages in Settings → Pages → Source: GitHub Actions
4. Feeds will be available at: `https://USERNAME.github.io/repo/rss/CHANNEL_NAME.xml`

## 📡 Available Feeds

| Channel | Feed URL |
|---------|----------|
| @koohnameh | `feeds/rss/koohnameh.xml` |
| @bbcpersian | `feeds/rss/bbcpersian.xml` |
| @navad | `feeds/rss/navad.xml` |

## ⚙️ Configuration

Edit `generate_feeds.py` and modify the `CHANNELS` list:

```python
CHANNELS = [
    "koohnameh",
    "bbcpersian",
    "your_channel",
]
```

## 🔧 Features

- ✅ No API credentials needed
- ✅ Works with any public channel
- ✅ Standard RSS 2.0 format
- ✅ Full message content
- ✅ Images included
- ✅ Original publication dates
- ✅ Persian language support
- ✅ Auto-updates via GitHub Actions

## 📝 How It Works

1. Fetches messages from `t.me/s/` web preview
2. Parses HTML to extract message content
3. Generates valid RSS XML
4. Saves to `feeds/rss/` directory

## 🌐 Host as Website

Enable GitHub Pages to host the feeds:

1. Go to repository Settings
2. Click Pages
3. Select Source: GitHub Actions
4. Feeds will be at: `https://USERNAME.github.io/repo/`

## 📄 License

MIT
