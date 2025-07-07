import tkinter as tk #main ui library
from tkinter import filedialog
import pygame.mixer as sound #main sound library
from os import walk
from mutagen.mp3 import MP3 #mutagen needs to be installed with "pip install mutagen"
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
from time import sleep
import threading
from keyboard import hook #keyboard needs to be installed with "pip install keyboard"
import json as j

#region initialise
r = tk.Tk()
r.title('Lightning Media Player')
r.state('zoomed')
r.geometry('800x600')
r.minsize(320, 232)
sound.init()

WID = 1920
HEI =  1080
scroll = 0
songCurrentlyPlaying = -1
paused = False
bpfs = 0
diff = 0
timeR = ''
song = ''
l = 1
D = __file__.replace(__file__.split('\\')[-1], '')

allSongs = []
with open(D + 'settings.json', 'r') as f:
    playlists = j.load(f)['songFolders']
for i in playlists:
    for root, dirs, files in walk(i):
        files = [f.replace(f, i + '/' + f) for f in files]
        allSongs.extend(files)
allSongs = [i for i in allSongs if i.split('.')[-1] in ('mp3', 'wav', 'ogg', 'oga', 'mogg')]

#endregion

#region threads
def timer_bar():
    global l, bpfs, diff

    n = bpfs * 4
    playMenu.delete('timeline')
    diff = 88 + (n / (l * 4)) * (playMenu.winfo_width() - 176)
    playMenu.create_line(88, 16, diff, 16, width=4, fill='#FF7F3F',
                        capstyle='round', tags='timeline')
    playMenu.create_line(diff, 16, diff, 16, width=22, fill='#454545',
                        capstyle='round', tags='timeline')
    playMenu.create_line(diff, 16, diff, 16, width=10, fill='#FF7F3F',
                        capstyle='round', tags='timeline')

