import requests
import time
from http import HTTPStatus
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

app = Flask(__name__)

def get_latest_videos():
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
            
            latest_videos.append({
                        'channel_id' : channel_id,
                        'channel_name' : channel_name,
                        'video_id' : video_id,
                        'video_title' : video_title,
                        'publishTime' : publishTime,
                        "url": f"https://www.youtube.com/watch?v={video_id}"
                    })
                
    return latest_videos

@app.route('/')
def home():
    return jsonify({"message": "RUNNING", "status" : HTTPStatus.OK})

@app.route("/health")
def health():
    return jsonify({"message": "OK", "status": HTTPStatus.OK})

@app.route('/get_new_videos', methods=['GET'])
def get_new_videos():
    latest_videos = get_latest_videos()
    return jsonify({"data" : latest_videos,"status": HTTPStatus.OK})

if __name__ == "__main__":
    # Flask 서버 실행
    app.run(host="0.0.0.0", port=5000)
