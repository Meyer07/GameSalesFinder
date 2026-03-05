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


def sendEmail(to_email: str, deals: list[dict]):
    """Send a deal notification email to the given address."""
    if not deals or not to_email:
        return

    today   = datetime.now().strftime("%b %d, %Y")
    subject = f"🎮 PS Store Deals — {len(deals)} wishlist game(s) on sale! ({today})"

    # ── Plain Text ─────────────────────────────────────────
    lines = [f"PlayStation Store Deals — {today}", "=" * 50]
    for d in deals:
        lines.append(
            f"\n🎮 {d['name']}\n"
            f"   {d['regular_price']} → {d['sale_price']} ({d['discount']}% OFF)\n"
            f"   {d['url']}"
        )
    plain_text = "\n".join(lines)

    # ── HTML ───────────────────────────────────────────────
    rows = ""
    for d in deals:
        rows += f"""
        <tr>
          <td style="padding:8px; border-bottom:1px solid #333;">
            <a href="{d['url']}" style="color:#0070cc; font-weight:bold; text-decoration:none;">{d['name']}</a>
          </td>
          <td style="padding:8px; border-bottom:1px solid #333; text-align:center;">
            <span style="text-decoration:line-through; color:#888;">{d['regular_price']}</span>
          </td>
          <td style="padding:8px; border-bottom:1px solid #333; text-align:center; color:#00c853; font-weight:bold;">
            {d['sale_price']}
          </td>
          <td style="padding:8px; border-bottom:1px solid #333; text-align:center; color:#ff6b6b; font-weight:bold;">
            {d['discount']}% OFF
          </td>
        </tr>"""

    html = f"""
    <html><body style="background:#1a1a2e; color:#eee; font-family:Arial,sans-serif; padding:20px;">
      <div style="max-width:700px; margin:auto;">
        <h1 style="color:#0070cc;">🎮 Your PS Wishlist is on Sale!</h1>
        <p style="color:#aaa;">{today}</p>
        <table width="100%" cellspacing="0" style="border-collapse:collapse; background:#16213e; border-radius:8px; overflow:hidden;">
          <thead>
            <tr style="background:#0070cc; color:#fff;">
              <th style="padding:10px; text-align:left;">Game</th>
              <th style="padding:10px;">Original</th>
              <th style="padding:10px;">Sale Price</th>
              <th style="padding:10px;">Discount</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
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
        lines.append(f"• {d['name']} — {d['sale_price']} ({d['discount']}% OFF)")
    if len(deals) > 3:
        lines.append(f"...and {len(deals) - 3} more. Check your email!")

    try:
        resp = requests.post("https://api.pushover.net/1/messages.json", data={
            "token":     PUSHOVER_API_TOKEN,
            "user":      pushover_key,
            "title":     "PlayStation Store Deals",
            "message":   "\n".join(lines),
            "url":       deals[0].get("url", ""),
            "url_title": "View on DekuDeals",
            "sound":     "cashregister"
        })
        resp.raise_for_status()
        print(f"[✓] Pushover notification sent.")
    except Exception as e:
        print(f"[ERROR] Pushover failed: {e}")