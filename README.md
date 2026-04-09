# Mediafire Bulk Downloader (IDM Style)

A modern, multi-threaded desktop application to bulk download files and folders from Mediafire. Built with Python and `ttkbootstrap`, this tool features an IDM-style (Internet Download Manager) interface that provides real-time progress tracking, download speeds, and file management.

screenshot.png *

## ✨ Features

* **Folder & File Support:** Paste a Mediafire folder link to bulk-download its entire contents recursively, or paste a single file link.
* **IDM-Style UI:** Track your downloads with real-time updates including total size, downloaded amount, percentage complete, and live download speed.
* **Multi-Threaded:** Downloads run in the background without freezing the UI, allowing for fast, concurrent fetching.
* **Bypass Link Protection:** Automatically handles Mediafire's GZip compression and scrambled `base64` download buttons.
* **Built-in File Manager:** Open downloaded files, open the output directory, or delete selected files directly from the application interface.
* **Modern Design:** Uses a sleek, dark-themed interface powered by `ttkbootstrap`.

## 🛠️ Prerequisites

* **Python 3.10+** (Standard Windows Python from python.org is highly recommended. *Note: Environments like MSYS2/MinGW may struggle to compile the required UI libraries.*)

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/mediafire_bulk_downloader.git](https://github.com/yourusername/mediafire_bulk_downloader.git)
   cd mediafire_bulk_downloader

2. **Create a virtual environment (Optional but recommended):**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    source venv/bin/activate  # On macOS/Linux

3. **Install the required dependencies:**
    ```bash
    pip install requests gazpacho ttkbootstrap

## 💻 Usage

Run the GUI application using Python:
    ```bash
    python mediafire_gui.py

1. Enter your Mediafire URL (Folder or File).

2. Click **Change Folder** to select where you want the files saved.

3. Click **Download**.

4. Watch the progress in the data table!


## 📦 Building a Standalone Executable (.exe)

If you want to share this application with friends who don't have Python installed, you can compile it into a single Windows `.exe` file using PyInstaller.

1. Install PyInstaller:
    ```bash
    pip install pyinstaller

2. Run the build command:
    ```bash
    pyinstaller --noconsole --onefile --windowed --name "MediafireDownloader" mediafire_gui.py

3. Your compiled application will be located in the newly created `dist/` folder.

## 📁 Project Structure

* `mediafire_gui.py` - The main entry point containing the Tkinter/ttkbootstrap frontend UI.
* `mediafire.py` - The backend scraping, parsing, and downloading logic.

## ⚠️ Disclaimer

This tool is for educational purposes and personal use. Please respect Mediafire's Terms of Service and only download content you have the rights or permission to access.