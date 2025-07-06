import tkinter as tk
from tkinter import filedialog
from os import listdir, path
import pygame.mixer as sound #pygame needs to be installed with "pip install pygame"
from mutagen.mp3 import MP3 #mutagen needs to be installed with "pip install mutagen"
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
import time
import threading
from keyboard import hook #keyboard needs to be installed with "pip install keyboard"

#region initialise
r = tk.Tk()
r.title('Lightning Media Player')
r.state('zoomed')
r.geometry('800x600')
sound.init()

scroll = 0
songCurrentlyPlaying = -1
paused = False
bpfs = 0
song = ''
l = 1
try:
    playlists = listdir(path.join(path.expanduser('~'), 'Music', 'Playlists'))
    playlists = [f.replace('.m3u8', '') for f in playlists if f.endswith('.m3u8')]
except FileNotFoundError:
    playlists = []
playlistContent = []
for p in range(len(playlists)):
    playlistContent.append([])
    with open(path.join(path.expanduser('~'), 'Music', 'Playlists', playlists[p] + '.m3u8'), encoding='utf-8') as lis:
        playlistContent[p] = [l.replace('\n', '') for l in lis if l and l[0] not in ('#', '\n')]
#endregion

#region threads
def timer_bar():
    global l, bpfs

    n = bpfs * 4
    playMenu.delete('timeline')
    diff = 88 + (n / (l * 4)) * 1744
    playMenu.create_line(88, 16, diff, 16, width=4, fill='#FF7F3F',
                        capstyle='round', tags='timeline')
    playMenu.create_line(diff, 16, diff, 16, width=22, fill='#454545',
                        capstyle='round', tags='timeline')
    playMenu.create_line(diff, 16, diff, 16, width=10, fill='#FF7F3F',
                        capstyle='round', tags='timeline')

def timer_nums():
    global l, bpfs
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
    global bpfs, songCurrentlyPlaying, song, l

    while True:
        while paused:
            time.sleep(.02)

        if songCurrentlyPlaying != -1 and song != playlistContent[0][songCurrentlyPlaying]:
            song = playlistContent[0][songCurrentlyPlaying]
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
        time.sleep(.25)

Timers = threading.Thread(target=run_timers, daemon=True)
#endregion

#region play menu
playMenu = tk.Canvas(
    r, width=1920, height=116, bg='#282828',
    highlightthickness=0)
playMenu.pack(side='bottom')

playMenu.create_line(88, 16, 1832, 16, #timer bar
                    width=4, fill='#9D9D9D', capstyle='round')

playMenu.create_line(960, 72, 960, 72, width=50, #pause button
                    fill='#696969', capstyle='round')
def make_pause_button():
    playMenu.create_line(960, 72, 960, 72, width=42,
                        fill='#323232', capstyle='round')
    playMenu.create_text(963, 72, text='▌▌', font=('Consolas', 16),
                        fill='#FFFFFF', tags='pbutton')

def pause_action(i):
    global paused
    playMenu.delete('pbutton')
    if paused:
        playMenu.create_text(963, 72, text='▌▌', font=('Consolas', 16),
                            fill='#FFFFFF', tags='pbutton')
        sound.music.unpause()
        paused = False
    else:
        playMenu.create_text(962, 72, text='►', font=('Arial', 19),
                            fill='#FFFFFF', tags='pbutton')
        sound.music.pause()
        paused = True

def click_on_pm(i):
    global songCurrentlyPlaying, paused, l, bpfs
    if  87 < i.x < 1834 and 6 < i.y < 27:
        bpfs = ((i.x - 87) / 1747) * l
        sound.music.set_pos(bpfs)
    elif (i.x - 960) ** 2 + (i.y - 72) ** 2 <= 625 and songCurrentlyPlaying != -1:
        pause_action(i)

make_pause_button()
playMenu.bind('<Button-1>', click_on_pm)
r.bind('<space>', pause_action)
hook(lambda i: pause_action(i) if i.name == 'play/pause media' and i.event_type == 'down' else None)
Timers.start()
#endregion

