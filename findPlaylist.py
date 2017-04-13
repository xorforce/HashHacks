import pygn
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import os
import urllib, base64, json, requests
import datetime
import math

def findPlaylist(score):
    emotion={"-0.8": "65329","-0.7": "42951","-0.6": "42953","-0.5": "42953","-0.4": "65330","-0.3": "65327","-0.2": "65325","-0.1": "42969","0.0": "42954","0.1": "42947","0.2": "65326","0.3": "65332","0.4": "42961","0.5": "42946","0.6": "65333","0.7": "65323","0.8": "42960"}
    emotionSelected = emotion[score]
    now=datetime.datetime.now()
    sp_client_ID='7547da5d51034f04b323576a95adbb77'
    sp_client_secret='f80b03245a5a4d1689f74046d6181176'
    host='http://127.0.0.1:5000/'
    os.environ["SPOTIPY_CLIENT_ID"]=sp_client_ID
    os.environ["SPOTIPY_CLIENT_SECRET"]=sp_client_secret
    os.environ["SPOTIPY_REDIRECT_URI"]=host
    username="manjogsingh+sp4"
    scope = 'playlist-modify-public'
    util.prompt_for_user_token(username=username,scope=scope,client_id = sp_client_ID,client_secret = sp_client_secret,redirect_uri = host)
    token = util.prompt_for_user_token(username, scope)
    client_ID='170259781-06F33892AE9B17F95EE25A24C4593C70'
    user_ID=pygn.register(client_ID)
    track_titles=[]
    artist_list=[]
    result=pygn.createRadio(client_ID,user_ID,mood=emotionSelected,popularity='1000',similarity='1000',count='10') 
    jsonData=json.dumps(result,sort_keys=True,indent=4)
    jsonObject=json.loads(jsonData)

    i=0
    while(i<9):
        temp=jsonObject[i]["track_title"]
        temp1=jsonObject[i]["track_artist_name"]
        track_titles.append(temp)
        artist_list.append(temp1)
        i=i+1

    if token:
        sp = spotipy.Spotify(auth=token)
        sp_playlist_name="New Playlist "+now.strftime("%Y-%m-%d %H:%M")
        sp.user_playlist_create(user=username,name=sp_playlist_name,public=True)
        playlist_raw=sp.current_user_playlists(limit=10,offset=0)
        playlist_jsonData=json.dumps(playlist_raw)
        playlist_jsonObject=json.loads(playlist_jsonData)
        tracks=[]
        for i in range(0,9):
            q="track:"+track_titles[i]
            sp_track=sp.search(q=q,limit=10,offset=0,type='track')
            sp_jsonData=json.dumps(sp_track,sort_keys=True,indent=4)
            sp_jsonObject=json.loads(sp_jsonData)
            #print(playlist_jsonData)
            track_ID=sp_jsonObject["tracks"]["items"][0]["id"]
            print(track_ID)
            tracks.append(track_ID)
        x=0
        for x in range(playlist_jsonObject):
            if playlist_jsonObject["items"][x]["name"]==sp_playlist_name:
                playlist_ID=playlist_jsonObject["items"][x]["id"]
                sp.user_playlist_add_tracks(user=username,playlist_id=playlist_ID,tracks=tracks)
            else:
                pass
    else:
        print('TOKEN NOT AVAILABLE')
    
findPlaylist(str(-0.3))