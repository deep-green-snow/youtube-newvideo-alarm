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

@app.route('/')
def home():
    return jsonify({"message": "RUNNING", "status" : HTTPStatus.OK})

@app.route('/latest_video_id')
def latest_video_id():
    return jsonify(LATEST_VIDEO_ID)

@app.route("/health")
def health():
    return jsonify({"message": "OK", "status": HTTPStatus.OK})

@app.route('/get_new_videos', methods=['GET'])
def get_new_videos():
    latest_viedos = get_latest_video()
    return jsonify({"data" : latest_viedos, "status": HTTPStatus.OK})

if __name__ == "__main__":
    # Flask 서버 실행
    app.run(host="0.0.0.0", port=5000)
