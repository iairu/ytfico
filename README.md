# YouTube First Comment

> **Y**ou**T**ube **Fi**rst **Co**mment

Thanks to MrBeast for inspiration (100 mil. subscriber special reward for first comment), I got close...

| attempt to make your comment the first comment | a way to identify the true first comment |
| ---------------------------------------------- | ---------------------------------------- |
| ![](https://i.imgur.com/4Hct9cb.png)           | ![](https://i.imgur.com/SCf3nsy.png)     |
| see `_run_comment_on_publish`                  | see `_run_comment_saver`                 |



## Docs

### _run_comment_on_publish

> attempts to make your comment the first comment

repeatedly attempts over time (based on modified gaussian curve) to **get the latest upload until one is found that isn't on a blacklist and then sends comments to it in a burst**
- config is all over the place, mostly just look for CHANGE_ME in all files and you should be good
- there is a timestamp setting for what should roughly be the peak of a modified gaussian curve of requests over time (hour before target to hour after)
- gaussian curve can be visualized (plt lines which are commented out) and is pre-cached for speed
- to run this on **multiple accounts** simmultaneously please **run multiple instances with different client_tokens** (just rename the file after launching an instance to re-login with a different account)
  - also a good idea to adjust latency and user_comments variables before launching another instance
  - this way you will cover more time-space and have a higher chance of getting the first comment spot
- ideally **you should run bulks of instances in different parts of the globe** to reach the closest data-centre there, 
  - because of how distributed servers for a platform like YouTube work, please **read up on "eventual consistency"**
  - this would require you to rent a bunch of AWS EC2 instances or similar and likely use clustering software solutions to be able to communicate with all of the instances and gather data from them
  - this part wasn't tested, i got close towards getting a first comment on a video with a reward prize for it, but likely lost because i didn't have time for this

### _run_comment_saver

> a way to identify the true first comment

**retrieves all comments for a video** (requests must be made until last page in API is reached for the first comment)
- config is all over the place, mostly just look for CHANGE_ME in all files and you should be good
- provides a way to identify the true first comment by saving all of them to a log, you will have to do the scrolling yourself
  - normally because of how distributed servers work on platforms like YouTube you won't see the actual first comment right as it gets posted, but later after they sync up
- be aware, that the log can reach 100s of MBs and you could waste your whole daily API quota on this alone
  - there are 20 comments retreivable per request, so that means: (number of comments you see on your video on YouTube) / 20 = number of requests
  - each request right now costs 1 quota unit so that makes the final cost: (number of requests) * 1 = final quota to be spent to retreive all comments

## Todo for better performance

Currently requires a lot of refactoring and optimization for better performance, but works *fairly decently*.
- There is a possibility that you would achieve better results by scrapping the whole Gaussian curve idea that I based my project around.
- There is a very strong possibility that you would achieve much better performance by refactoring and adjusting the delays in this project, adding a way to calculate them better and also implementing better async/multi-threading.

## Environment and Launch

```
python -m venv venv
venv/Scripts/activate
(which python / where python => venv)
(which pip / where pip => venv)
pip install -r requirements.txt
python _run_... (your choice)
```

- you need to provide your own `client_secret.json` from the Google API Console
https://developers.google.com/youtube/v3/quickstart/python?hl=en#step_1_set_up_your_project_and_credentials
  - create a new project
  - add YouTube DATA API to it
  - create an OAuth login method for it with scopes mentioned in __yt_api.py (Ctrl+F scopes)
  - afterwards the site will give you a download link for .JSON, rename it to client_secret.json, put it to the project folder and don't share it with anyone
  - please see __yt_api.py and Google API documentation for details, this is the hardest part
- ideally run this in a console where you can Ctrl+Click links to open them in a browser, because you will need to do this once for a long Google authentication link

### YouTube API Credentials

- `client_secret.json` needs to be obtained from API console as mentioned
- `client_tokens.json` gets generated on run and saves session tokens so you don't need to reauthorize on each run

## Original plan

- Implement YouTube API or use a reasonably fast 3rd party library
  - Goal is to **fetch YouTube channel recent videos** in a loop (1 quota credit / request I think) until a new upload within our timeframe is found.
  - **Gaussian curve** of requests (find and modify a relevant equation): 
    - Start 1 hour prior just in case
    - Focus on periodic timeframes around scheduling targets possible within YouTube Studio
    - Peak around proper publish time
    - If no new upload found continue trying periodically
- Schedule vids to **measure API delay** on publish of a scheduled video to take it into the equation
- Use **throwaway Google account** just in case (there will be more people attempting something similar in the same timeframe, potentially raising DDOS suspicion at YouTube and you don't want to be considered a bot by Google and get your main account purged without support)
- Launch **multiple instances** on multiple accounts over different networks with **different API delay** setting to cover more time.
- If no success still keep periodically trying in Gaussian curve bursts until new video or give up at a given time.
- When new upload is found:
  - Send an insert request for a comment to the API immediately afterwards taking response into account (retry if error)
  - Additional insert request with different contents 750ms after first.
- Ideally GZip all requests.
