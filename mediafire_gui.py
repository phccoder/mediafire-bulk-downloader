import os
import sys
import threading
import subprocess
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import mediafire 

class MediafireDownloaderApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly") 
        self.title("Mediafire Bulk Downloader (IDM Style)")
        self.geometry("950x600")
        
        self.output_dir = os.getcwd()
        
        # Inject our GUI progress callback directly into the mediafire module
        mediafire.UI_CALLBACK = self.progress_callback
        
        self.setup_ui()

    def setup_ui(self):
        # --- Top Frame: Inputs ---
        input_frame = ttk.Frame(self, padding=20)
        input_frame.pack(fill=X)

        ttk.Label(input_frame, text="Mediafire URL:").pack(side=LEFT, padx=(0, 10))
        self.url_entry = ttk.Entry(input_frame, width=50)
        self.url_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))

        self.btn_download = ttk.Button(input_frame, text="Download", bootstyle=SUCCESS, command=self.start_download)
        self.btn_download.pack(side=LEFT)

        # --- Directory Frame ---
        dir_frame = ttk.Frame(self, padding=(20, 0, 20, 10))
        dir_frame.pack(fill=X)

        self.lbl_dir = ttk.Label(dir_frame, text=f"Output: {self.output_dir}")
        self.lbl_dir.pack(side=LEFT, fill=X, expand=True)

        ttk.Button(dir_frame, text="Change Folder", bootstyle=SECONDARY, command=self.change_directory).pack(side=RIGHT)

        # --- Treeview (IDM Style File Tracking) ---
        table_frame = ttk.Frame(self, padding=20)
        table_frame.pack(fill=BOTH, expand=True)

        # Expanded columns for detailed progress
        columns = ("filename", "size", "progress", "speed", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("filename", text="File Name")
        self.tree.heading("size", text="Size")
        self.tree.heading("progress", text="Progress")
        self.tree.heading("speed", text="Speed")
        self.tree.heading("status", text="Status")
        
        self.tree.column("filename", width=300)
        self.tree.column("size", width=80, anchor=E)
        self.tree.column("progress", width=220, anchor=CENTER)
        self.tree.column("speed", width=100, anchor=E)
        self.tree.column("status", width=120, anchor=W)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # --- Bottom Controls ---
        control_frame = ttk.Frame(self, padding=(20, 0, 20, 20))
        control_frame.pack(fill=X)

        ttk.Button(control_frame, text="Open File", bootstyle=INFO, command=self.open_file).pack(side=LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Open Folder", bootstyle=INFO, command=self.open_folder).pack(side=LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Delete Selected", bootstyle=DANGER, command=self.delete_file).pack(side=RIGHT)

    # --- Formatting Helpers ---
    @staticmethod
    def format_size(bytes_size):
        if bytes_size == 0:
            return "Unknown"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"

    @staticmethod
    def format_speed(bytes_per_sec):
        if bytes_per_sec == 0:
            return "0 B/s"
        for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
            if bytes_per_sec < 1024.0:
                return f"{bytes_per_sec:.1f} {unit}"
            bytes_per_sec /= 1024.0
        return "Fast"

    # --- Progress Callback (Called by mediafire.py background thread) ---
    def progress_callback(self, filename, downloaded, total, speed, status):
        size_str = self.format_size(total)
        speed_str = f"{self.format_speed(speed)}" if speed > 0 and status == "Downloading..." else ""
        
        if total > 0:
            percent = (downloaded / total) * 100
            prog_str = f"{self.format_size(downloaded)} / {size_str} ({percent:.1f}%)"
        else:
            prog_str = f"{self.format_size(downloaded)} / Unknown"
            
        # Clean up UI text when finished
        if status in ["Completed", "Skipped (Exists)", "Error"]:
            speed_str = "" 
            if status == "Completed":
                prog_str = "100%"

        # Update Tkinter from main thread safely
        self.after(0, self._update_tree_item, filename, size_str, prog_str, speed_str, status)

    def _update_tree_item(self, filename, size_str, prog_str, speed_str, status):
        # Use filename as unique ID. If it doesn't exist, insert it. Otherwise, update it.
        if not self.tree.exists(filename):
            self.tree.insert("", END, iid=filename, values=(filename, size_str, prog_str, speed_str, status))
        else:
            self.tree.item(filename, values=(filename, size_str, prog_str, speed_str, status))

    def change_directory(self):
        folder_selected = filedialog.askdirectory(initialdir=self.output_dir)
        if folder_selected:
            self.output_dir = folder_selected
            self.lbl_dir.config(text=f"Output: {self.output_dir}")

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL")
            return

        self.btn_download.config(state=DISABLED)
        t = threading.Thread(target=self._process_download, args=(url,), daemon=True)
        t.start()

    def _process_download(self, url):
        import re
        folder_or_file = re.findall(
            r"mediafire\.com/(folder|file|file_premium)\/([a-zA-Z0-9]+)", url
        )

        if not folder_or_file:
            self.after(0, messagebox.showerror, "Error", "Invalid link")
            self.after(0, lambda: self.btn_download.config(state=NORMAL))
            return

        t, key = folder_or_file[0]
        
        try:
            self.after(0, self._update_tree_item, "System", "-", "-", "-", "Fetching metadata...")
            
            if t in {"file", "file_premium"}:
                mediafire.get_file(key, self.output_dir)
            elif t == "folder":
                mediafire.get_folders(key, self.output_dir, threads_num=10, first=True)
            
            self.after(0, self._update_tree_item, "System", "-", "-", "-", "Batch completed.")
        except Exception as e:
            self.after(0, messagebox.showerror, "Error", str(e))
        finally:
            self.after(0, lambda: self.btn_download.config(state=NORMAL))

    def get_selected_filename(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return None
        return self.tree.item(selected_item[0], "values")[0]

    def open_file(self):
        filename = self.get_selected_filename()
        if not filename or filename in ["System"]:
            return
            
        filepath = os.path.join(self.output_dir, filename)
        if os.path.exists(filepath):
            if os.name == 'nt': 
                os.startfile(filepath)
            elif os.name == 'posix': 
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.call([opener, filepath])
        else:
            messagebox.showerror("Error", "File not found.")

    def open_folder(self):
        if os.name == 'nt':
            os.startfile(self.output_dir)
        elif os.name == 'posix':
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.call([opener, self.output_dir])

    def delete_file(self):
        filename = self.get_selected_filename()
        if not filename or filename in ["System"]:
            return

        filepath = os.path.join(self.output_dir, filename)
        if os.path.exists(filepath):
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {filename}?")
            if confirm:
                try:
                    os.remove(filepath)
                    self._update_tree_item(filename, "-", "-", "-", "Deleted")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete file:\n{e}")
        else:
             messagebox.showerror("Error", "File not found.")

if __name__ == "__main__":
    app = MediafireDownloaderApp()
    app.mainloop()