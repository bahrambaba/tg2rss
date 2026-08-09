#!/usr/bin/env python3
"""
Generate RSS feeds from Telegram channels.
Run this script to update all feeds.
"""

import requests
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import json


# =============================================================================
# Configuration - Add your channels here
# =============================================================================

CHANNELS = [
    "koohnameh",
    "bbcpersian",
    "VOAbrfarsi",
    "BBCAfghan",
    "euronews_africa",
    "navad",
    "tjpress",
    "irdiplomacy",
]


# =============================================================================
# Functions
# =============================================================================

def fetch_channel_messages(channel_username):
    """Fetch messages from t.me/s/ web preview"""
    url = f"https://t.me/s/{channel_username}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Error fetching {channel_username}: {e}")
        return None


def parse_messages(html, channel_username):
    """Parse messages from HTML"""
    messages = []
    
    msg_blocks = re.findall(r'data-post="([^"]*)"', html)
    
    for post_id in msg_blocks:
        pattern = rf'data-post="{re.escape(post_id)}".*?<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>'
        match = re.search(pattern, html, re.DOTALL)
        
        if match:
            text = match.group(1)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            date_match = re.search(
                r'datetime="([^"]*)"',
                html[html.find(f'data-post="{post_id}"'):html.find(f'data-post="{post_id}"') + 2000]
            )
            date_str = date_match.group(1) if date_match else datetime.now().isoformat()
            
            img_match = re.search(
                r'<img class="tgme_widget_message_photo[^"]*"[^>]*src="([^"]*)"',
                html[html.find(f'data-post="{post_id}"'):html.find(f'data-post="{post_id}"') + 3000]
            )
            image_url = img_match.group(1) if img_match else None
            
            messages.append({
                "id": post_id,
                "text": text[:2000],
                "date": date_str,
                "link": f"https://t.me/{channel_username}/{post_id.split('/')[-1]}",
                "image": image_url
            })
    
    return messages


def generate_rss(messages, channel_username):
    """Generate RSS XML from messages"""
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    rss.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")
    rss.set("xmlns:media", "http://search.yahoo.com/mrss/")
    
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = f"Telegram: @{channel_username}"
    ET.SubElement(channel, "link").text = f"https://t.me/{channel_username}"
    ET.SubElement(channel, "description").text = f"RSS feed for Telegram channel @{channel_username}"
    ET.SubElement(channel, "language").text = "fa"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    
    atom_link = ET.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", f"/rss/{channel_username}.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")
    
    for msg in messages:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = msg["text"][:100] + "..." if len(msg["text"]) > 100 else msg["text"]
        ET.SubElement(item, "link").text = msg["link"]
        ET.SubElement(item, "guid").text = msg["link"]
        ET.SubElement(item, "description").text = msg["text"]
        ET.SubElement(item, "pubDate").text = msg["date"]
        ET.SubElement(item, "dc:creator").text = f"@{channel_username}"
        
        if msg.get("image"):
            media = ET.SubElement(item, "{http://search.yahoo.com/mrss/}content")
            media.set("url", msg["image"])
            media.set("medium", "image")
    
    return rss


def main():
    # Create feeds directory
    os.makedirs("feeds", exist_ok=True)
    
    # Also create feeds/rss subdirectory for GitHub Pages
    os.makedirs("feeds/rss", exist_ok=True)
    
    results = []
    
    for channel in CHANNELS:
        print(f"Processing @{channel}...")
        
        html = fetch_channel_messages(channel)
        if not html:
            print(f"  Failed to fetch @{channel}")
            continue
        
        messages = parse_messages(html, channel)
        if not messages:
            print(f"  No messages found for @{channel}")
            continue
        
        rss = generate_rss(messages, channel)
        
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_string = xml_declaration + ET.tostring(rss, encoding="unicode")
        
        filename = f"feeds/rss/{channel}.xml"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_string)
        
        print(f"  Generated: {filename} ({len(messages)} messages)")
        results.append({"channel": channel, "messages": len(messages), "file": filename})
    
    # Generate index page
    generate_index(results)
    
    # Save results as JSON
    with open("feeds/results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDone! Generated {len(results)} feeds")


def generate_index(results):
    """Generate HTML index page"""
    html = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Telegram RSS Feeds</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        .feed { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .feed a { color: #0066cc; text-decoration: none; }
        .feed:hover { background: #e0e0e0; }
    </style>
</head>
<body>
    <h1>Telegram RSS Feeds</h1>
    <p>Generated RSS feeds from Telegram channels</p>
    
    <h2>Available Feeds</h2>
"""
    
    for r in results:
        html += f"""
    <div class="feed">
        <h3>@{r['channel']}</h3>
        <p>{r['messages']} messages</p>
        <a href="rss/{r['channel']}.xml">RSS Feed</a> | 
        <a href="https://t.me/{r['channel']}" target="_blank">Open in Telegram</a>
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    with open("feeds/index.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
