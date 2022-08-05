from datetime import datetime
from time import sleep
import matplotlib.pyplot as plt
import numpy as np
import asyncio
from threading import Thread

from __yt_api import YTCommenter

def printer(timeline, arr):
    out = ""
    j = 0
    for i in timeline:
        out += str([arr[j], i]) + "\n"
        j += 1
    print(out)
    return

# Define the Gaussian function (normal distribution)
def gauss(thickness, peak = 1, shift = 0):
    return lambda t: np.exp(-((t - shift) ** 2) / (2 * thickness ** 2)) * peak
def normal(sum, peak, magic_multiplier = 1):
    return lambda x: int(np.round(np.round((x / sum) * peak) * magic_multiplier))
def normal_sum(curr_sum, wanted_sum, magic_multiplier = 1):
    return lambda x: int(np.round(np.round((curr_sum / wanted_sum if curr_sum < wanted_sum else wanted_sum / curr_sum) * x) * magic_multiplier)) 
def merge(first, second):
    l = len(first)
    ll = len(second)
    out = list()
    for i in range(0, l if l < ll else ll, 1):
        out.append(first[i] if first[i] > second[i] else second[i])
    for i in range(l if l < ll else ll, l if l > ll else ll, 1):
        out.append(first[i] if l > ll else second[i])
    return out

def subhourly_gauss(rpm_peak = 30, decay = 12, t = 60):
    # total t is 2*t because subhourly (-t, t) - it is recommended to start the next loop around t == 0 or if each 30mins then t = 30
    # rpm_peak: peak of requests per minute, broken because of magic/rounding/noise
    # decay: gaussian deviation
    # t: in minutes (hour before and hour after)
    g = gauss(decay, rpm_peak)
    timeline_mins = np.arange(-t,t,1) # hour before, hour after peak, minute intervals
    modifier = lambda x: int(np.ceil(x))
    modified_gauss = list(modifier(g(i)) for i in timeline_mins)
    debug_approx = sum(modified_gauss)
    # print("Approx total requests:" + str(debug_approx))
    # printer(timeline_mins, modified_gauss)
    # plt.plot(timeline_mins, modified_gauss)
    # plt.show()
    return (timeline_mins, modifier, g, debug_approx)
def subhourly_minute_gauss(timeline_mins, modifier, g, noise_peak = 3, gauss_peak = 6, gausf_decay = 3, t = 60, magic = 1.68):
    # pre-normalization values:
    # - noise_peak: max amount of noise per second, can peak multiple times
    # - gauss_peak: max peak during initial seconds of this minute, peaks once (can drag for a few seconds)
    # - gausf_decay: die-off for the gaussian peak
    # t: in seconds (a single minute)
    # set magic to 0 if you cant afford overshooting approximate targets
    # magic: calculated as debug_approx / debug_actual to reduce inconsistency caused by rounding errors
    debug_actual = 0 # counter for total requests to compare with approximation and later estimate proper magic number to reduce inconsistency caused by rounding errors
    cpm_timeline = list() # cache per minute
    for curr_t in timeline_mins:
        rpm = int(modifier(g(curr_t))) # takes the gaussian curve value for current minute
        if (rpm > 0):
            print("Minute:" + str(curr_t + t))
            print("- Wanted:" + str(rpm))
            
        noise = np.random.triangular(0, 0, t - 1, t) # very stupid way to generate
        gausf = gauss(gausf_decay, 1)
        timeline = np.arange(0, t, 1)
        noise_normalizer = normal(t / noise_peak, 1)
        gauss_normalizer = normal(1, gauss_peak)
        normalized_noise = list(noise_normalizer(x) for x in noise)
        normalized_gauss = list(gauss_normalizer(gausf(i)) for i in timeline)
        normalized_merge = merge(normalized_noise, normalized_gauss)
        rpm_normalizer = normal_sum(sum(normalized_merge), rpm, magic)
        rpm_normalized_merge = list(rpm_normalizer(x) for x in normalized_merge)
        cpm_timeline.append(rpm_normalized_merge)
        if (rpm > 0):
            print("- Actual:" + str(int(sum(rpm_normalized_merge))) + "\n")
        debug_actual += sum(rpm_normalized_merge)
        # plt.plot(timeline, normalized_noise)
        # plt.plot(timeline, normalized_gauss)
        # plt.plot(timeline, normalized_merge)
        # plt.plot(timeline, rpm_normalized_merge)
        # plt.show()
    return (cpm_timeline, debug_actual)

def unix_seconds_utc():
    return int(datetime.utcnow().timestamp())
def unix_precise_utc():
    return datetime.utcnow().timestamp()

def run_resync(unix_last_utc, unix_target_utc, show_comments = False):
    # wait for next second
    now = unix_seconds_utc()
    while (now - unix_last_utc < 1):
        now = unix_seconds_utc()
    last = now

    away_sec = unix_target_utc - now
    away_min = away_sec / 60
    away_hr = away_min / 60

    if (show_comments): 
        print("Target is " + str(away_hr) + " hours away in total")
        print("Target is " + str(away_min) + " minutes away in total")
        print("Target is " + str(away_sec) + " seconds away in total")

    t_min_intro = 60 # minutes until peak
    if (away_min >= 0):
        target_min = t_min_intro - int(away_min) - 1
    else:
        target_min = t_min_intro - int(away_min)
    # if (target_min >= 120): target_min %= 120 # broken due to new threading implementation
    if (away_sec >= 0):
        target_sec = 60 - (int(away_sec) - int(away_min) * 60) - 1
    else:
        target_sec = - (int(away_sec) - int(away_min) * 60) - 1
    if (show_comments): 
        print("Position: cpm_timeline[" + str(target_min) + "] / minute_cache[" + str(target_sec) + "]")

    return (target_min, target_sec)
