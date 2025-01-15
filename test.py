from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Upload
#file_list = drive.ListFile({'q': f"title = 'webfishing_backup.zip'"}).GetList()
#if file_list:
#    file_list[0].Delete()

#file2 = drive.CreateFile({'title': 'webfishing_backup.zip'})
#file2.SetContentFile('./download_cache/webfishing_backup.zip')
#file2.Upload()

# Download
file_list = drive.ListFile({'q': f"title = 'webfishing_backup.zip'"}).GetList()
if file_list:
    file_list[0].GetContentFile('./download_cache/webfishing_backup.zip')
    dt = datetime.strptime(file_list[0]['modifiedDate'], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
    print(dt)
