#!/usr/bin/python3


import sys, time, types, subprocess, re


if sys.platform.startswith('win'):

    # on Windows the ping has poor precision
    # but it is not privileged operation, yay!

    import pythonping

    def ping (host, count=4):
        results = []
        if sys.platform.startswith('win'):
            responses = pythonping.ping(host, count=count)
            for response in responses:
                result = types.SimpleNamespace()
                result.timeout = response.message==None
                result.latency = response.time_elapsed_ms
                results.append(result)
        return results

elif sys.platform == 'linux':
    
    # on Linux ping is privileged but the system implementation
    # is much nicer. Lets parse its output

    def ping (host, count=4):
        args = "-c%d -i0.2" % count
        status, output = subprocess.getstatusoutput("ping " + args + " " + host)
        # do not need status
        output = output.split('\n')
        results = []
        for i in range(0,count):
            result = types.SimpleNamespace()
            result.timeout = True
            result.latency = 0
            m = re.search(r"time=([0-9.]+)\s+ms", output[i+1])
            if m:
                result.timeout = False
                result.latency = float(m[1])
            results.append(result)
        return results

else:

    print("Platform %s not supported!" % sys.platform)
    quit(1)


# get time from internet and return float number as offset from local time
# does not matter if it is accurate as long as its referenced in all instances
# that will be correlated
gUnixTimeOffset = None
def getUnixTimeOffset ():
    global gUnixTimeOffset
    import urllib.request, json, datetime
    with urllib.request.urlopen("http://worldtimeapi.org/api/etc/gmt") as url:
        data = json.loads(url.read().decode())
    dt = datetime.datetime.fromisoformat(data["datetime"]) # since Python 3.7
    gUnixTimeOffset = dt.timestamp() - time.time()
    return gUnixTimeOffset

def getUnixTime():
    if gUnixTimeOffset is None:
        getUnixTimeOffset()
    return time.time() + gUnixTimeOffset


def measureJitter (host, count=4):
    pings = ping(host, count=count)
    sum = cnt = 0
    for p in pings:
        if not p.timeout:
            sum += p.latency
            cnt += 1
    avg = (sum / cnt) if cnt else 0
    sum = 0
    for p in pings:
        if not p.timeout:
            sum += abs(avg - p.latency)
    jtr = (sum / cnt) if cnt else 0
    return avg, jtr, (count - cnt)


if __name__ == "__main__":
    
    hosts = [ "192.168.100.1", "www.google.com" ]
    PINGCOUNT = 4
    INTERVALSEC = 2
    FOUTPATH = "jitter.log"

    timeStr = time.strftime("%H:%M:%S", time.localtime(getUnixTime()))
    text = "\n%s jitter monitoring started with UnixTime offset %.3fs" % (timeStr, gUnixTimeOffset)
    print(text)
    fout = open(FOUTPATH, "a")
    fout.write(text)
    fout.close()

    next = (int(getUnixTime()/INTERVALSEC)+1.5) * INTERVALSEC # start measurements in middle of interval
    while 1:
        while 1:
            now = getUnixTime()
            if now >= next:
                break
            time.sleep(0.05)
        # print timestamp first so sync across devices can be observed
        isTooSlow = now > next + 0.5
        timeStr = time.strftime("%H:%M:%S", time.localtime(next if isTooSlow else now))
        sys.stdout.write(timeStr)
        sys.stdout.flush()
        results = []
        if not isTooSlow:
            for i in range(len(hosts)):
                latency, jitter, dropped = measureJitter(hosts[i])
                results.append(latency)
                results.append(jitter)
                results.append(dropped)
#        msStr = ("%.3f" % math.modf(now)[0])
        for i in range(len(results)):
            r = results[i]
            results[i] = str(r) if isinstance(r, int) else format(r, ".3f")
        print(", " + ", ".join(results))
        sys.stdout.flush()
        fout = open(FOUTPATH, "a")
        fout.write("\n" +  timeStr + ", " + ", ".join(results))
        fout.close()
        next += INTERVALSEC
