import discord
from discord.ext import commands
from discord import ui
import json
import os
from dotenv import load_dotenv

# โหลดตัวแปรลับจากไฟล์ .env
load_dotenv()

# โหลด config (เฉพาะค่าที่ไม่ลับ)
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "ยังไม่ได้ตั้งค่า DISCORD_BOT_TOKEN\n"
        "ให้ copy ไฟล์ .env.example เป็น .env แล้วใส่โทเคนจริงของบอทลงไป."
    )


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # ลิงก์ไปยัง Endpoint Login ของ Flask Server เรา
        url = "https://softtown.online/login"

        self.add_item(discord.ui.Button(
            label="ตรวจสอบข้อมูล & รับยศ", 
            style=discord.ButtonStyle.link, 
            url=url,
            emoji="🛡️"
        ))


class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        print(f'Bot connect as {self.user}')
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)


bot = MyBot()


@bot.tree.command(name="setup_auth", description="สร้างปุ่มตรวจสอบบัญชี")
async def setup_auth(interaction: discord.Interaction):
    desc = (
        "คลิกปุ่มด้านล่างเพื่อตรวจสอบความปลอดภัยของบัญชีและรับสิทธิ์เข้าใช้งาน Server\n\n"
        "```diff\n"
        "[+] ตรวจสอบอายุบัญชีอัตโนมัติ\n"
        "[+] ป้องกันสแปมและบอท\n"
        "```"
    )

    embed = discord.Embed(
        title="ระบบตรวจสอบบัญชี (Account Verification)",
        description=desc,
        color=discord.Color.from_rgb(37, 99, 235)  # สีฟ้า
    )
    embed.set_footer(text="SOFT TOWN  v0.1")

    await interaction.response.send_message(embed=embed, view=VerifyView())


bot.run(BOT_TOKEN)