#region side menu
findMenu = tk.Canvas(
    r, width=320, bg='#212121',
    highlightthickness=0, name='findMenu')
findMenu.pack(side='left', fill='y')
#endregion

#region high menu
highMenu = tk.Canvas(
    r, width=1600, height=156, bg='#2B2B2B',
    highlightthickness=0, name='highMenu')
highMenu.pack(side='top')

highMenu.create_text(48, 48, text='Music', font=('Consolas', 32, 'bold'),
                    fill='#DEDEDE', anchor='w')
addFolderButton = tk.Canvas(highMenu, width=140, height=32, bg='#383838', highlightthickness=0)
addFolderButton.place(x=1392, y=48)
addFolderButton.create_text(12, 16, text='🗀 Add Folder', font=('Consolas', 13, 'bold'),
                            fill='#DEDEDE', anchor='w')
#endregion

#region screen
mainMenu = tk.Canvas(
    r, width=1600, bg='#2B2B2B', highlightthickness=0)
mainMenu.pack(side='right', fill='y')

#song loading
def song_text():
    mainMenu.delete('songtext')
    for s in range(len(playlistContent[0])):
        if s == songCurrentlyPlaying:
            mainMenu.create_rectangle(
                36, songCurrentlyPlaying * 36 + scroll + 20,
                1564, songCurrentlyPlaying * 36 + scroll + 52,
                fill='#323232', width=0, tags='songtext')
            mainMenu.create_text(
                48, s * 36 + 36 + scroll,
                text='.'.join(playlistContent[0][s].split('\\')[-1].split('.')[:-1]),
                font=('Consolas', 16, 'bold'), anchor='w',
                fill='#ffffff', tags='songtext')
        else:
            if s % 2 == 0:
                mainMenu.create_rectangle(
                    36, s * 36 + scroll + 20,
                    1564, s * 36 + scroll + 52,
                    fill='#2E2E2E', width=0, tags='songtext')
            mainMenu.create_text(
                48, s * 36 + 36 + scroll,
                text='.'.join(playlistContent[0][s].split('\\')[-1].split('.')[:-1]),
                font=('Consolas', 12), anchor='w',
                fill='#ffffff', tags='songtext')
    if songCurrentlyPlaying != -1:
        mainMenu.create_text(
            16, songCurrentlyPlaying * 36 + 36 + scroll, text='▶',
            font=('Consolas', 12), anchor='w',
            fill='#ffffff', tags='songtext')

def song_highlight(i):
    mainMenu.delete('highlightbox')
    if 18 < i.y - scroll < (len(playlistContent[0]) * 36 + 18):
        mainMenu.create_rectangle(
            36, ((i.y - scroll - 18) // 36) * 36 + 20 + scroll,
            1564, ((i.y - scroll - 18) // 36) * 36 + 52 + scroll,
            fill='#323232', width=0, tags='highlightbox')
        mainMenu.create_text(
            48, ((i.y - scroll - 18) // 36) * 36 + 36 + scroll,
            text='.'.join(playlistContent[0][(i.y - scroll - 18) // 36].split('\\')[-1].split('.')[:-1]),
            font=('Consolas', 16, 'bold'), anchor='w',
            fill='#ffffff', tags='highlightbox')

def click_on_song(i):
    global songCurrentlyPlaying, bpfs
    mainMenu.delete('chosenbox')
    if 18 < i.y - scroll < (len(playlistContent[0]) * 36 + 18):
        sound.music.stop()
        sound.music.load(playlistContent[0][(i.y - scroll - 18) // 36])
        sound.music.play()
        songCurrentlyPlaying = (i.y - scroll - 18) // 36
        bpfs = 0
        playMenu.create_line(960, 72, 960, 72, #pause button
                    width=50, fill='#FF7F3F', capstyle='round')
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
