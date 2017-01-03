from xbmcswift2 import Plugin
import os
import re
import requests
import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import xbmcplugin


plugin = Plugin()

@plugin.route('/service')
def service():
    d = xbmcgui.Dialog()
    d.notification("Downloader","service")

@plugin.route('/')
def index():
    items = []

    items.append(
    {
        'label': "Service",
        'path': plugin.url_for('service'),
        'thumbnail': 'special://home/addons/plugin.program.downloader/icon.png',
    })
    return items

if __name__ == '__main__':
    plugin.run()