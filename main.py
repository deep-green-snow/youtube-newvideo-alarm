import requests
import time
from flask import Flask, jsonify, request
import threading
import atexit
import os

# YouTube API 정보
API_KEY = "AIzaSyAoiKv4A8AIOFg3WrAeCdOornFuR2m3fzs"  # YouTube API Key
# YouTube Channel ID 
CHANNELS = {
    "UCOB62fKRT7b73X7tRxMuN2g" : "박종훈의 지식한방",
    "UCpqD9_OJNtF6suPpi6mOQCQ" : "월가아재의 과학적 투자",
    "UCg7O-KGVGFOauZ_8XQJFP0g" : "아세안패스 : 숫자로 보는 기회",
    "UCIUni4ScRp4mqPXsxy62L5w" : "언더스탠딩 : 세상의 모든 지식",
    "UC4noqcTx0lqmKTv3lrrjtBw" : "ASPIM Research",
    "UCznImSIaxZR7fdLCICLdgaQ" : "전인구경제연구소",   
    "UCgF5fyJGpkScPHLmhIrlUHg" : "에릭의 거장연구소",
    "UCxvdCnvGODDyuvnELnLkQWw" : "이효석아카데미",
    "UCD9vzSxZ69pjcnf8hgCQXVQ" : "채부심 - 채상욱의 부동산 심부름센터",
    "UCKTMvIu9a4VGSrpWy-8bUrQ" : "내일은 투자왕 - 김단테"
  }

# Make.com Webhook URL
WEBHOOK_URL = "https://hook.us2.make.com/n5an8aok5383arxggx02krkuex7mxshs"  # Make.com Webhook URL

# Polling Period (sec)
POLL_INTERVAL = 3600  # every 1 hr

# Stop Event
STOP_EVENT = threading.Event()

# Keep the latest video id 
LATEST_VIDEO_ID = {
    "UCOB62fKRT7b73X7tRxMuN2g" : None, 
    "UCpqD9_OJNtF6suPpi6mOQCQ" : None, 
    "UCg7O-KGVGFOauZ_8XQJFP0g" : None, 
    "UCIUni4ScRp4mqPXsxy62L5w" : None, 
    "UC4noqcTx0lqmKTv3lrrjtBw" : None, 
    "UCznImSIaxZR7fdLCICLdgaQ" : None,
    "UCgF5fyJGpkScPHLmhIrlUHg" : None, 
    "UCxvdCnvGODDyuvnELnLkQWw" : None,
    "UCD9vzSxZ69pjcnf8hgCQXVQ" : None, 
    "UCKTMvIu9a4VGSrpWy-8bUrQ" : None, 
  }  

app = Flask(__name__)

def get_latest_video():
    global LATEST_VIDEO_ID
    latest_videos = []    
    for channel_id, channel_name in CHANNELS.items():
        url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={channel_id}&part=snippet,id&order=date&maxResults=1"
        try:
            response = requests.get(url).json()
        except Exception as e:
            print(f'[ERROR] {e} (channel : {channel_name})')
    
        if "items" in response:
            video_id = response["items"][0]["id"].get("videoId")
            video_title = response["items"][0]["snippet"].get("title")
            publishTime = response["items"][0]["snippet"].get("publishTime")
            
            if(LATEST_VIDEO_ID[channel_id] is None or 
               (LATEST_VIDEO_ID[channel_id] is not None and LATEST_VIDEO_ID[channel_id] != video_id)):
                print(f"[New Video Detected] {channel_name}")
                LATEST_VIDEO_ID[channel_id] = video_id # update latest video id
                latest_videos.append({
                        'channel_id' : channel_id,
                        'channel_name' : channel_name,
                        'video_id' : video_id,
                        'video_title' : video_title,
                        'publishTime' : publishTime,
                        "url": f"https://www.youtube.com/watch?v={video_id}"
                    })
                
    return latest_videos

def send_webhook(items):
    """ Make.com Webhook에 새로운 영상 정보 전송 """
    payload = {
        "items" : items
    }
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[Webhook Sent] {payload} | Response: {response.status_code}")

def check_new_video():
    """ Send Webhook when new videos are uploaded  """
    latest_videos = get_latest_video()

    items = []
    for video in latest_videos:
        items.append(video)

    if len(items) > 0:
        print(f'[INFO] {len(items)} new videos are found.')
        send_webhook(items)
    else:
        print('[INFO] No new videos.')

def start_polling():
    """ 주기적으로 YouTube 채널을 감시하는 백그라운드 작업 """
    while not STOP_EVENT.is_set():
        check_new_video()
        time.sleep(POLL_INTERVAL)

@app.route('/')
def home():
    return jsonify({"message": "YouTube Polling Server Running"})

@app.route('/latest_video_id')
def latest_video_id():
    return jsonify(LATEST_VIDEO_ID)

@app.route('/poll', methods=['GET'])
def manual_poll():
    """ 수동으로 Polling 실행 (테스트용) """
    check_new_video()
    return jsonify({"status": "Checked"})

@app.before_first_request
def activate_polling():
    polling_thread = threading.Thread(target=start_polling, daemon=True)
    polling_thread.start()

if __name__ == "__main__":
    # Flask 서버 실행
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=5000, debug=False)
