import tkinter as tk
import pygame.mixer as sound
from os import listdir, path
from mutagen.mp3 import MP3
from time import sleep
import threading

#region setup
r = tk.Tk()
r.title('Lightning Media Player')
r.state('zoomed')
r.geometry('800x600')
sound.init()

scroll = 0
songCurrentlyPlaying = -1
try:
    playlists = listdir(path.expanduser('~') + '\\Music\\Playlists')
    playlists = [f.replace('.m3u8', '') for f in playlists if f.endswith('.m3u8')]
except FileNotFoundError:
    playlists = []
playlistContent = []
for p in range(len(playlists)):
    playlistContent.append([])
    with open(path.expanduser('~') + '\\Music\\Playlists\\' + playlists[p] + '.m3u8', encoding='utf-8') as lis:
        playlistContent[p] = [l.replace('\n', '') for l in lis if l and l[0] not in ('#', '\n')]
#endregion

#region play menu
playMenu = tk.Canvas(
    r, height=116, bg='#282828',
    highlightthickness=0)
playMenu.pack(side='bottom', fill='x')

def song_playing(song):
    l = MP3(song).info.length
    playMenu.delete('musiclength')
    playMenu.create_text(
        4, 4, text=':'.join(((str(int(l - (l % 3600)) // 3600).zfill(2)),
        (str(int(l - (l - l % 3600) - (l % 60)) // 60).zfill(2)),
        (str(int(l % 60)).zfill(2)))),
        font=('Consolas', 8),
        anchor='w', fill='#ffffff', tags='musiclength')
#endregion

#region side menu
findMenu = tk.Canvas(
    r, width=320, bg='#212121',
    highlightthickness=0, name='findMenu')
findMenu.pack(side='left', fill='y')
#endregion

#region screen
mainMenu = tk.Canvas(
    r, width=r.winfo_screenwidth() - 320,
    bg='#2B2B2B', highlightthickness=0)
mainMenu.pack(side='right', fill='y')

#song loading
def song_text():
    mainMenu.delete('songtext')
    for s in range(len(playlistContent[0])):
        if s == songCurrentlyPlaying:
            mainMenu.create_rectangle(
                36, songCurrentlyPlaying * 36 + scroll + 20,
                int(mainMenu.cget('width')) - 36,
                songCurrentlyPlaying * 36 + scroll + 52,
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
                    int(mainMenu.cget('width')) - 36,
                    s * 36 + scroll + 52,
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
            int(mainMenu.cget('width')) - 36,
            ((i.y - scroll - 18) // 36) * 36 + 52 + scroll,
            fill='#323232', width=0, tags='highlightbox')
        mainMenu.create_text(
            48, ((i.y - scroll - 18) // 36) * 36 + 36 + scroll,
            text='.'.join(playlistContent[0][(i.y - scroll - 18) // 36].split('\\')[-1].split('.')[:-1]),
            font=('Consolas', 16, 'bold'), anchor='w',
            fill='#ffffff', tags='highlightbox')

def click_on_song(i):
    global songCurrentlyPlaying
    mainMenu.delete('chosenbox')
    if 18 < i.y - scroll < (len(playlistContent[0]) * 36 + 18):
         sound.music.load(playlistContent[0][(i.y - scroll - 18) // 36])
        sound.music.play()
        songTimer = threading.Thread(target=song_playing, args=(playlistContent[0][(i.y - scroll - 18) // 36], ), daemon=True)
        songTimer.start()
        songCurrentlyPlaying = (i.y - scroll - 18) // 36
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