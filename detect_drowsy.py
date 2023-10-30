import torch
import numpy as np
import tkinter as tk
import customtkinter as ctk 
from PIL import Image, ImageTk

import os
import cv2
import time
import threading
import vlc

model = torch.hub.load('ultralytics/yolov5', 'custom', path='last.pt', force_reload=True)

counter_treshold = 10
alarm = False
alarm_counter = 0
closed_eye = 0
yawn = 0

app = tk.Tk()
app.geometry("600x600")
app.title("Drowsy Detection")
ctk.set_appearance_mode("dark")

vidFrame = tk.Frame(height=480, width=600)
vidFrame.pack()
vid = ctk.CTkLabel(vidFrame)
vid.pack()

counterLabel = ctk.CTkLabel(master=app,
                            text=alarm_counter,  
                            height=40, 
                            width=120, 
                            font=("Arial", 20), 
                            text_color="white", 
                            fg_color="teal")
counterLabel.pack(pady=10)


def reset_counter():
    global counter
    global closed_eye
    global yawn
    
    counter = 0
    closed_eye = 0
    yawn = 0
    
def start_alarm():
    global alarm
    
    if alarm:
        print("ALARM")
        p = vlc.MediaPlayer(f"file:///drowsy_alert.wav")
        p.play()
        Ended = 6
        current_state = p.get_state()
        while current_state != Ended:
            current_state = p.get_state()
        alarm = False
    

cap = cv2.VideoCapture(0)
def detect():
    global closed_eye
    global yawn
    global alarm_counter
    global alarm
    global counter_treshold

    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Make detections 
    results = model(frame)
    img = np.squeeze(results.render())
    
    if len(results.xywh[0]) > 0:
        for d in results.xywh[0]:
            if d[4] > 0.85 and d[5] == 18:
                closed_eye += 1
            
            if d[4] > 0.85 and d[5] == 17:
                yawn +=1
        
        if closed_eye > 0 or yawn > 0:
            alarm_counter += 1
            reset_counter()
        else:
            if alarm_counter > counter_treshold:
                alarm_counter = alarm_counter % counter_treshold
            elif alarm_counter > 0:
                alarm_counter -= 1

    if alarm_counter > 10 and not alarm:
        alarm = True
        threading.Thread(target=start_alarm).start()
                
    imgarr = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(imgarr) 
    vid.imgtk = imgtk
    vid.configure(image=imgtk)
    vid.after(10, detect) 
    counterLabel.configure(text=alarm_counter)  

detect()
app.mainloop()
