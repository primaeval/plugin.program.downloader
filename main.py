from xbmcswift2 import Plugin
import os
import re
import requests
import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import xbmcplugin
import json


plugin = Plugin()

def log(x):
    xbmc.log(repr(x))

@plugin.route('/service')
def service():
    d = xbmcgui.Dialog()
    d.notification("Downloader","service")

@plugin.route('/edit')
def edit():
    file_name = 'special://profile/addon_data/plugin.program.downloader/downloads.json'
    data = xbmcvfs.File(file_name,'rb').read()
    if data:
        downloads = json.loads(data)
    else:
        downloads = {}
    d = xbmcgui.Dialog()
    while True:
        keys = sorted(downloads.keys())
        labels = ["New"] + keys
        which = d.select("Edit Download",labels)
        if which == -1:
            data = json.dumps(downloads,indent=2)
            xbmcvfs.File(file_name,'wb').write(data)
            return
        elif which == 0:
            more = True
            while more:
                name = d.input("Unique Name")
                if not name or name not in downloads:
                    more = False
            url = d.input("URL")
            if not url:
                continue
            folder = d.input("Download Folder")
            if not folder:
                continue
            downloads[name] = {}
            downloads[name]["url"] = url
            downloads[name]["folder"] = folder
            downloads[name]["user"] = None
            downloads[name]["pass"] = None
            user = d.input("User Name")
            if not user:
                continue
            downloads[name]["user"] = user
            password = d.input("Password")
            if not password:
                continue
            downloads[name]["pass"] = password
        else:
            key = keys[which-1]
            download = downloads[key]
            url = download.get("url",'')
            folder = download.get("folder",'')
            user = download.get("user",'')
            if not user:
                user = ''
            password = download.get("pass",'')
            if not password:
                password = ''
            actions = ["Delete","URL: "+url,"Folder: "+folder,"User: "+user,"Password: "+password]
            action = d.select("Edit - %s" % key,actions)
            if action == -1:
                continue
            if action == 0:
                del downloads[key]
            elif action == 1:
                new_url = d.input("URL: "+url,url)
                if new_url:
                    download["url"] = new_url
            elif action == 2:
                new_folder = d.input("folder: "+folder,folder)
                if new_folder:
                    download["folder"] = new_folder
            elif action == 3:
                new_user = d.input("user: "+user,user)
                if new_user:
                    download["user"] = new_user                    
            elif action == 4:
                new_password = d.input("password: "+password,password)
                if new_password:
                    download["url"] = new_password
                        

@plugin.route('/')
def index():
    items = []

    items.append(
    {
        'label': "Download",
        'path': plugin.url_for('service'),
        'thumbnail': 'special://home/addons/plugin.program.downloader/icon.png',
    })
    items.append(
    {
        'label': "Edit",
        'path': plugin.url_for('edit'),
        'thumbnail': 'special://home/addons/plugin.program.downloader/icon.png',
    })
    return items

if __name__ == '__main__':
    plugin.run()