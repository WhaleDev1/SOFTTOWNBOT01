# Discord Verification Bot (Safe Version)

โปรเจกต์นี้ปรับให้ปลอดภัยสำหรับเอาขึ้น GitHub โดยเอาโทเคน/ซีเคร็ทออกจากโค้ด
แล้วเก็บไว้ในไฟล์ `.env` แทน

## การเตรียมใช้งาน

1. ติดตั้ง Python ให้เรียบร้อย
2. ดับเบิลคลิก `Requirements.bat` เพื่อติดตั้งไลบรารีที่ต้องใช้
3. คัดลอกไฟล์ `.env.example` เป็น `.env`
4. เปิดไฟล์ `.env` แล้วใส่ค่า:
   - `DISCORD_BOT_TOKEN=` โทเคนบอทจาก Discord Developer Portal
   - `DISCORD_CLIENT_SECRET=` Client Secret จากเมนู OAuth2 ของแอปเดียวกัน
5. ตรวจสอบ `config.json`:
   - `CLIENT_ID` = Application (client) ID
   - `REDIRECT_URI` = `https://softtown.online/callback` (หรือของคุณ)
   - `GUILD_ID` = ID เซิร์ฟเวอร์
   - `ROLE_ID`  = ID ยศที่ต้องการแจก
6. ดับเบิลคลิก `run.bat` เพื่อรันทั้งบอทและเว็บเซิร์ฟเวอร์

## การเอาขึ้น GitHub ให้ปลอดภัย

- ไฟล์ที่มีค่าโทเคนจริงคือ `.env` **เท่านั้น**
- `.env` ถูกเพิ่มไว้ใน `.gitignore` แล้ว (Git จะไม่อัปโหลดไฟล์นี้)
- เวลารันคำสั่ง `git status` ก่อน commit ให้เช็คว่าไม่มี `.env` อยู่ในรายการไฟล์

ถ้าเคยเผลอ commit โทเคน/ซีเคร็ทไปแล้ว แนะนำให้:
- รีเซ็ตโทเคนใหม่จาก Discord Developer Portal
- สร้างโฟลเดอร์โปรเจกต์ใหม่ แล้วคัดลอกไฟล์ชุดนี้ไปใช้แทน
- จากนั้น `git init`, เพิ่ม remote, แล้วค่อย `git push` โปรเจกต์ที่สะอาดขึ้น GitHub
