import tkinter as tk
from tkinter import ttk, messagebox
from bs4 import BeautifulSoup
import requests
import os

# ---------------------- THEME SETTINGS ----------------------
THEME = {
    "bg_color": "#080810",          # window background
    "fg_color": "#ffffff",          # text color
    "btn_bg": "#ffffff",            # button background
    "btn_fg": "#000000",            # button text color
    "entry_bg": "#2e2e3f",          # entry background
    "entry_fg": "#ffffff",          # entry text color
    "font_main": ("Arial", 12),
    "font_button": ("Arial", 11, "bold"),
    "font_title": ("Arial", 14, "bold")
}

# ---------------------- BOOK FUNCTIONS ----------------------
def search_books_online(topic, book_name):
    search_query = f"{book_name} filetype:pdf"
    duckduckgo_url = "https://html.duckduckgo.com/html/"
    headers = {"User-Agent": "Mozilla/5.0"}
    data = {"q": search_query}
    try:
        response = requests.post(duckduckgo_url, headers=headers, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Search failed: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    for link in soup.find_all('a', class_="result__url"):
        title = link.text.strip()
        url = link.get("href")
        if "pdf" in url.lower():
            results.append((title, url))
    return results[:10]  # Limit to 10 results

def download_book(url, book_name, title):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        folder = f"./{book_name}"
        os.makedirs(folder, exist_ok=True)
        filename = f"{folder}/{title}.pdf".replace("/", "_").replace("\\", "_")
        with open(filename, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    except Exception as e:
        messagebox.showerror("Download Error", f"Failed to download {title}: {e}")

def save_results_to_file(results, book_name):
    folder = f"./{book_name}"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/{book_name}_results.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        for idx, (title, link) in enumerate(results, start=1):
            f.write(f"{idx}. {title}\n   Link: {link}\n\n")
    messagebox.showinfo("Saved", f"Results saved to {filename}")

# ---------------------- GUI FUNCTIONS ----------------------
def open_results_window(results, book_name):
    win = tk.Toplevel()
    win.title(f"Results for {book_name}")
    win.geometry("600x400")
    win.configure(bg=THEME["bg_color"])

    # Button frame at the bottom
    btn_frame = tk.Frame(win, bg=THEME["bg_color"])
    btn_frame.pack(side="bottom", fill="x", pady=5)

    # Buttons
    def download_selected():
        for var, title, link in vars_list:
            if var.get():
                download_book(link, book_name, title)
        messagebox.showinfo("Done", "Selected books downloaded!")

    def save_results():
        save_results_to_file(results, book_name)

    tk.Button(btn_frame, text="Download Selected", command=download_selected,
              bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=THEME["font_button"]).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Save Results", command=save_results,
              bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=THEME["font_button"]).pack(side="right", padx=10)

    # Scrollable results frame
    canvas = tk.Canvas(win, bg=THEME["bg_color"])
    canvas.pack(side="top", fill="both", expand=True)

    frame = tk.Frame(canvas, bg=THEME["bg_color"])
    canvas.create_window((0,0), window=frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame.bind("<Configure>", on_frame_configure)

    # Checkbuttons
    vars_list = []
    for title, link in results:
        var = tk.IntVar()
        chk = tk.Checkbutton(frame, text=title, variable=var,
                             bg=THEME["bg_color"], fg=THEME["fg_color"],
                             selectcolor="#555555", anchor="w",
                             font=THEME["font_main"], wraplength=500, justify="left")
        chk.pack(anchor="w", padx=10, pady=2)
        vars_list.append((var, title, link))

def search_action():
    topic = topic_var.get()
    book_names = entry_books.get().split(",")
    for book_name in book_names:
        book_name = book_name.strip()
        if not book_name:
            continue
        results = search_books_online(topic, book_name)
        if results:
            open_results_window(results, book_name)
        else:
            messagebox.showinfo("No Results", f"No books found for '{book_name}'.")

# ---------------------- MAIN GUI ----------------------
root = tk.Tk()
root.title("Book Finder")
root.geometry("400x250")
root.configure(bg=THEME["bg_color"])

# Topic selection
ttk.Label(root, text="Select Topic:", font=THEME["font_title"], background=THEME["bg_color"], foreground=THEME["fg_color"]).pack(pady=5)
topic_var = tk.StringVar(value="science")
topics = ["science","growth","agriculture","technology","history","fiction","philosophy","other"]
ttk.Combobox(root, textvariable=topic_var, values=topics, font=THEME["font_main"]).pack(pady=5)

# Book names input
ttk.Label(root, text="Enter Book Names (comma-separated):", font=THEME["font_main"], background=THEME["bg_color"], foreground=THEME["fg_color"]).pack(pady=5)
entry_books = tk.Entry(root, width=40, bg=THEME["entry_bg"], fg=THEME["entry_fg"], font=THEME["font_main"])
entry_books.pack(pady=5)

# Search button
tk.Button(root, text="Search", command=search_action,
          bg=THEME["btn_bg"], fg=THEME["btn_fg"], font=THEME["font_button"]).pack(pady=20)

root.mainloop()
