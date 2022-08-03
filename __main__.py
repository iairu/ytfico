import matplotlib.pyplot as plt
import numpy as np

# Define the Gaussian function (normal distribution)
def gauss(thickness, peak = 1, shift = 0):
    return lambda t: np.exp(-((t - shift) ** 2) / (2 * thickness ** 2)) * peak

def printer(timeline, arr):
    out = ""
    j = 0
    for i in timeline:
        out += str([arr[j], i]) + "\n"
        j += 1
    print(out)
    return

def normal(sum, peak, magic_multiplier = 1):
    return lambda x: np.round(np.round((x / sum) * peak) * magic_multiplier)

def normal_sum(curr_sum, wanted_sum, magic_multiplier = 1):
    return lambda x: np.round(np.round((curr_sum / wanted_sum if curr_sum < wanted_sum else wanted_sum / curr_sum) * x) * magic_multiplier) 

def merge(first, second):
    l = len(first)
    ll = len(second)
    out = list()

    for i in range(0, l if l < ll else ll, 1):
        out.append(first[i] if first[i] > second[i] else second[i])

    for i in range(l if l < ll else ll, l if l > ll else ll, 1):
        out.append(first[i] if l > ll else second[i])

    return out

def main():
    
    # total-length config for total gaussian curve
    rpm_peak = 30 # peak requests per minute, broken because of magic/rounding/noise
    t = 61 # minutes
    decay = 12

    g = gauss(decay, rpm_peak)
    timeline_mins = np.arange(-t,t + 1,1) # hour before, hour after peak, minute intervals
    modifier = lambda x: int(np.ceil(x))
    modified_gauss = list(modifier(g(i)) for i in timeline_mins)

    debug_approx = sum(modified_gauss)
    print("Approx total requests:" + str(debug_approx))
    # printer(timeline, modified_gauss)
    # plt.plot(timeline, modified_gauss)
    # plt.show()

    # ------------------

    # minute-length config before normalization to fit rpm
    t = 60 # seconds
    noise_peak = 3
    gauss_peak = 6
    gausf_decay = 3
    # set magic to 0 if you cant afford overshooting approximate targets
    magic = 1.68 # calculated as debug_approx / debug_actual to reduce inconsistency caused by rounding errors
    debug_actual = 0 # counter for total requests to compare with approximation and later estimate proper magic number to reduce inconsistency caused by rounding errors
    # minute-length processing
    for curr_t in timeline_mins:
        rpm = int(modifier(g(curr_t))) # takes the gaussian curve value for current minute
        print("Minute diff:" + str(curr_t))
        print("Set RPM:" + str(rpm))
        
        
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
        print("Actual Requests scheduled:" + str(int(sum(rpm_normalized_merge))) + "\n")
        debug_actual += sum(rpm_normalized_merge)
        # plt.plot(timeline, normalized_noise)
        # plt.plot(timeline, normalized_gauss)
        # plt.plot(timeline, normalized_merge)
        # plt.plot(timeline, rpm_normalized_merge)
        # plt.show()

        # todo: save rpm_normalized_merge to precache array

        # processing within a single second
        # todo: must be asynchronous
        # todo: separate from upper loop and use precache
        for curr_t_sec in range(t):
            # todo syncup: unix timestamp changed on level of seconds here otherwise wait
            now_req_count = int(rpm_normalized_merge[curr_t_sec])
            print(">> Sending " + str(now_req_count) + " requests")
            for k in range(now_req_count):
                print(">> Async Sent request")
        print("\n")
            


    magic_multiplier = debug_approx / debug_actual
    print("Approx total requests:" + str(debug_approx))
    print("Actual total requests:" + str(debug_actual))
    print("Calculated magic multiplier:" + str(magic_multiplier))

    # todo: create an additional 0-5sec gaussian burst at the beginning of a minute, sum its values and subtract them from triangular so the sum stays, then combine triangular with this gaussian


if __name__ == "__main__":
    main()