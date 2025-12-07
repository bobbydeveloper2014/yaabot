import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from flask import Flask
import threading

# ------------------------
# Load .env
# ------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Không tìm thấy DISCORD_TOKEN trong .env")

# ------------------------
# Setup bot
# ------------------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)  # nhắn !settag

# ------------------------
# Settag tự động cho tất cả member với log debug
# ------------------------
@bot.command()
async def settag(ctx):
    applied = 0
    guild = ctx.guild
    print(f"[DEBUG] Bắt đầu settag cho server: {guild.name} ({guild.id})")
    
    for member in guild.members:
        if member.bot:
            print(f"[DEBUG] Bỏ qua bot: {member}")
            continue

        roles = [r for r in member.roles if not r.is_default()]
        if not roles:
            print(f"[DEBUG] Member {member} không có role nào ngoại trừ @everyone")
            continue

        top_role = sorted(roles, key=lambda r: r.position, reverse=True)[0]
        print(f"[DEBUG] Member {member} - Role cao nhất: {top_role.name} (position {top_role.position})")

        current = member.nick or member.name
        if f"| {top_role.name}" in current:
            print(f"[DEBUG] Member {member} đã có tag '{top_role.name}' trong nickname, bỏ qua")
            continue

        new_nick = f"{current} | {top_role.name}"
        try:
            await member.edit(nick=new_nick)
            applied += 1
            print(f"[DEBUG] Đổi nickname cho {member}: {new_nick}")
        except discord.Forbidden:
            print(f"[DEBUG] Không đủ quyền đổi nickname cho {member}")
        except Exception as e:
            print(f"[DEBUG] Lỗi khi đổi nickname cho {member}: {e}")

    await ctx.reply(f"Đã tự động set tag cho {applied} thành viên.", mention_author=False)
    print(f"[DEBUG] Hoàn tất settag, tổng số thành viên đổi nickname: {applied}")

# ------------------------
# Flask app để giữ bot luôn chạy
# ------------------------
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# ------------------------
# Thread để chạy Flask song song với bot
# ------------------------
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# ------------------------
# Run Discord bot
# ------------------------
bot.run(TOKEN)
