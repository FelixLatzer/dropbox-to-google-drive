# dropbox-to-google-drive

This project exists because the free version of Dropbox only provides **2GB of storage**, while most users have significantly more space available on Google Drive.

This script automatically transfers files from Dropbox to Google Drive, helping you effectively extend your Dropbox storage.

---

# 🚀 What it does

* Monitors a Dropbox folder
* Downloads new files
* Uploads them to Google Drive
* Deletes them from Dropbox
* Runs continuously

---

# 📋 Requirements

* Python 3.8+
* Dropbox account
* Google account

---

# 📦 Installation

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

python3 -m venv venv
source venv/bin/activate

pip install google-auth google-auth-oauthlib google-api-python-client dropbox requests
```

---

# 🔐 Setup

## 📁 Google Drive

Follow the official guide to create credentials:
👉 https://developers.google.com/drive/api/quickstart/python

Steps:

1. Create a project
2. Enable **Google Drive API**
3. Create OAuth Client ID (Desktop App)
4. Download credentials file and rename it to:

```bash
drive_credentials.json
```

5. Place it in the project root folder

⚠️ Set OAuth app to **Production** (otherwise tokens expire after 7 days)

---

## 📦 Dropbox

Create your app here:
👉 https://www.dropbox.com/developers/apps

### During setup:

* Choose **Scoped access** ✅
* Choose **App folder** (recommended)

👉 This means:

* Your script only has access to a dedicated folder inside Dropbox
* You’ll see something like:

  ```
  Apps/YourAppName/
  ```

### ⚠️ Important

When using **App folder access**:

* Your `DROPBOX_FOLDER` path is **relative to that app folder**
* Example:

  * App folder: `Apps/MyApp/`
  * Config:

    ```json
    "DROPBOX_FOLDER": "/"
    ```

  → refers to `Apps/MyApp/`

---

### Enable permissions:

* `files.metadata.read`
* `files.content.read`
* `files.content.write`

Then copy:

* `APP_KEY`
* `APP_SECRET`

---

# ⚙️ Configuration

Edit `config.json`:

```json
{
  "APP_KEY": "",
  "APP_SECRET": "",
  "DROPBOX_FOLDER": "/",
  "DRIVE_FOLDER_NAME": "",
  "SLEEP_SECONDS": 30
}
```

---

# ▶️ First Run

```bash
python main.py
```

* Google login will open in browser
* Dropbox authorization required once
* Tokens are saved locally

---

# 📁 Generated files

* `drive_token.json` → Google authentication
* `drop_box_token.json` → Dropbox refresh token

---

# 🔄 Run in background (optional)

```bash
nohup bash -c "source venv/bin/activate && python main.py" &
```

---

# ⚠️ Troubleshooting

### Google: `invalid_grant`

```bash
rm drive_token.json
```

Then run again and re-authenticate.

---

### Dropbox: `expired_access_token`

Handled automatically via refresh token.

---

# 🧠 Notes

* Files are **moved** (deleted from Dropbox after upload)
* Script runs every `SLEEP_SECONDS`
* Designed for long-running environments (server / Raspberry Pi)

---
