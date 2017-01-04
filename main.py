from xbmcswift2 import Plugin
import os
import re
import requests
import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import xbmcplugin
import json
import hashlib
import zipfile

plugin = Plugin()

def log(x):
    xbmc.log(repr(x))


@plugin.route('/service')
def service():
    d = xbmcgui.Dialog()
    d.notification("Downloader","service")
    file_name = 'special://profile/addon_data/plugin.program.downloader/downloads.json'
    data = xbmcvfs.File(file_name,'rb').read()
    if data:
        downloads = json.loads(data)
    else:
        downloads = {}

    for name in downloads:
        log("[plugin.program.downloader] Starting %s" % name)

        download = downloads[name]
        url = download["url"]
        folder = download["folder"]
        user = download["user"]
        password = download["pass"]
        if user and password:
            auth = (user, password)
        else:
            auth = None

        filename = url.rsplit('/',1)[-1]
        if not filename:
            log(("ERROR",url))
            continue
        local_filename = folder + filename
        local_temp_filename = local_filename + ".tmp"
        local_md5_filename = local_filename + ".md5"
        remote_md5_url = url + ".md5"

        local_md5 = xbmcvfs.File(local_md5_filename,"rb").read()[:32]
        r = requests.get(remote_md5_url,auth=auth)
        if r.status_code == requests.codes.ok:
            remote_md5 = r.text.encode('ascii', 'ignore')[:32]
        else:
            remote_md5 = None

        if local_md5 and remote_md5 and local_md5 == remote_md5:
            log("DOWNLOAD NOT NEEDED: " + url)
            continue

        f = xbmcvfs.File(local_temp_filename,"wb")
        r = requests.get(url,auth=auth, stream=True, verify=False)
        if r.status_code == requests.codes.ok:
            chunk_size = 16 * 1024
            for chunk in r.iter_content(chunk_size):
                success = f.write(chunk)
                log(success)
            f.close()
        else:
            log("FAILED TO DOWNLOAD: " + url)
            continue

        md5 = hashlib.md5()
        md5.update(xbmcvfs.File(local_temp_filename,"rb").read())
        tmp_md5 = md5.hexdigest()

        if remote_md5 and tmp_md5 != remote_md5:
            log("FAILED MD5: " + url)
            continue

        if xbmcvfs.exists(local_filename):
            success = xbmcvfs.delete(local_filename)
            if not success:
                log("FAILED TO DELETE: " + local_filename)
                continue

        success = xbmcvfs.rename(local_temp_filename,local_filename)
        if not success:
            log("FAILED TO RENAME: " + local_filename)
            continue

        xbmcvfs.File(local_md5_filename,"wb").write(tmp_md5)

        magic = xbmcvfs.File(local_filename,"rb").read(4)
        if magic == "\x50\x4b\x03\x04":
            z = zipfile.ZipFile(local_filename, "r")
            z.extractall(folder)

        #TODO delete

        log("[plugin.program.downloader] Finished %s" % name)

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
            folder = d.browse(3, 'Folder', 'files', '', False, False)
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
                new_folder = d.browse(3, 'Folder', 'files', '', False, False)
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