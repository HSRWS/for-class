# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time
import json
import random
import threading
import urllib.request
from datetime import datetime, timedelta

# ===== 配置（可修改） =====
BROKER = "broker.emqx.io"
PORT = 1883
ROOM = "lobby"                     # 房间名，与网页一致
USERNAME = "广播机器人"             # 机器人名称
INTERVAL = 2                       # 正常广播间隔（秒）
PAUSE_AFTER_WELCOME = 5            # 欢迎新人后暂停（秒）
ONLINE_TIMEOUT = 60                # 用户超时离线时间（秒）
ADMIN_TOPIC = "navchat/admin"      # 管理指令订阅主题
STATUS_TOPIC = "navchat/status"    # 状态发布主题

# 普通广播消息列表
MESSAGES = [
    "🎉 大家好！我是自动广播机器人",
    "📢 欢迎使用 for-class 聊天室",
    "💡 本消息由 Python 脚本自动发送",
    "🕒 当前时间：{time}",
    "🌐 广域网 MQTT 实时通信",
    "🚀 每 {interval} 秒广播一次",
    "✨ 祝你今天愉快！",
    "🔁 这是自动循环消息 #{count}",
]

# 关键词回复规则（可自由增删）
KEYWORD_REPLIES = {
    "天气": "🌤️ 当前天气：正在查询……",
    "你好": "👋 你好呀！有什么我可以帮你的？",
    "帮助": "🤖 我可以：自动广播、欢迎新人、回复关键词（如“天气”）、定时推送早安、统计在线人数。",
    "时间": "🕐 当前服务器时间：{time}",
}

# ===== MQTT 客户端 =====
client = mqtt.Client()
seen_users = {}          # 用户 -> 最后发言时间戳
pause_until = 0          # 暂停广播的截止时间戳
running = True           # 控制主循环

def on_connect(c, userdata, flags, rc):
    if rc == 0:
        print("✅ 已连接到 MQTT 服务器")
        c.subscribe(f"navchat/{ROOM}")
        c.subscribe(ADMIN_TOPIC)
        send_status("running")
    else:
        print(f"❌ 连接失败，错误码：{rc}")

def on_message(c, userdata, msg):
    global pause_until, running, INTERVAL
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        topic = msg.topic

        # ===== 管理指令 =====
        if topic == ADMIN_TOPIC:
            action = payload.get("action")
            if action == "pause":
                pause_until = time.time() + 999999
                print("⏸️ 已暂停广播")
                send_status("paused")
            elif action == "resume":
                pause_until = 0
                print("▶️ 已恢复广播")
                send_status("running")
            elif action == "stop":
                running = False
                print("🛑 收到停止指令")
                send_status("stopped")
                return
            elif action == "set_interval":
                new_interval = payload.get("value", 2)
                INTERVAL = float(new_interval)
                print(f"⏱️ 广播间隔已更新为 {INTERVAL} 秒")
                send_status("running")
            elif action == "send":
                text = payload.get("text", "")
                if text:
                    send_message(text)
                    print(f"📨 手动发送: {text}")
            elif action == "status":
                send_status("running" if pause_until == 0 else "paused")
            return

        # ===== 聊天室消息 =====
        user = payload.get("user")
        text = payload.get("text", "").strip()
        if user == USERNAME:
            return

        now = time.time()
        seen_users[user] = now
        # 移除超时用户
        offline = [u for u, t in seen_users.items() if now - t > ONLINE_TIMEOUT]
        for u in offline:
            del seen_users[u]
        online_count = len(seen_users)

        # 欢迎新用户
        if user not in seen_users or seen_users[user] == now:
            print(f"👋 新用户出现：{user}")
            welcome = f"👋 欢迎 {user} 来到聊天室！当前在线人数：{online_count}"
            send_message(welcome)
            pause_until = time.time() + PAUSE_AFTER_WELCOME
            print(f"⏸️ 暂停广播 {PAUSE_AFTER_WELCOME} 秒")

        # 关键词回复
        reply = None
        for keyword, response in KEYWORD_REPLIES.items():
            if keyword in text:
                if keyword == "天气":
                    try:
                        url = "https://wttr.in/Beijing?format=%C+%t&lang=zh"
                        with urllib.request.urlopen(url, timeout=5) as resp:
                            weather = resp.read().decode('utf-8').strip()
                        reply = f"🌤️ {weather}"
                    except:
                        reply = "🌤️ 天气信息暂时无法获取，请稍后再试。"
                elif keyword == "时间":
                    reply = response.format(time=time.strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    reply = response
                break
        if reply:
            send_message(reply)
            pause_until = max(pause_until, time.time() + 2)

    except Exception as e:
        print(f"⚠️ 处理消息出错：{e}")

client.on_connect = on_connect
client.on_message = on_message

def send_message(text):
    msg = {
        "user": USERNAME,
        "text": text,
        "time": int(time.time() * 1000),
        "cid": "bot_" + str(random.randint(1000, 9999))
    }
    client.publish(f"navchat/{ROOM}", json.dumps(msg))
    print(f"📤 已发送：{text}")

def send_status(state):
    status_msg = {
        "status": state,
        "users": len(seen_users),
        "interval": INTERVAL,
        "room": ROOM,
        "online": list(seen_users.keys())
    }
    client.publish(STATUS_TOPIC, json.dumps(status_msg))
    print(f"📊 状态发布: {state}")

def send_good_morning():
    send_message("🌅 早上好！新的一天开始了，祝大家心情愉快，工作顺利！☀️")

# ===== 定时任务线程（每天8:00） =====
def schedule_daily():
    while running:
        now = datetime.now()
        target = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        wait_seconds = (target - now).total_seconds()
        if wait_seconds > 0:
            print(f"⏰ 距离下次早安推送还有 {wait_seconds/3600:.1f} 小时")
            time.sleep(wait_seconds)
            if running:
                send_good_morning()

threading.Thread(target=schedule_daily, daemon=True).start()

# ===== 连接 =====
client.connect(BROKER, PORT, 60)
client.loop_start()

# ===== 主循环 =====
count = 0
try:
    while running:
        if time.time() < pause_until:
            time.sleep(0.5)
            continue
        count += 1
        msg = MESSAGES[count % len(MESSAGES)]
        msg = msg.format(
            time=time.strftime("%H:%M:%S"),
            interval=INTERVAL,
            count=count
        )
        send_message(msg)
        time.sleep(INTERVAL)
except KeyboardInterrupt:
    print("\n🛑 用户停止")
finally:
    running = False
    client.loop_stop()
    client.disconnect()
    print("已断开连接")