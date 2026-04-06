import os
import time
import requests
import json

import dropbox
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =========================
# CONFIG
# =========================
SCOPES = ["https://www.googleapis.com/auth/drive"]

APP_KEY = "DROP_BOX_APP_KEY"
APP_SECRET = "DROP_BOX_APP_SECRET"
REFRESH_TOKEN = "YOUR_REFRESH_TOKEN"

DROPBOX_FOLDER = "DROP_BOX_FOLDER"
DRIVE_FOLDER_NAME = "DRIVE_FOLDER"

SLEEP_SECONDS = 30

#=========================
# DROP BOX
#=========================
def connect_to_drop_box():
    token_file = "drop_box_token.json"

    # Check if token already exists
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            data = json.load(f)

        refresh_token = data.get("refresh_token")

        if refresh_token:
            print("Using existing refresh token")
            return refresh_token
        else:
            print("Token file exists but no refresh token found. Re-authenticating...")

    # OAuth flow
    auth_url = (
        "https://www.dropbox.com/oauth2/authorize"
        "?response_type=code"
        f"&client_id={APP_KEY}"
        "&token_access_type=offline"
    )

    print("Go to this URL and authorize:")
    print(auth_url)

    code = input("Enter the authorization code: ").strip()

    token_url = "https://api.dropboxapi.com/oauth2/token"

    response = requests.post(token_url, data={
        "code": code,
        "grant_type": "authorization_code",
        "client_id": APP_KEY,
        "client_secret": APP_SECRET
    })

    token_data = response.json()

    with open(token_file, "w") as f:
        json.dump(token_data, f, indent=2)

    print("New token saved.")

    return token_data.get("refresh_token")

# =========================
# GOOGLE DRIVE
# =========================
def connect_to_drive():
    creds = None

    if os.path.exists("drive_token.json"):
        creds = Credentials.from_authorized_user_file("drive_token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "drive_credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("drive_token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def get_drive_folder_id(service):
    results = service.files().list(
        q=f"mimeType='application/vnd.google-apps.folder' and name='{DRIVE_FOLDER_NAME}'",
        fields="files(id, name)"
    ).execute()

    folders = results.get("files", [])

    if not folders:
        raise Exception("Drive folder not found")

    return folders[0]["id"]


def upload_to_drive(filename, service, folder_id):
    try:
        file_metadata = {"name": filename, "parents": [folder_id]}
        media = MediaFileUpload(filename)

        service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        print(f"Uploaded {filename} to Google Drive")
        return True
    except Exception as e:
        print(f"Could not upload {filename}: {e}")
        return False


# =========================
# DROPBOX
# =========================
def get_dropbox_client():
    return dropbox.Dropbox(
        oauth2_refresh_token=REFRESH_TOKEN,
        app_key=APP_KEY,
        app_secret=APP_SECRET
    )


# =========================
# MAIN LOOP
# =========================
if __name__ == "__main__":
    # Get config
    with open("config.json", "r") as config:
        config_json = json.load(config)
        APP_KEY = config_json.get("APP_KEY")
        APP_SECRET = config_json.get("APP_SECRET")
        DROPBOX_FOLDER = config_json.get("DROPBOX_FOLDER")
        DRIVE_FOLDER_NAME = config_json.get("DRIVE_FOLDER_NAME")
        SLEEP_SECONDS = config_json.get("SLEEP_SECONDS")

    # Connect
    creds = connect_to_drive()
    drive_service = build("drive", "v3", credentials=creds)
    folder_id = get_drive_folder_id(drive_service)

    REFRESH_TOKEN = connect_to_drop_box()
    dbx = get_dropbox_client()

    while True:
        try:
            result = dbx.files_list_folder(DROPBOX_FOLDER)

            for entry in result.entries:
                if not isinstance(entry, dropbox.files.FileMetadata):
                    continue

                path = entry.path_display
                name = entry.name

                # Download file
                metadata, res = dbx.files_download(path)

                with open(name, "wb") as f:
                    f.write(res.content)

                print(f"Downloaded {name}")

                # Upload to Drive
                if not upload_to_drive(name, drive_service, folder_id):
                    continue

                # Delete from Dropbox
                dbx.files_delete_v2(path)
                print(f"Deleted {name} from Dropbox")

                # Delete local file
                os.remove(name)

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(SLEEP_SECONDS)