def timer_nums():
    global l, bpfs, timeR
    n = int(bpfs)
    bpf = (int(n // 3600), int(n % 3600 // 60), n % 60)
    timeL = ':'.join((str(bpf[0]).zfill(2), str(bpf[1]).zfill(2),
                    str(bpf[2]).zfill(2)))
    timeR = ':'.join((str(int(l - n) // 3600).zfill(2),
                    str(int((l - n) % 3600) // 60).zfill(2),
                    str(int(l - n) % 60).zfill(2)))
    playMenu.delete('timeL')
    playMenu.create_text(
        16, 12, text=timeL, font=('Consolas', 10),
        anchor='w', fill='#ffffff', tags='timeL')
    playMenu.delete('timeR')
    playMenu.create_text(
        playMenu.winfo_width() - 16, 12,
        text=timeR, font=('Consolas', 10),
        anchor='e', fill='#ffffff', tags='timeR')

def run_timers():
    global bpfs, songCurrentlyPlaying, song, l, allSongs

    while True:
        while paused:
            sleep(.02)

        if songCurrentlyPlaying != -1 and song != allSongs[songCurrentlyPlaying]:
            song = allSongs[songCurrentlyPlaying]
            if song.lower().split('.')[-1] in ('.mp3'):
                l = MP3(song).info.length #song length in seconds
            elif song.lower().split('.')[-1] in ('.wav'):
                l = WAVE(song).info.length
            elif song.lower().split('.')[-1] in ('ogg', 'oga', 'mogg'):
                l = OggVorbis(song).info.length

        if songCurrentlyPlaying != -1:
            timer_bar()
            timer_nums()
            bpfs += .25
        sleep(.25)

Timers = threading.Thread(target=run_timers, daemon=True)
#endregion

#region play menu
playMenu = tk.Canvas(
    r, width=WID, height=116, bg='#282828',
    highlightthickness=0)
playMenu.pack(side='bottom', fill='x')

playMenu.create_line(88, 16, playMenu.winfo_width() - 88, 16, width=4, #timer bar
                    fill='#9D9D9D', capstyle='round', tags=('timer bar',))

def make_pause_button():
    playMenu.delete('pbutton')
    playMenu.create_line(playMenu.winfo_width() / 2, 72, #pause button
                    playMenu.winfo_width() / 2, 72, width=50, capstyle='round', tags=('pbutton'),
                    fill='#696969' if songCurrentlyPlaying == -1 else '#FF7F3F')
    playMenu.create_line(playMenu.winfo_width() / 2, 72,
                        playMenu.winfo_width() / 2, 72, width=42,
                        fill='#323232', capstyle='round', tags=('pbutton',))
    if paused:
        playMenu.create_text(playMenu.winfo_width() / 2 + 2, 72, text='►', font=('Arial', 19),
                            fill='#FFFFFF', tags=('pbutton',))
    else:
        playMenu.create_text(playMenu.winfo_width() / 2 + 3, 72, text='▌▌',
                            font=('Consolas', 16), fill='#FFFFFF', tags=('pbutton',))

def pause_action(i):
    global paused
    playMenu.delete('pbutton')
    if paused:
        sound.music.unpause()
        paused = False
        make_pause_button()
        playMenu.create_text(playMenu.winfo_width() / 2 + 3, 72, text='▌▌', font=('Consolas', 16),
                            fill='#FFFFFF', tags=('pbutton',))
    else:
        sound.music.pause()
        paused = True
        make_pause_button()
        playMenu.create_text(playMenu.winfo_width() / 2 + 2, 72, text='►', font=('Arial', 19),
                            fill='#FFFFFF', tags=('pbutton',))

def click_on_pm(i):
    global songCurrentlyPlaying, paused, l, bpfs
    if  87 < i.x < WID - 86 and 6 < i.y < 27:
        bpfs = ((i.x - 87) / (playMenu.winfo_width() - 176)) * l
        sound.music.set_pos(bpfs)
    elif (i.x - playMenu.winfo_width() / 2) ** 2 + (i.y - 72) ** 2 <= 625 and songCurrentlyPlaying != -1:
        pause_action(i)

def resize_PM(event): #rearrange the ui when window is resized
    global timeR, diff, bpfs

    playMenu.delete('timeR') #time on the right
    playMenu.create_text(
        playMenu.winfo_width() - 16, 12,
        text=timeR, font=('Consolas', 10),
        anchor='e', fill='#ffffff', tags='timeR')

    playMenu.delete('timer bar') #grey timer bar
    playMenu.create_line(88, 16, event.width - 88, 16, width=4,
                    fill='#9D9D9D', capstyle='round', tags=('timer bar',))
    
    diff = 88 + (bpfs / l) * (event.width - 176) #rest of timer bar
    playMenu.delete('timeline')
    playMenu.create_line(88, 16, diff, 16, width=4, fill='#FF7F3F',
                        capstyle='round', tags=('timeline',))
    playMenu.create_line(diff, 16, diff, 16, width=22, fill='#454545',
                        capstyle='round', tags=('timeline',))
    playMenu.create_line(diff, 16, diff, 16, width=10, fill='#FF7F3F',
                        capstyle='round', tags=('timeline',))
    
    make_pause_button() #pause button

make_pause_button()
r.bind('<space>', pause_action)
playMenu.bind('<Button-1>', click_on_pm)
playMenu.bind('<Configure>', resize_PM)
hook(lambda i: pause_action(i) if i.name == 'play/pause media' and i.event_type == 'down' else None)
Timers.start()
#endregion

#region side menu
findMenu = tk.Canvas(
    r, width=320, height=HEI - 166, bg='#212121',
    highlightthickness=0, name='findMenu')
findMenu.pack(side='left', fill='y')
#endregion

#region main screen
#region top bar
highMenu = tk.Canvas(
    r, width=WID - 320, height=156, bg='#2B2B2B',
    highlightthickness=0)
highMenu.pack(side='top')

def remake_HM_buttons(x, y):
    highMenu.delete('menu choice')
    highMenu.create_text(
        108, 48, text='Songs', font=('Consolas', 32, 'bold'),
        tags='menu choice', fill='#BBBBBB' if (0 <= x < 216 and y < 99) else '#FFFFFF')
    highMenu.create_text(
        324, 48, text='Albums', font=('Consolas', 32, 'bold'),
        tags='menu choice', fill='#BBBBBB' if (216 <= x < 432 and y < 99) else '#FFFFFF')
    highMenu.create_text(
        540, 48, text='Artists', font=('Consolas', 32, 'bold'),
        tags='menu choice', fill='#BBBBBB' if (432 <= x < 648 and y < 99) else '#FFFFFF')    
def click_choice_HM(i):
    global currentMenu
    currentMenu = 'HM ' + str(i.x // 216)
    #trigger a function that changes the menu based off currentMenu

def add_folder_cmd(i):
    with open(D + 'settings.json', 'r') as f:
        settings = j.load(f)
    newFolder = filedialog.askdirectory(title='Select Song Folder')
    if newFolder not in settings['songFolders'] and newFolder != '':
        settings['songFolders'].append(newFolder)
        with open(D + 'settings.json', 'w') as f:
            j.dump(settings, f, indent=4)

addFolderButton = tk.Canvas(
    highMenu, width=135, height=29, bg='#353535',
    highlightthickness=0)
addFolderButton.place(x=1420, y=37)
addFolderButton.create_text(
    8, 14, text='Add Folder', font=('Consolas', 16),
    anchor='w', fill='#FFFFFF')
addFolderButton.bind('<Button-1>', add_folder_cmd)

remake_HM_buttons(0, 100)
highMenu.bind('<Motion>', lambda i: remake_HM_buttons(i.x, i.y)) #highlight effect
highMenu.bind('<Button-1>', click_choice_HM)
#endregion

mainMenu = tk.Canvas(
    r, width=WID - 320, height=HEI - 272,
    bg='#2B2B2B', highlightthickness=0)
mainMenu.pack(side='right', fill='y')

def song_text():
    mainMenu.delete('songtext')
    for s in range(len(allSongs)):
        if s == songCurrentlyPlaying:
            mainMenu.create_rectangle(
                36, songCurrentlyPlaying * 36 + scroll + 20,
                WID - 356, songCurrentlyPlaying * 36 + scroll + 52,
                fill='#323232', width=0, tags='songtext')
            mainMenu.create_text(
                48, s * 36 + 36 + scroll,
                text='.'.join(allSongs[s].split('/')[-1].split('.')[:-1]),
                font=('Consolas', 16, 'bold'), anchor='w',
                fill='#ffffff', tags='songtext')
        else:
            if s % 2 == 0:
                mainMenu.create_rectangle(
                    36, s * 36 + scroll + 20,
                    WID - 356, s * 36 + scroll + 52,
                    fill='#2E2E2E', width=0, tags='songtext')
            mainMenu.create_text(
                48, s * 36 + 36 + scroll,
                text='.'.join(allSongs[s].split('/')[-1].split('.')[:-1]),
                font=('Consolas', 12), anchor='w',
                fill='#ffffff', tags='songtext')
    if songCurrentlyPlaying != -1:
        mainMenu.create_text(
            16, songCurrentlyPlaying * 36 + 36 + scroll, text='▶',
            font=('Consolas', 12), anchor='w',
            fill='#ffffff', tags='songtext')

def song_highlight(i):
    mainMenu.delete('highlightbox')
    if 18 < i.y - scroll < (len(allSongs) * 36 + 18):
        mainMenu.create_rectangle(
            36, ((i.y - scroll - 18) // 36) * 36 + 20 + scroll,
            WID - 356, ((i.y - scroll - 18) // 36) * 36 + 52 + scroll,
            fill='#323232', width=0, tags='highlightbox')
        mainMenu.create_text(
            48, ((i.y - scroll - 18) // 36) * 36 + 36 + scroll,
            text='.'.join(allSongs[(i.y - scroll - 18) // 36].split('/')[-1].split('.')[:-1]),
            font=('Consolas', 16, 'bold'), anchor='w',
            fill='#ffffff', tags='highlightbox')

def click_on_song(i):
    global songCurrentlyPlaying, bpfs
    mainMenu.delete('chosenbox')
    if 18 < i.y - scroll < (len(allSongs) * 36 + 18):
        sound.music.stop()
        sound.music.load(allSongs[(i.y - scroll - 18) // 36])
        sound.music.play()
        songCurrentlyPlaying = (i.y - scroll - 18) // 36
        bpfs = 0
        make_pause_button()
        song_text()

def menu_scroll(i):
    global scroll
    if i.delta < 0:
        scroll -= 27
        song_text()
        song_highlight(i)
    else:
        if scroll < 0:
            scroll += 27
            song_text()
            song_highlight(i)

song_text()
mainMenu.bind('<Motion>', song_highlight)
mainMenu.bind('<Button-1>', click_on_song)
mainMenu.bind('<MouseWheel>', menu_scroll)
#endregion

r.mainloop()
