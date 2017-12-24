#Clock
import json #For reading JSON
import datetime #For getting current date
from tkinter import * #User interface
from time import gmtime, strftime, localtime, sleep #For getting time
from pygame import mixer #For alarm sound
from PIL import Image, ImageTk #For wallpapers
from os import listdir #For music player

def load_json(filename): #Function for loading JSON into an array
    with open(filename) as data_file:
        data = json.load(data_file)
    return data

class clock: #Window thing.
    def __init__(self, master):
        self.master = master
        master.title("Clock")

config = load_json("config.json") #Load config file. Used for version message and alarm.

root = Tk() #Create the actual window
root.resizable(0,0) #Don't allow user resizing.
root.attributes("-fullscreen", True) #Make window fullscreen.

#Get monitor size.
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

#Create canvas.
draw = Canvas(root, width=screen_width, height=screen_height)
draw.pack() #I don't know what this line does, but I was told I need it.

#Setup Wallpaper
if(config["USE_WALLPAPER"] == 1):
    wallpaper = Image.open(config["WALLPAPER_PATH"])
    wallpaperImage = ImageTk.PhotoImage(wallpaper)
    wallpaperObject = draw.create_image(screen_width / 2, screen_height / 2, image=wallpaperImage)

global stop_text
global stop_button
global playPause
global backButton
global nextButton
global musicList
global currentSong

#Setup music player icons
playImage = Image.open("img/play.png")
nextImage = Image.open("img/next.png")
prevImage = Image.open("img/back.png")
pauseImage = Image.open("img/pause.png")
playTk = ImageTk.PhotoImage(playImage)
nextTk = ImageTk.PhotoImage(nextImage)
prevTk = ImageTk.PhotoImage(prevImage)
pauseTk = ImageTk.PhotoImage(pauseImage)
playPause = draw.create_image(screen_width / 2, screen_height / 2 + 50, image=playTk)
backButton = draw.create_image(screen_width / 2 - 64, screen_height / 2 + 50, image=prevTk)
nextButton = draw.create_image(screen_width / 2 + 64, screen_height / 2 + 50, image=nextTk)

print("Music found:")
print(listdir(config["MUSIC_DIRECTORY"]))
musicList = listdir(config["MUSIC_DIRECTORY"])
currentSong = 0

def playMusic(hi):
    global currentSong
    global playPause
    playPause = draw.create_image(screen_width / 2, screen_height / 2 + 50, image=pauseTk)
    draw.tag_bind(playPause, '<ButtonPress-1>', pauseMusic)
    try:
        mixer.music.unpause()

    except:
        try:
            mixer.init()
            mixer.music.load(musicList[int(currentSong)])
            mixer.music.play()
        except:
            print("Couldn't play music. (Song: " + musicList[currentSong] + ")")
            currentSong += 1
            pauseMusic(1)
            pass

def pauseMusic(hi):
    global playPause
    draw.delete(playPause)
    playPause = draw.create_image(screen_width / 2, screen_height / 2 + 50, image=playTk)
    draw.tag_bind(playPause, '<ButtonPress-1>', playMusic)
    try:
        mixer.music.pause()
    except:
        print("Couldn't pause music?")
        mixer.stop()
        pass

def nextTrack(hi):
    global currentSong
    global musicList
    currentSong += 1
    if(currentSong > len(musicList)):
        currentSong = 0
    try:
        mixer.music.fadeout(500)
        mixer.init()
        mixer.music.load(musicList[currentSong])
        playMusic(1)

    except:
        print("Error switching to next track.")
        pass

def prevTrack(hi):
    global currentSong
    currentSong -= 1
    if(currentSong == 0):
        currentSong = len(musicList)
    try:
        mixer.music.fadeout(500)
        mixer.init()
        mixer.music.load(musicList[currentSong])
        playMusic(1)

    except:
        print("Error switching to previous track.")
        pass

draw.tag_bind(playPause, '<ButtonPress-1>', playMusic)
draw.tag_bind(backButton, '<ButtonPress-1>', prevTrack)
draw.tag_bind(nextButton, '<ButtonPress-1>', nextTrack)

def alarm_stop(t):
    print("Stopping alarm.")
    mixer.music.stop()
    global stop_text
    global stop_button
    draw.delete(stop_button)
    draw.delete(stop_text)

def alarm(): #Play alarm sound.
    global stop_text
    global stop_button
    print("ALARM! Starting playback.")
    mixer.music.load('alarm.mp3')
    mixer.music.play()
    while(mixer.music.get_busy() == False):
        mixer.music.play()
    stop_button = draw.create_rectangle(screen_width / 2 - 128, screen_height / 2 + 32, screen_width / 2 + 128, screen_height / 2 + 80, outline="red", fill="red")
    stop_text = draw.create_text(screen_width / 2, screen_height / 2 + 55, text="Stop", font="Ubuntu", fill="white")
    draw.tag_bind(stop_button, '<ButtonPress-1>', alarm_stop)

#Draw statusbar. TODO: Add functionality. (The clock will eventually get notifications from bluetooth.)
notificationmsg = "0 new notifications."
statusbar_bar = draw.create_rectangle(0, 0, screen_width, 20, fill="black")
statusbar_text = draw.create_text(screen_width / 2,12, text=notificationmsg, fill="white")

#Draw clock stuff. Placeholders are replaced with time and date every second.
clock_time = draw.create_text(screen_width / 2, screen_height / 2 - 64, text="This is a placeholder.", font=("Ubuntu", 64))
date = draw.create_text(screen_width / 2, screen_height / 2, text="This is a placeholder.", font=("Ubuntu"))

#Draw version info
ver_info = "Clock Version " + config["SOFTWARE_VERSION"]
ver_msg = draw.create_text(0, screen_height, text=ver_info, anchor=SW, font="Ubuntu")

global alarm_started
alarm_started = 0

#Function to update screen
def update():
    global alarm_started
    try:
        if(config["SHOW_SECONDS"] == 1):
            current_time = strftime("%I:%M:%S", localtime()) #Grab current time with seconds
        else:
            current_time = strftime("%I:%M", localtime()) #Grab current time
        if(int(strftime("%H")) > 12): #AM or PM?
            time_thing = "PM"
        else:
            time_thing = "AM"

        tmsg = current_time + " " + time_thing #Add suffix to time
        current_date = datetime.date.today().strftime("%B %d, %Y") #Grab date.
        if(datetime.date.today().strftime("%B") == "December"): #Happy holidays message
            draw.itemconfigure(ver_msg, text="Happy holidays!")

        if(strftime("%I:%M") + " " + time_thing == config["ALARM_TIME"]): #Hacked together alarm check
            mixer.init()
            if(mixer.music.get_busy() == False and alarm_started != 1):
                alarm()
                alarm_started = 1
        else:
            alarm_started = 0

        if(int(strftime("%I")) < 10):
            tmsg = tmsg.lstrip('0')
        draw.itemconfigure(clock_time, text=tmsg) #Update canvas items.
        draw.itemconfigure(date, text=current_date)
        draw.after(1000, update) #Do this again in 1 second.
    except StopIteration:
        pass

update() #Run the above function

clck = clock(root)
root.mainloop()
