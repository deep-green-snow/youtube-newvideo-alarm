import requests
import time
from flask import Flask, jsonify, request
import threading

# YouTube API 정보
API_KEY = "AIzaSyAoiKv4A8AIOFg3WrAeCdOornFuR2m3fzs"  # 🔹 YouTube API Key 입력
CHANNEL_ID = "UCOB62fKRT7b73X7tRxMuN2g"  # 🔹 감지할 YouTube 채널 ID 입력

# Make.com Webhook URL
WEBHOOK_URL = "https://hook.us2.make.com/n5an8aok5383arxggx02krkuex7mxshs"  # 🔹 Make.com Webhook URL 입력

# Polling 주기 (초 단위)
POLL_INTERVAL = 3600  # 5분마다 실행

# 가장 최근의 영상 ID 저장
latest_video_id = None

app = Flask(__name__)

def get_latest_video():
    """ YouTube API를 사용하여 최신 영상 ID 조회 """
    url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=1"
    response = requests.get(url).json()
    
    if "items" in response:
        video_id = response["items"][0]["id"].get("videoId")
        video_title = response["items"][0]["snippet"].get("title")
        publishTime = response["items"][0]["snippet"].get("publishTime")
        return video_id, video_title, publishTime
    return None

def send_webhook(video_id, video_title, publishTime):
    """ Make.com Webhook에 새로운 영상 정보 전송 """
    payload = {
        "video_id": video_id,
        "video_title" : video_title,
        "publishTime" : publishTime,
        "channel_id": CHANNEL_ID,
        "url": f"https://www.youtube.com/watch?v={video_id}"
    }
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[Webhook Sent] {payload} | Response: {response.status_code}")

def check_new_video():
    """ 새로운 영상이 올라오면 Webhook 전송 """
    global latest_video_id
    video_id, video_title, publishTime = get_latest_video()
    
    if video_id and video_id != latest_video_id:
        latest_video_id = video_id
        print(f"[New Video Detected] {video_id}")
        send_webhook(video_id, video_title, publishTime)

def start_polling():
    """ 주기적으로 YouTube 채널을 감시하는 백그라운드 작업 """
    while True:
        check_new_video()
        time.sleep(POLL_INTERVAL)

@app.route('/')
def home():
    return jsonify({"message": "YouTube Polling Server Running"})

@app.route('/poll', methods=['GET'])
def manual_poll():
    """ 수동으로 Polling 실행 (테스트용) """
    check_new_video()
    return jsonify({"status": "Checked"})

if __name__ == "__main__":
    # 백그라운드에서 Polling 실행
    polling_thread = threading.Thread(target=start_polling, daemon=True)
    polling_thread.start()
    
    # Flask 서버 실행
    app.run(host="0.0.0.0", port=5000)
