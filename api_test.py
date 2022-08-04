# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

from http.server import CGIHTTPRequestHandler
from logging import exception
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from pyparsing import exceptions

# use None instead of empty string to avoid error
# choose either username or channelId (leave one of them as None)
user_target_username = None
user_target_channelId = None
# comments will be made as long as the videoId is not contained here
# after comments are requested, the videoId will be added to this list and no longer processed
user_blacklist_videoIds = [
]
# these comments will get posted within the respective timeframe
user_comments = [
]

# Quota cost: 0
def YouTubeAPI_init(client_secrets_file, client_tokens_file, scopes, port=8080):
    # Get credentials and create an API client
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)

    # Credential storing reference:
    # - https://stackoverflow.com/questions/50865584/python-google-drive-api-oauth2-save-authorization-consent-for-user
    # - https://github.com/googleworkspace/python-samples/blob/master/drive/quickstart/quickstart.py
    creds = None
    if os.path.exists(client_tokens_file):
        creds = Credentials.from_authorized_user_file(client_tokens_file, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            creds = flow.run_local_server(port)
            # creds = flow.run_console()
        # Save the credentials for the next run
        with open(client_tokens_file, 'w') as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

# Quota cost: 1
def YouTubeAPI_GET_uploadsPlaylistID(youtube, username=None, channelId=None):
    request = youtube.channels().list(
        part="contentDetails",
        forUsername=username,
        id=channelId
    )
    uploadsPlaylistID = None
    try:
        res = request.execute()
        # print(res)
        try:
            uploadsPlaylistID = res.get("items")[0].get("contentDetails").get("relatedPlaylists").get("uploads")
        except:
            print("Error (uploadsPlaylistID): No uploads playlist ID found.")
            pass
    except:
        print("Error (uploadsPlaylistID): Invalid request.")
    print("GET (uploadsPlaylistID):" + str(uploadsPlaylistID))
    return uploadsPlaylistID

# Quota cost: 1?
def YouTubeAPI_GET_playlistLatestVideo(youtube, playlistId):
    request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=playlistId
    )
    videoId = None
    # videoPublishedAt = None
    try:
        res = request.execute()
        # print(res)
        try:
            videoId = res.get("items")[0].get("contentDetails").get("videoId")
        except:
            print("Error (playlistLatestVideo): videoId not found.")
            pass
        # try:
        #     videoPublishedAt = res.get("items")[0].get("contentDetails").get("videoPublishedAt")
        # except:
        #     print("Error (playlistLatestVideo): videoPublishedAt not found.")
        #     pass
    except:
        print("Error (playlistLatestVideo): Invalid request.")
    # out = (videoId, videoPublishedAt)
    # print("GET (playlistLatestVideo):" + str(out))
    # return out
    print("GET (playlistLatestVideo):" + videoId)
    return videoId

# Quota cost: BIG?
def YouTubeAPI_PUT_videoComment(youtube, videoId, comment):
    request = youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": videoId,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment
                    }
                }
            }
        }
    )
    isPublic = None
    try:
        res = request.execute()
        # print(res)
        try:
            isPublic = res.get("snippet").get("isPublic")
        except:
            print("Error (videoComment): isPublic not found.")
            pass
    except:
        print("Error (videoComment): Invalid request.")
    print("PUT (videoComment):" + isPublic)
    return isPublic

def main():

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Get the API service instance.
    yt = YouTubeAPI_init(client_secrets_file="client_secret.json", client_tokens_file="client_tokens.json", scopes=["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/youtube.force-ssl"])
    
    # Get the uploads playlist ID.
    yt_uid = YouTubeAPI_GET_uploadsPlaylistID(yt, username=user_target_username, channelId=user_target_channelId)

    # Get the list of videos in the uploads playlist.
    yt_vid = YouTubeAPI_GET_playlistLatestVideo(yt, playlistId=yt_uid)

    # Check if the video is in the blacklist.
    if yt_vid in user_blacklist_videoIds:
        print("Video is in blacklist, skipping.")
    else:
        # todo: New video! Post the comments.
        for comment in user_comments:
            yt_cpub = None # isPublic property in response has to exist otherwise the comment is not posted. 
            while (yt_cpub is None):
                yt_cpub = YouTubeAPI_PUT_videoComment(yt, videoId=yt_vid, comment=comment)
        user_blacklist_videoIds.append(yt_vid)


if __name__ == "__main__":
    main()