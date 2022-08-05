from datetime import datetime
from _yt_api import YTCommenter

user_video_id = "CHANGE_ME"

yt, yt_uid = YTCommenter.initialize(request_uid=False)
log = open("_yt_comment_finder.log", "a", encoding="utf-8")

nextPageToken = None
i = 0
while (nextPageToken != None or i == 0):
    i += 1
    res, nextPageToken = YTCommenter.get_comments(yt, user_video_id, nextPageToken)

    print(str(datetime.utcnow()) + "UTC | Page no. " + str(i))
    log.write(
        ("[\n" if i == 0 else "") + "{" + 
            "\"log_retrieved\": \"" + str(datetime.utcnow()) + "UTC\"," + 
            "\"log_page\": " + str(i) + "," + 
            "\"log_contents:\": " + str(res) + 
        "}" + ("," if nextPageToken else "\n]") + "\n"
        )

log.close()
print("Done")
