from flask import Flask, request, redirect, render_template, jsonify
import requests
import json
import datetime
from dateutil.parser import parse  # ถ้าไม่ได้ใช้จะลบออกก็ได้ แต่ไม่จำเป็น
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = "random-secret-key"  # เปลี่ยนเป็นค่าอื่นก็ได้

# โหลดตัวแปรลับจากไฟล์ .env (DISCORD_BOT_TOKEN, DISCORD_CLIENT_SECRET)
load_dotenv()

# Load Config (ค่าที่ไม่ลับ)
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# API Constants
API_ENDPOINT = 'https://discord.com/api/v10'
CLIENT_ID = config['CLIENT_ID']
CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
REDIRECT_URI = config['REDIRECT_URI']
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD_ID = config['GUILD_ID']
ROLE_ID = config['ROLE_ID']
MIN_AGE_DAYS = config.get('MIN_ACCOUNT_AGE_DAYS', 3)

if not CLIENT_SECRET or not BOT_TOKEN:
    raise RuntimeError(
        "Missing DISCORD_CLIENT_SECRET หรือ DISCORD_BOT_TOKEN\n"
        "ให้สร้างไฟล์ .env (copy จาก .env.example) แล้วใส่ค่าจริงลงไป จากนั้นรันใหม่อีกครั้ง."
    )


def get_account_creation_date(user_id: str) -> datetime.datetime:
    """
    แปลง Discord Snowflake เป็นเวลาสร้างบัญชี (UTC)
    (id >> 22) + 1420070400000 = timestamp in ms
    """
    timestamp = ((int(user_id) >> 22) + 1420070400000) / 1000
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)


@app.route('/login')
def login():
    # ส่งผู้ใช้ไปหน้า Login ของ Discord
    discord_login_url = (
        "https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=identify"
    )
    return redirect(discord_login_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: No code provided"

    # 1. แลก Code เป็น Token
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(f'{API_ENDPOINT}/oauth2/token', data=data, headers=headers)

    if r.status_code != 200:
        return f"Error fetching token: {r.text}"

    tokens = r.json()
    access_token = tokens['access_token']

    # 2. ดึงข้อมูล User
    headers_user = {'Authorization': f'Bearer {access_token}'}
    r_user = requests.get(f'{API_ENDPOINT}/users/@me', headers=headers_user)
    user_data = r_user.json()
    user_id = user_data['id']
    username = user_data['username']
    avatar_hash = user_data.get('avatar')
    avatar_url = (
        f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"
        if avatar_hash else None
    )

    # 3. เตรียมข้อมูลแสดงผล (Server & Role Info)
    headers_bot = {'Authorization': f'Bot {BOT_TOKEN}'}

    # Get Server Info
    r_guild = requests.get(f'{API_ENDPOINT}/guilds/{GUILD_ID}', headers=headers_bot)
    server_data = r_guild.json()
    server_name = server_data.get('name', 'Unknown Server')
    server_icon_hash = server_data.get('icon')
    server_icon = (
        f"https://cdn.discordapp.com/icons/{GUILD_ID}/{server_icon_hash}.png"
        if server_icon_hash else None
    )

    # Get Role Info
    r_roles = requests.get(f'{API_ENDPOINT}/guilds/{GUILD_ID}/roles', headers=headers_bot)
    roles = r_roles.json()
    role_name = "Verified Role"
    if isinstance(roles, list):
        for role in roles:
            if role['id'] == str(ROLE_ID):
                role_name = role['name']
                break

    # --- เริ่มการตรวจสอบ (VERIFICATION LOGIC) ---

    # Check 1: อายุบัญชี
    created_at = get_account_creation_date(user_id)
    now = datetime.datetime.now(datetime.timezone.utc)
    age_days = (now - created_at).days

    # Check 2: เป็น Bot หรือไม่?
    is_bot = user_data.get('bot', False)

    if is_bot:
        # บอทห้ามผ่านเลย
        return render_template(
            'result.html',
            status='error',
            message="ไม่อนุญาตให้บอทยืนยันตัวตน",
            server_name=server_name,
            server_icon=server_icon,
            server_id=GUILD_ID,
            user_name=username,
            user_avatar=avatar_url,
            user_id=user_id
        )

    if age_days < MIN_AGE_DAYS:
        # บัญชีใหม่เกินไป
        return render_template(
            'result.html',
            status='error',
            message=f"บัญชีของคุณใหม่เกินไป (อายุ {age_days} วัน) ต้องมีอายุอย่างน้อย {MIN_AGE_DAYS} วันเพื่อความปลอดภัย",
            server_name=server_name,
            server_icon=server_icon,
            server_id=GUILD_ID,
            user_name=username,
            user_avatar=avatar_url,
            user_id=user_id
        )

    # --- ผ่านเกณฑ์: 'ยังไม่ให้ยศ' รอให้ผู้ใช้กดยืนยันในหน้าเว็บก่อน ---
    return render_template(
        'result.html',
        status='success',
        server_name=server_name,
        server_icon=server_icon,
        server_id=GUILD_ID,
        user_name=username,
        user_avatar=avatar_url,
        user_id=user_id,
        role_name=role_name
    )


# 🔥 API สำหรับตอนกดปุ่ม "ฉันไม่ใช่บอท"
@app.post("/api/human_confirm")
def human_confirm():
    """
    ถูกเรียกจาก JS ใน result.html ตอนที่ผู้ใช้กดปุ่ม "ฉันไม่ใช่บอท"
    ถ้าเรียก API นี้สำเร็จ -> ค่อยแอดยศให้
    ถ้าไม่กด/หมดเวลา -> API นี้จะไม่ถูกเรียกเลย -> ไม่มียศให้แน่นอน
    """
    data = request.get_json(force=True) or {}

    user_id = data.get("user_id")
    server_id = data.get("server_id") or GUILD_ID  # ปกติจะเป็น GUILD_ID เดียวกัน

    if not user_id:
        return jsonify({"ok": False, "error": "missing user id"}), 400

    # เรียก Discord API เพื่อแอดยศ
    headers_bot = {"Authorization": f"Bot {BOT_TOKEN}"}
    url_add_role = f"{API_ENDPOINT}/guilds/{server_id}/members/{user_id}/roles/{ROLE_ID}"

    r_add = requests.put(url_add_role, headers=headers_bot)

    if r_add.status_code in (200, 204):
        return jsonify({"ok": True})
    else:
        return jsonify({
            "ok": False,
            "error": f"discord error {r_add.status_code}",
            "detail": r_add.text
        }), 500


if __name__ == '__main__':
    print("🌍 Verification System Online on Port 5000")
    print(f"🔗 Callback URL needed in Discord Dev Portal: {REDIRECT_URI}")
    app.run(host="0.0.0.0", port=5000, debug=False)
