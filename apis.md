# quickstart - client secrets file and pip packages tutorial

https://developers.google.com/youtube/v3/quickstart/python?hl=en

it do be rly good plz haev a look! thank





# Get Channel => Uploads playlist

https://developers.google.com/youtube/v3/docs/channels/list?apix=true&apix_params=%7B%22part%22%3A%5B%22contentDetails%22%5D%2C%22forUsername%22%3A%22MrBeast6000%22%7D

by username => forUsername

by channelid => id

```python
# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.channels().list(
        part="contentDetails",
        forUsername="MrBeast6000"
    )
    response = request.execute()

    print(response)

if __name__ == "__main__":
    main()
```

json response, notice `items[0].contentDetails.relatedPlaylists.uploads`:

```json
{
  "kind": "youtube#channelListResponse",
  "etag": "mky5yfatRnp-E8N9-BwXGY8W8Dk",
  "pageInfo": {
    "totalResults": 1,
    "resultsPerPage": 5
  },
  "items": [
    {
      "kind": "youtube#channel",
      "etag": "-f8h6RTCebSZttPcDz3dTkMV5yo",
      "id": "UCX6OQ3DkcsbYNE6H8uQQuVA",
      "contentDetails": {
        "relatedPlaylists": {
          "likes": "",
          "uploads": "UUX6OQ3DkcsbYNE6H8uQQuVA"
        }
      }
    }
  ]
}

```

# Get playlist items => Get new upload

https://developers.google.com/youtube/v3/docs/playlistItems/list?apix_params=%7B%22part%22%3A%5B%22contentDetails%22%5D%2C%22playlistId%22%3A%22UUX6OQ3DkcsbYNE6H8uQQuVA%22%7D&apix=true

from previous response: id = `UUX6OQ3DkcsbYNE6H8uQQuVA`

```python
# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlistItems.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId="UUX6OQ3DkcsbYNE6H8uQQuVA"
    )
    response = request.execute()

    print(response)

if __name__ == "__main__":
    main()
```

json response, notice `items[0].contentDetails.videoPublishedAt` and `videoId`

**get new upload:** take the `videoId` if it is above `videoPublishedAt` threshold (can be set as previous + 1 second) else keep refreshing

**todo: check timezone and api delay around scheduled video's publish time using python request burst**

```json
{
  "kind": "youtube#playlistItemListResponse",
  "etag": "JEATttyhXn0PEVRu-1jUyIDHJYM",
  "nextPageToken": "EAAaBlBUOkNBVQ",
  "items": [
    {
      "kind": "youtube#playlistItem",
      "etag": "S7OEkNmopvH0HjCOpbYQEMGOzzc",
      "id": "VVVYNk9RM0RrY3NiWU5FNkg4dVFRdVZBLmRaa2xaVmFVNEFJ",
      "contentDetails": {
        "videoId": "dZklZVaU4AI",
        "videoPublishedAt": "2022-07-31T21:00:01Z"
      }
    },
    {
      "kind": "youtube#playlistItem",
      "etag": "7aUdVO6UvuVn0m37kGzslUcJ1B8",
      "id": "VVVYNk9RM0RrY3NiWU5FNkg4dVFRdVZBLnRWV1dwMVBxRHVz",
      "contentDetails": {
        "videoId": "tVWWp1PqDus",
        "videoPublishedAt": "2022-07-23T20:00:09Z"
      }
    },
    {
      "kind": "youtube#playlistItem",
      "etag": "trc3kxqkIzrw7bpAGxyvwfpQv9M",
      "id": "VVVYNk9RM0RrY3NiWU5FNkg4dVFRdVZBLnZhSWd5Um9Va1FJ",
      "contentDetails": {
        "videoId": "vaIgyRoUkQI",
        "videoPublishedAt": "2022-07-02T20:00:02Z"
      }
    },
    {
      "kind": "youtube#playlistItem",
      "etag": "SdvuWE0YtcAz-mS29iedoFEKrW8",
      "id": "VVVYNk9RM0RrY3NiWU5FNkg4dVFRdVZBLkh3eWJwMzhHblp3",
      "contentDetails": {
        "videoId": "Hwybp38GnZw",
        "videoPublishedAt": "2022-06-04T20:00:02Z"
      }
    },
    {
      "kind": "youtube#playlistItem",
      "etag": "L6EI7mknnbwT6jPAIohhwdgTdjI",
      "id": "VVVYNk9RM0RrY3NiWU5FNkg4dVFRdVZBLmhEMVl0bUtYTmI0",
      "contentDetails": {
        "videoId": "hD1YtmKXNb4",
        "videoPublishedAt": "2022-04-09T20:00:00Z"
      }
    }
  ],
  "pageInfo": {
    "totalResults": 725,
    "resultsPerPage": 5
  }
}

```

# Create a top level comment on the newly uploaded video

https://developers.google.com/youtube/v3/docs/commentThreads/insert?apix=true&apix_params=%7B%22part%22%3A%5B%22snippet%22%5D%2C%22resource%22%3A%7B%22snippet%22%3A%7B%22videoId%22%3A%22dZklZVaU4AI%22%2C%22topLevelComment%22%3A%7B%22snippet%22%3A%7B%22textOriginal%22%3A%22I%20will%20try%20my%20best!%22%7D%7D%7D%7D%7D

## **NEEDS OAUTH**

```python
# -*- coding: utf-8 -*-

# Sample Python code for youtube.commentThreads.insert
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.commentThreads().insert(
        part="snippet",
        body={
          "snippet": {
            "videoId": "dZklZVaU4AI",
            "topLevelComment": {
              "snippet": {
                "textOriginal": "I will try my best!"
              }
            }
          }
        }
    )
    response = request.execute()

    print(response)

if __name__ == "__main__":
    main()
```

success 200 ok response:

```json
{
  "kind": "youtube#commentThread",
  "etag": "WYFKPOD-qlAoGX5ljkTFPHru1hw",
  "id": "UgxbdMD5VUmm7BvgD3p4AaABAg",
  "snippet": {
    "channelId": "UCX6OQ3DkcsbYNE6H8uQQuVA",
    "videoId": "dZklZVaU4AI",
    "topLevelComment": {
      "kind": "youtube#comment",
      "etag": "jB3PU7q6EKOqqHMgrBj3S-3OXO0",
      "id": "UgxbdMD5VUmm7BvgD3p4AaABAg",
      "snippet": {
        "channelId": "UCX6OQ3DkcsbYNE6H8uQQuVA",
        "videoId": "dZklZVaU4AI",
        "textDisplay": "I will try my best!",
        "textOriginal": "I will try my best!",
        "authorDisplayName": "mindcapped",
        "authorProfileImageUrl": "https://yt3.ggpht.com/ytc/AMLnZu93NnZ26lE0x7rzik6BBiPRhKHGosJciAzy5o1aDQ=s48-c-k-c0x00ffffff-no-rj",
        "authorChannelUrl": "http://www.youtube.com/channel/UCIltfMyMAiZskLyGIkvXO9w",
        "authorChannelId": {
          "value": "UCIltfMyMAiZskLyGIkvXO9w"
        },
        "canRate": true,
        "viewerRating": "none",
        "likeCount": 0,
        "publishedAt": "2022-08-03T23:08:51Z",
        "updatedAt": "2022-08-03T23:08:51Z"
      }
    },
    "canReply": true,
    "totalReplyCount": 0,
    "isPublic": true
  }
}

```

