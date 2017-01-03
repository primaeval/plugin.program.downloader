import xbmc,xbmcaddon
import requests
import base64
import datetime, time
from datetime import date, timedelta

def log(x):
    xbmc.log(repr(x))
    
def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

ADDON = xbmcaddon.Addon('plugin.program.downloader')

last_time = datetime.datetime.fromtimestamp(time.mktime(time.strptime(ADDON.getSetting('serviced').encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))
if not last_time:
    last_time = datetime.datetime.now()
#log(last_time)
if ADDON.getSetting('startup') == 'true':
    xbmc.executebuiltin('RunPlugin(plugin://plugin.program.downloader/service)')
    now = datetime.datetime.now()
    ADDON.setSetting('serviced', str(now + timedelta(hours=0)).split('.')[0])
    #log(("service",datetime.datetime.now()))

monitor = xbmc.Monitor()
timer = ADDON.getSetting('timer')
#log(timer)

if timer and timer != 'None':
    while not xbmc.abortRequested:
        last_time = datetime.datetime.fromtimestamp(time.mktime(time.strptime(ADDON.getSetting('serviced').encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))
        #log(("last time",last_time))
        next_time = None
        if ADDON.getSetting('timer') == 'Period':
            period = ADDON.getSetting('period')
            if period:
                next_time = last_time + timedelta(seconds=int(period))
                #log(period)
        else:
            next_time = ADDON.getSetting('time')
            log(("next time",next_time))
            if next_time:
                hour,minute = next_time.split(':')
                now = datetime.datetime.now()
                next_time = now.replace(hour=int(hour),minute=int(minute),second=0,microsecond=0)
                log(("next time",next_time))
                if next_time < now:
                    next_time = next_time + timedelta(hours=24)
                
        #log(("next time",next_time))
        if not next_time:
            quit()
        now = datetime.datetime.now()
        #log(("now",now))
        waiting_time = next_time - now
        seconds = total_seconds(waiting_time)
        #log(("waiting time",seconds))
        if seconds == 0 and timer == 'Time':
            seconds = 86400
        elif seconds < 1:
            seconds = 1
        #log(("waiting time",seconds))
        monitor.waitForAbort(float(seconds))
        if xbmc.abortRequested:
            quit()
        xbmc.executebuiltin('RunPlugin(plugin://plugin.program.downloader/service)')
        log(("service",datetime.datetime.now()))
        ADDON.setSetting('serviced', str(datetime.datetime.now() + timedelta(hours=0)).split('.')[0])

