#Copyright primaeval - but you can use it for free if you can be nice to someone all day :)

import xbmc,xbmcaddon
import requests
import base64
import datetime, time
from datetime import date, timedelta

ADDON = xbmcaddon.Addon('plugin.program.downloader')

def log(x):
    xbmc.log(repr(x))

def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

def runService():
    log("[plugin.program.downloader] Starting Service...")
    xbmc.executebuiltin('RunPlugin(plugin://plugin.program.downloader/service)')
    log("[plugin.program.downloader] Finished Service...")
    now = datetime.datetime.now()
    ADDON.setSetting('serviced', str(now + timedelta(hours=0)).split('.')[0])


if ADDON.getSetting('startup') == 'true':
    runService()

monitor = xbmc.Monitor()
timer = ADDON.getSetting('timer')
if timer and timer != 'None':
    while not xbmc.abortRequested:
        last_time = datetime.datetime.fromtimestamp(time.mktime(time.strptime(ADDON.getSetting('serviced').encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))
        next_time = None
        if ADDON.getSetting('timer') == 'Period':
            period = ADDON.getSetting('period')
            if period:
                next_time = last_time + timedelta(hours=int(period))
        else:
            next_time = ADDON.getSetting('time')
            if next_time:
                hour,minute = next_time.split(':')
                now = datetime.datetime.now()
                next_time = now.replace(hour=int(hour),minute=int(minute),second=0,microsecond=0)
                if next_time < now:
                    next_time = next_time + timedelta(hours=24)

        if not next_time:
            quit()
        now = datetime.datetime.now()
        waiting_time = next_time - now
        seconds = total_seconds(waiting_time)
        if seconds == 0 and timer == 'Time':
            seconds = 86400
        elif seconds < 1:
            seconds = 1
        next = datetime.datetime.now() + timedelta(seconds=seconds+1)
        log("[plugin.program.downloader] Waiting Until %s (%s seconds to go)" % (str(next).split('.')[0], seconds))
        monitor.waitForAbort(float(seconds))
        time.sleep(1)
        if xbmc.abortRequested:
            quit()
        runService()

