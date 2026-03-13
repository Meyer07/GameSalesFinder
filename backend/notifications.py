import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

ROADRUNNER_EMAIL    = os.getenv("ROADRUNNER_EMAIL")
ROADRUNNER_PASSWORD = os.getenv("ROADRUNNER_PASSWORD")
PUSHOVER_API_TOKEN  = os.getenv("PUSHOVER_API_TOKEN")

PLATFORM_COLORS = {
    "ps":     "#0070cc",
    "steam":  "#1b2838",
    "switch": "#e4000f",
    "xbox":   "#107c10",
}

PLATFORM_LABELS = {
    "ps":     "PlayStation",
    "steam":  "Steam",
    "switch": "Nintendo Switch",
    "xbox":   "Xbox",
}


def sendEmail(to_email: str, deals: list[dict]):
    """Send a deal notification email grouped by platform."""
    if not deals or not to_email:
        return

    today   = datetime.now().strftime("%b %d, %Y")
    subject = f"🎮 Game Deals — {len(deals)} wishlist game(s) on sale! ({today})"

    # ── Plain Text ─────────────────────────────────────────
    lines = [f"Game Deals — {today}", "=" * 50]
    for d in deals:
        label = d.get("platform_label", "")
        lines.append(
            f"\n🎮 {d['name']} [{label}]\n"
            f"   {d['regular_price']} → {d['sale_price']} ({d['discount']}% OFF)\n"
            f"   {d['url']}"
        )
    plain_text = "\n".join(lines)

    # ── HTML grouped by platform ───────────────────────────
    # Group deals by platform
    from collections import defaultdict
    by_platform = defaultdict(list)
    for d in deals:
        by_platform[d.get("platform", "ps")].append(d)

    sections = ""
    for platform_key, platform_deals in by_platform.items():
        color = PLATFORM_COLORS.get(platform_key, "#0070cc")
        label = PLATFORM_LABELS.get(platform_key, platform_key)

        rows = ""
        for d in platform_deals:
            rows += f"""
            <tr>
              <td style="padding:8px; border-bottom:1px solid #1a1a2e;">
                <a href="{d['url']}" style="color:{color}; font-weight:bold; text-decoration:none;">{d['name']}</a>
              </td>
              <td style="padding:8px; border-bottom:1px solid #1a1a2e; text-align:center;">
                <span style="text-decoration:line-through; color:#888;">{d['regular_price']}</span>
              </td>
              <td style="padding:8px; border-bottom:1px solid #1a1a2e; text-align:center; color:#00c853; font-weight:bold;">
                {d['sale_price']}
              </td>
              <td style="padding:8px; border-bottom:1px solid #1a1a2e; text-align:center; color:#ff6b6b; font-weight:bold;">
                {d['discount']}% OFF
              </td>
            </tr>"""

        sections += f"""
        <h2 style="color:{color}; margin-top:2rem;">{label}</h2>
        <table width="100%" cellspacing="0" style="border-collapse:collapse; background:#16213e; border-radius:8px; overflow:hidden; margin-bottom:1.5rem;">
          <thead>
            <tr style="background:{color}; color:#fff;">
              <th style="padding:10px; text-align:left;">Game</th>
              <th style="padding:10px;">Original</th>
              <th style="padding:10px;">Sale Price</th>
              <th style="padding:10px;">Discount</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>"""

    html = f"""
    <html><body style="background:#1a1a2e; color:#eee; font-family:Arial,sans-serif; padding:20px;">
      <div style="max-width:700px; margin:auto;">
        <h1 style="color:#fff;">🎮 Your Wishlist is on Sale!</h1>
        <p style="color:#aaa;">{today}</p>
        {sections}
        <p style="color:#555; font-size:12px; margin-top:20px;">Powered by DekuDeals</p>
      </div>
    </html></body>"""

    try:
        recipients = to_email if isinstance(to_email, list) else [to_email]
        with smtplib.SMTP("mail.twc.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(ROADRUNNER_EMAIL, ROADRUNNER_PASSWORD)
            for recipient in recipients:
                msg            = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"]    = ROADRUNNER_EMAIL
                msg["To"]      = recipient
                msg.attach(MIMEText(plain_text, "plain"))
                msg.attach(MIMEText(html, "html"))
                server.sendmail(ROADRUNNER_EMAIL, recipient, msg.as_string())
                print(f"[✓] Email sent to {recipient}")
    except Exception as e:
        print(f"[ERROR] Email failed: {e}")


def sendPushover(pushover_key: str, deals: list[dict]):
    """Send a Pushover push notification with the top deals."""
    if not deals or not pushover_key:
        return

    top   = deals[:3]
    lines = ["🎮 Wishlist Deals Today:"]
    for d in top:
        label = d.get("platform_label", "")
        lines.append(f"• {d['name']} [{label}] — {d['sale_price']} ({d['discount']}% OFF)")
    if len(deals) > 3:
        lines.append(f"...and {len(deals) - 3} more. Check your email!")

    try:
        resp = requests.post("https://api.pushover.net/1/messages.json", data={
            "token":     PUSHOVER_API_TOKEN,
            "user":      pushover_key,
            "title":     "Game Deals Alert",
            "message":   "\n".join(lines),
            "url":       deals[0].get("url", ""),
            "url_title": "View on DekuDeals",
            "sound":     "cashregister"
        })
        resp.raise_for_status()
        print(f"[✓] Pushover notification sent.")
    except Exception as e:
        print(f"[ERROR] Pushover failed: {e}")