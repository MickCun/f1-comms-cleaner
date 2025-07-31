import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
from customtkinter import CTkImage
import f1_comms_backend
import threading

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue") 

# Default App Setup. 
app = ctk.CTk(fg_color="#0F2C5F")
app.title("Red Bull Comms System")
app.geometry("1000x600")
app.minsize(1000, 600) 
app.maxsize(1000, 600)

# *** HOME SCREEN ***
# Set up the home screen, with the button and background image. 
home_frame = ctk.CTkFrame(master=app, fg_color="#0F2C5F")
home_frame.pack(fill="both", expand=True)

racing_background = Image.open("Media/RBR.png")
racing_background_ctk_image = CTkImage(
    light_image=racing_background,
    dark_image=racing_background,
    size=(1000, 600)
)

background_label = ctk.CTkLabel(home_frame, image=racing_background_ctk_image, text="")
background_label.place(x=0, y=0, relwidth=1, relheight=1)

begin_button = ctk.CTkButton(home_frame, text="Begin Race", font=ctk.CTkFont(size=22), fg_color="#FAD02C", text_color="black", width=200, height=60, command=lambda: switch_to_main())
begin_button.place(x=50, y=125)

main_frame = ctk.CTkFrame(master=app, fg_color="#0F2C5F")

def switch_to_main():
    home_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)

    f1_comms_backend.load_audio()
    f1_comms_backend.prepare_audio()
    threading.Thread(target=lambda: f1_comms_backend.live_process_audio(display_callback=update_comms_box), daemon=True).start()

    update_video()

# *** COMMS SCREEN ***
# Load image 
red_bull_logo = Image.open("Media/Red_bull_racing_logo.png")
logo_image = CTkImage(light_image=red_bull_logo, dark_image=red_bull_logo, size=(170, 70)) 
logo_label = ctk.CTkLabel(main_frame, image=logo_image, text="")
logo_label.place(x=30, y=30) 

# Live comms feed
comms_label = ctk.CTkLabel(main_frame, text="Live Comms", font=ctk.CTkFont(size=18, weight="bold"))
comms_label.place(x=30, y=110)

comms_box = ctk.CTkTextbox(main_frame, width=400, height=400)
comms_box.place(x=30, y=135)
comms_box.configure(state="disabled")


# Simulated Live Feed Video
video_path = "Media/F1_LIVE_VIDEO.mp4"
cap = cv2.VideoCapture(video_path)

video_label = ctk.CTkLabel(main_frame, text="")
video_label.place(x=480, y=60)

def update_video():
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (480, 300))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        img = ImageTk.PhotoImage(Image.fromarray(frame))
        video_label.configure(image=img)
        video_label.image = img  
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0) 
    app.after(66, update_video) 

update_video()


# Buttons
# Create Transcript Button
transcript_btn = ctk.CTkButton(main_frame, text="Create Transcript", width=180, height=100, font=ctk.CTkFont(size=25), fg_color="#FAD02C", text_color="black", command=f1_comms_backend.produce_comms_log)
transcript_btn.place(x=480, y=436)

# Export Wav Files Button
export_btn = ctk.CTkButton(main_frame, text="Export Audio Clips", width=180, height=100, font=ctk.CTkFont(size=25), fg_color="#FAD02C", text_color="black", command=f1_comms_backend.produce_combined_clean_wav_file)
export_btn.place(x=750, y=436)

# Update the comms box with the data from the comms system. 
def update_comms_box(text):
    comms_box.configure(state="normal")
    comms_box.insert("end", text + "\n")
    comms_box.see("end")
    comms_box.configure(state="disabled")

app.mainloop()