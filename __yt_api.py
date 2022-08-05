import os
from time import sleep
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import asyncio

# use None instead of empty string to avoid error
# choose either username or channelId (leave one of them as None)
user_target_username = "CHANGE_ME"
user_target_channelId = None
# comments will be made as long as the videoId is not contained here
# after comments are requested, the videoId will be added to this list and no longer processed
user_blacklist_videoIds = [
    "CHANGE_ME",
]
# these comments will get posted within the respective timeframe
# each post costs large quota!!!
user_comments = [
    "CHANGE_ME",
    "CHANGE_ME"
]
# maximum number of comment attempts per video
# each post costs large quota!!!
user_max_burst_attempts = 1




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
            # creds = flow.run_local_server(port)
            creds = flow.run_console()
        # Save the credentials for the next run
        with open(client_tokens_file, 'w') as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

# Quota cost: 1
def YouTubeAPI_GET_uploadsPlaylistID(youtube, username=None, channelId=None, prefix=""):
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
            print(prefix + "Error (uploadsPlaylistID): No uploads playlist ID found.")
            pass
    except:
        print(prefix + "Error (uploadsPlaylistID): Invalid request.")
    print(prefix + "GET-1 (uploadsPlaylistID):" + str(uploadsPlaylistID))
    return uploadsPlaylistID

# Quota cost: 1
def YouTubeAPI_GET_playlistLatestVideo(youtube, playlistId, prefix=""):
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
            print(prefix + "Error (playlistLatestVideo): videoId not found.")
            pass
        # try:
        #     videoPublishedAt = res.get("items")[0].get("contentDetails").get("videoPublishedAt")
        # except:
        #     print(prefix + "Error (playlistLatestVideo): videoPublishedAt not found.")
        #     pass
    except:
        print(prefix + "Error (playlistLatestVideo): Invalid request.")
    # out = (videoId, videoPublishedAt)
    # print("GET (playlistLatestVideo):" + str(out))
    # return out
    print(prefix + "GET-1 (playlistLatestVideo):" + str(videoId))
    return videoId

# Quota cost: 50
def YouTubeAPI_PUT_videoComment(youtube, videoId, comment, prefix=""):
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
            print(prefix + "Error (videoComment): isPublic not found.")
            pass
    except:
        print(prefix + "Error (videoComment): Invalid request.")
    print(prefix + "PUT-50 (videoComment):" + str(isPublic))
    return isPublic

# Quota cost: 50 * (1 up to user_max_burst_attempts)
def YouTubeAPI_PUT_videoComment_BURST(youtube, videoId, comment, max_burst_attempts, prefix=""):
    burst = max_burst_attempts
    yt_cpub = None # isPublic property in response has to exist otherwise the comment is not posted. 
    while (burst and yt_cpub is None):
        # Warning! If YouTubeAPI_PUT_videoComment is outdated, this could waste your whole quota. Set burst variable with caution!
        yt_cpub = YouTubeAPI_PUT_videoComment(youtube, videoId=videoId, comment=comment, prefix=prefix)
        sleep(70 / 1000) # todo quickfix !!!!
        burst -= 1
    if yt_cpub is None:
        print(prefix + "Error (videoComment_BURST): user_max_burst_attempts exhausted. Giving up.")
    return

# Quota cost: 1
def YouTubeAPI_GET_commentPage(youtube, videoId, page_token=None):
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=videoId, # mrbeast 100 mil sub special
        pageToken=page_token
    )
    res = request.execute()
    nextPageToken = None
    try:
        nextPageToken = res.get("nextPageToken")
    except:
        nextPageToken = None
    return (res, nextPageToken)




class YTCommenter:
    def initialize(request_uid = True):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        # Get the API service instance.
        yt = YouTubeAPI_init(client_secrets_file="client_secret.json", client_tokens_file="client_tokens.json", scopes=["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/youtube.force-ssl"])
            
        # Get the uploads playlist ID.
        yt_uid = None
        if (request_uid):
            yt_uid = YouTubeAPI_GET_uploadsPlaylistID(yt, username=user_target_username, channelId=user_target_channelId)
        return (yt, yt_uid)

    def get_lastest_upload_and_comment_burst(run_id: str, yt, yt_uid, delay_ms):
        # Delay ideal right here, because once the video exists we need to act immediately.
        prefix = "  >> " + str(run_id) + ": "
        sleep(float(delay_ms) / 1000)
        print(prefix + "Start")

        # Get the list of videos in the uploads playlist.
        yt_vid = YouTubeAPI_GET_playlistLatestVideo(yt, playlistId=yt_uid, prefix=prefix)

        # Check if the video is in the blacklist.
        if yt_vid in user_blacklist_videoIds:
            print(prefix + "Video is in blacklist, skipping.")
            return False
        elif yt_vid != None:
            # Non-blacklisted video! Post the comments.
            for comment in user_comments:
                print(prefix + "Async publishing: " + comment)
                YouTubeAPI_PUT_videoComment_BURST(yt, videoId=yt_vid, comment=comment, max_burst_attempts=user_max_burst_attempts, prefix=prefix)
            # Blacklist the video!
            user_blacklist_videoIds.append(yt_vid)
            print(prefix + "Blacklisting processed video: " + yt_vid)
            return True

    def get_comments(yt, user_videoid, page_token=None):
        res, nextPageToken = YouTubeAPI_GET_commentPage(yt, videoId=user_videoid, page_token=page_token)
        return (res, nextPageToken)
        

    def report():
        # Finally, report the progress.
        print("Done.")
        print("Blacklisted videos: " + str(len(user_blacklist_videoIds)))
        print(" - " + str(user_blacklist_videoIds))
        