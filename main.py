import requests
import time
from http import HTTPStatus
from flask import Flask, jsonify, request
import threading
import atexit
import os
import isodate
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# YouTube API 정보
API_KEY = "AIzaSyAoiKv4A8AIOFg3WrAeCdOornFuR2m3fzs"  # YouTube API Key
youtube = build("youtube", "v3", developerKey=API_KEY)
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
        # url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={channel_id}&part=snippet,id&order=date&maxResults=1"
        try:
            # response = requests.get(url).json()
            
            request = youtube.search().list(
                part="snippet,id",
                channelId=channel_id,
                order='date',
                maxResults=3
            )

            response = request.execute()
        except HttpError as e:
            print(f"API(search) Error: {e} -> {channel_name}")        

        if "items" in response:
            
            try:
                video_request  = youtube.videos().list(
                    part="contentDetails",
                    id=",".join([video['id'].get("videoId") for video in response["items"]])
                )

                video_response = video_request.execute()
            except HttpError as e:
                print(f"API(videos) Error: {e} -> {channel_name}")

            latest_idx = 0
            for i, item in enumerate(video_response["items"]):
                duration = isodate.parse_duration(item["contentDetails"]["duration"]).total_seconds()
                
                if 60 < duration:  # not shorts
                    latest_idx = i
                    break

            video_id = response["items"][latest_idx]["id"].get("videoId")
            video_title = response["items"][latest_idx]["snippet"].get("title")
            publishTime = response["items"][latest_idx]["snippet"].get("publishTime")
            
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
    return jsonify({"data" : get_latest_video(), "status": HTTPStatus.OK})

if __name__ == "__main__":
    # Flask 서버 실행
    app.run(host="0.0.0.0", port=5000)
