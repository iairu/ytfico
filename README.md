# YouTube First Comment

## Plan

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

## Launch

```
python -m venv venv
venv/Scripts/activate
(which python / where python => venv)
(which pip / where pip => venv)
pip install -r requirements.txt
python .
```