def target_sec_recalc(unix_target_utc):
    away_sec = unix_target_utc - unix_seconds_utc()
    away_min = away_sec / 60
    if (away_sec >= 0):
        target_sec = 60 - (int(away_sec) - int(away_min) * 60) - 1
    else:
        target_sec = - (int(away_sec) - int(away_min) * 60) - 1
    return target_sec
def target_min_recalc(unix_target_utc):
    away_sec = unix_target_utc - unix_seconds_utc()
    away_min = away_sec / 60
    t_min_intro = 60 # minutes until peak
    if (away_min >= 0):
        target_min = t_min_intro - int(away_min) - 1
    else:
        target_min = t_min_intro - int(away_min)
    # if (target_min >= 120): target_min %= 120 # broken due to new threading implementation
    return target_min


async def synchronization(cpm_timeline, unix_target_utc, run_count, thread_api_func, thread_api_func_args: tuple):
    runs_left = run_count
    last = 0
    async_id = 0
    show_extra_comments = True
    while runs_left:
        print("Runs left:" + str(runs_left))
        runs_left -= 1
        target_min, target_sec = run_resync(last, unix_target_utc, show_extra_comments)

        if target_min < 0 :
            print("Negative target_min, waiting...")
        else: # every subhour (-60; 60)
            # todo extra thread to target each hour, then
            # todo mirroring for gaussian function (for now just launch multiple instances with different targets)
            sub_last = 0

            while (target_min < 120):
                debug_curr_sum = sum(cpm_timeline[target_min])
                print("Sending " + str(sum(cpm_timeline[target_min])) + " requests/minute")

                # minute-length processing per second:
                threads = list()
                target_sec = target_sec_recalc(unix_target_utc)
                print("Position: cpm_timeline[" + str(target_min) + "]...")
                for curr_sec in range(target_sec,60):
                    # wait for next second
                    now = unix_seconds_utc()
                    while (now - sub_last < 1):
                        now = unix_seconds_utc()
                    sub_last = now

                    if (debug_curr_sum > 0):
                        # todo threading improvements possibly needed 
                        rps = int(cpm_timeline[target_min][curr_sec]) # procedural requests per second
                        if (rps > 0):
                            if (rps > 3): rps = 2 # todo quickfix for now !!!!!!!!!!!!!!!!!!!
                        print("Second " + str(now) + ": Sending " + str(rps) + " requests/second")
                        for k in range(rps):
                            print("- Async request ID:" + str(async_id))
                            thread = Thread(target=thread_api_func, args=(async_id, *thread_api_func_args))
                            thread.start()
                            threads.append(thread)
                            async_id += 1
                            sleep(float(750 / rps) / 1000) # todo quickfix spaced out requests except peak of second
                    
                    if (target_sec % 13 == 0): # todo quickfix again :((((((( thread count issues
                        print("Joining threads be patient...")
                        for thread in threads:
                            thread.join()
                        print("- Joining finished... Resyncing...")
                        target_min = target_min_recalc(unix_target_utc)


async def main():
    
    # ---------------------------
    # Gaussian cached RPM and RPS (User config in arguments, plot visualization commented out in functions)
    # ---------------------------

    cache_start = unix_precise_utc()

    # total-length config for total gaussian curve
    timeline_mins, modifier, g, debug_approx = subhourly_gauss(30, 12, 60)

    # minute-length config before normalization to fit rpm
    cpm_timeline, debug_actual = subhourly_minute_gauss(timeline_mins, modifier, g, 3, 6, 3, 60, 1.5)

    cache_secs = unix_precise_utc() - cache_start
    print("Caching took:" + str(cache_secs) + " seconds\n---\n")

    # ---------------------------
    # Gaussian tuning debug info
    # ---------------------------

    # print("Approx total requests:" + str(debug_approx))
    # print("Actual total requests:" + str(debug_actual))

    # magic_multiplier = debug_approx / debug_actual
    # print("Calculated magic multiplier:" + str(magic_multiplier))


    # ---------------------------
    # YT initialization (User config in _yt_api.py)
    # ---------------------------

    yt, yt_uid = YTCommenter.initialize(request_uid=True)
    
    # ---------------------------
    # Synchronization and API requests (User config right below and in _yt_api.py)
    # ---------------------------

    run_count = 1
    latency_ms = 47 # << CHANGE_ME! latency here and date below \/
    unix_target_utc = datetime(2022, 8, 4, 20, 00, 00).timestamp() - 1 # -1 for delay (1000 - latency added to each req.) introduced later
    delay = 1000 - latency_ms
    
    await synchronization(cpm_timeline, unix_target_utc, run_count, YTCommenter.get_lastest_upload_and_comment_burst, (yt, yt_uid, delay))

    # ---------------------------
    # Final info for user
    # ---------------------------
    YTCommenter.report()


asyncio.run(main())
