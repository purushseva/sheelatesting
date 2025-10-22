from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os, requests, asyncio, re
from config import *

bot = Client("FileStoreBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def shorten_url(url):
    r = requests.get(f"https://api.apilayer.com/short_url?apikey={URL_SHORTENER_KEY}&url={url}")
    if r.status_code == 200:
        return r.json().get("result_url", url)
    return url

@bot.on_message(filters.document | filters.video | filters.photo)
async def save_file(client, message):
    file_path = await message.download()
    sent = await message.reply_document(
        file_path,
        caption="Protected File (Forwarding Disabled)",
        protect_content=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Clone Bot", url="https://render.com/deploy?repo=https://github.com/yourusername/filestore-bot")],
            [InlineKeyboardButton("Verify Link", url=shorten_url("https://yourbot.verification"))]
        ])
    )
    await asyncio.sleep(AUTO_DELETE_TIME)
    await sent.delete()
    await message.delete()

@bot.on_message(filters.text & filters.keyboard)
async def clone_from_link(client, message):
    link_pattern = r"(https?://t\.me/[a-zA-Z0-9_]+/[0-9]+)"
    links = re.findall(link_pattern, message.text)
    if not links:
        return

    for link in links:
        try:
            parts = link.split("/")
            chat_username = parts[3]
            message_id = int(parts[4])
            original = await client.get_messages(chat_username, message_id)
            downloaded = await original.download()
            new_file = await message.reply_document(
                downloaded,
                caption="Re-uploaded via FileStoreBot | Forwarding Disabled",
                protect_content=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Clone Bot", url="https://render.com/deploy?repo=https://github.com/yourusername/filestore-bot")],
                    [InlineKeyboardButton("Verify Link", url=shorten_url("https://yourbot.verification"))]
                ])
            )
            await original.delete()
        except Exception as e:
            await message.reply(f"Could not clone file: {e}")

print("Bot is running...")
bot.run()

