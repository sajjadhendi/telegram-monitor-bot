import tkinter as tk
from tkinter import Label, Frame, Button, Toplevel
from PIL import Image, ImageTk
import cv2
from datetime import datetime

stream_urls = [
    "https://live.i-news.tv/hls/stream.m3u8",
    "https://5d94523502c2d.streamlock.net/home/mystream/playlist.m3u8",
    # ... بقية الروابط هنا
]

channel_names = [f"Channel {i+1}" for i in range(len(stream_urls))]

root = tk.Tk()
root.title("🛰️ لوحة رصد ومتابعة - 12 قناة مباشر")
root.configure(bg="#121212")
root.attributes('-fullscreen', True)

frames, labels, status_labels, clock_labels, caps = [], [], [], [], []

def update_frame(index):
    cap, label, status_label = caps[index], labels[index], status_labels[index]
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (240, 150))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        status_label.config(text="✅ شغال", fg="#00FF00")
    else:
        status_label.config(text="❌ متوقف", fg="red")

    now = datetime.now().strftime("%H:%M:%S")
    clock_labels[index].config(text=now)

    root.after(1000, update_frame, index)

def reload_stream(index):
    try:
        caps[index].release()
    except:
        pass
    caps[index] = cv2.VideoCapture(stream_urls[index])
    status_labels[index].config(text="♻️ جاري إعادة التحميل", fg="orange")

def mute_stream(index):
    status_labels[index].config(text="🔇 كتم (اختباري)", fg="yellow")

def open_fullscreen(index):
    fs_win = Toplevel(root)
    fs_win.attributes('-fullscreen', True)
    fs_win.configure(bg="black")

    fs_label = Label(fs_win, bg="black")
    fs_label.pack(expand=True, fill="both")

    cap = cv2.VideoCapture(stream_urls[index])

    def update_fs_frame():
        ret, frame = cap.read()
        if ret:
            screen_w = fs_win.winfo_screenwidth()
            screen_h = fs_win.winfo_screenheight()
            frame = cv2.resize(frame, (screen_w, screen_h))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            fs_label.imgtk = imgtk
            fs_label.configure(image=imgtk)

        if fs_win.winfo_exists():
            fs_win.after(30, update_fs_frame)

    def close_fs(event=None):
        cap.release()
        fs_win.destroy()

    fs_win.bind("<Escape>", close_fs)
    update_fs_frame()

for i in range(len(stream_urls)):
    frame = Frame(root, bg="#1f1f1f", bd=3, relief="ridge")
    frame.grid(row=i // 4, column=i % 4, padx=8, pady=8)

    lbl_title = Label(frame, text=channel_names[i], bg="#2c2c2c", fg="white", font=("Arial", 14, "bold"))
    lbl_title.pack(fill="x")

    lbl_video = Label(frame, bg="black", cursor="hand2")
    lbl_video.pack()

    lbl_status = Label(frame, text="🔄 جاري التحميل", bg="#1f1f1f", fg="orange", font=("Arial", 11))
    lbl_status.pack()

    lbl_clock = Label(frame, text="00:00:00", bg="#1f1f1f", fg="#00ffff", font=("Arial", 12, "bold"))
    lbl_clock.pack()

    btn_reload = Button(frame, text="🔄 إعادة التحميل", command=lambda idx=i: reload_stream(idx), bg="#333", fg="white", font=("Arial", 10))
    btn_reload.pack(pady=2, fill="x")

    btn_mute = Button(frame, text="🔇 كتم الصوت", command=lambda idx=i: mute_stream(idx), bg="#333", fg="white", font=("Arial", 10))
    btn_mute.pack(pady=2, fill="x")

    lbl_video.bind("<Button-1>", lambda e, idx=i: open_fullscreen(idx))

    frames.append(frame)
    labels.append(lbl_video)
    status_labels.append(lbl_status)
    clock_labels.append(lbl_clock)

    cap = cv2.VideoCapture(stream_urls[i])
    caps.append(cap)

    root.after(0, update_frame, i)

def on_close():
    for cap in caps:
        cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.bind("<Escape>", lambda e: on_close())

root.mainloop()
