#region initialise
import tkinter as tk
from tkinter import filedialog
import pygame.mixer as sound
from os import walk
from mutagen import File #mutagen needs to be installed with "pip install mutagen"
from time import sleep
import threading
from keyboard import hook #keyboard needs to be installed with "pip install keyboard"
import json as j

r = tk.Tk()
r.title('Lightning Media Player')
r.state('zoomed')
r.geometry('800x600')
r.minsize(320, 232)
sound.init()

WID = 1920
HEI = 1080
D = __file__.replace(__file__.split('\\')[-1], '')
paused = True
bpfs = 0
diff = 0
timeR = ''
song = ''
l = 1

allSongs = []
def dir_to_playlist():
    global allSongs
    allSongs = []
    with open(D + 'settings.json', 'r') as f:
        playlists = j.load(f)['songFolders']
    for i in playlists:
        for root, dirs, files in walk(i):
            files = [f.replace(f, root + '/' + f) for f in files]
            allSongs.extend(files)
    allSongs = [i for i in allSongs if i.split('.')[-1] in ('mp3', 'wav', 'ogg', 'oga', 'mogg')]
dir_to_playlist()

with open(D + 'settings.json', 'r') as f:
    settings = j.load(f)
    volume = settings['volume']
    scroll = settings['scroll']
    songCurrentlyPlaying = settings['SCP']
sound.music.set_volume(volume / 100)
if songCurrentlyPlaying != -1:
    sound.music.load(allSongs[songCurrentlyPlaying])

#endregion

#region threads
def timer_bar():
    global l, bpfs, diff

    n = bpfs * 10
    playMenu.delete('timeline')
    diff = 88 + (n / (l * 10)) * (playMenu.winfo_width() - 176)
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
        playMenu.winfo_width() - 16, 12, text=timeR, font=('Consolas', 10),
        anchor='e', fill='#ffffff', tags='timeR')

def run_timers():
    global bpfs, songCurrentlyPlaying, song, l, allSongs
    while True:
        if bpfs >= l:
            bpfs = 0
            songCurrentlyPlaying += 1
            sound.music.load(allSongs[songCurrentlyPlaying])
            sound.music.play()
            song_title()
            song_highlight(mainMenu.winfo_pointery() - mainMenu.winfo_rooty())

        if songCurrentlyPlaying != -1 and song != allSongs[songCurrentlyPlaying]:
            l = File(allSongs[songCurrentlyPlaying]).info.length

        if songCurrentlyPlaying != -1:
            timer_bar()
            timer_nums()
            bpfs += .1
        while paused:
            sleep(.1)
        sleep(.1)

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
    playMenu.create_line(playMenu.winfo_width() / 2, 72,
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
    global paused, songCurrentlyPlaying
    if songCurrentlyPlaying != -1:
        playMenu.delete('pbutton')
        if paused:
            if sound.music.get_busy(): sound.music.unpause()
            else: sound.music.play()
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

volumeOpenFlag = False
def show_volume_changes():
    playMenu.delete('volume part')
    vr = int(volume / 100 * 177) + playMenu.winfo_width() - 243
    playMenu.create_line(playMenu.winfo_width() - 243, 31, vr, 31, width=4, fill='#FF7F3F', #line
                capstyle='round', tags=('volume part',))
    
    playMenu.create_line(vr, 31, vr, 31, width=22, fill='#454545', #dot
                capstyle='round', tags=('volume part',))
    playMenu.create_line(vr, 31, vr, 31, width=10, fill='#FF7F3F',
                capstyle='round', tags=('volume part',))
    
    playMenu.create_text( #volume text
        playMenu.winfo_width() - 40, 31, text=volume, font=('Consolas', 12),
        fill='#FFFFFF', tags=('volume part',))
    if volume == 0: mic = '🔇'
    elif 0 < volume <= 30: mic = '🔈'
    elif 30 < volume <= 70: mic = '🔉'
    elif 70 < volume: mic = '🔊'
    playMenu.create_text(
        playMenu.winfo_width() - 279, 31, text=mic, font=('Consolas', 16),
        fill='#FFFFFF', anchor='w', tags=('volume part',))
    sound.music.set_volume(volume / 100)

def make_volume():
    playMenu.create_rectangle(
        playMenu.winfo_width() - 295, 8, playMenu.winfo_width() - 13,
        58, fill='#303030', outline='#696969', tags=('volume menu',))
    playMenu.create_line(
        playMenu.winfo_width() - 243, 31, playMenu.winfo_width() - 66, 31,
        fill='#9D9D9D', width=4, capstyle='round', tags=('volume menu',))
    show_volume_changes()

def click_on_PM(i):
    global l, bpfs, volumeOpenFlag, volume
    if  (87 < i.x < playMenu.winfo_width() - 296 or\
        ((not playMenu.winfo_width() - 295 < i.x < playMenu.winfo_width() - 86) if volumeOpenFlag else True)) and 6 < i.y < 27: #timer bar
        if sound.music.get_busy():
            bpfs = ((i.x - 87) / (playMenu.winfo_width() - 176)) * l
            sound.music.set_pos(bpfs)
    elif (i.x - playMenu.winfo_width() / 2) ** 2 + (i.y - 72) ** 2 <= 625: #pause button
        pause_action(i)
    elif playMenu.winfo_width() - 173 < i.x < playMenu.winfo_width() - 142 and 58 < i.y < 90: #volume toggle
        if volumeOpenFlag:
            playMenu.delete('volume menu', 'volume part')
            volumeOpenFlag = False
        else:
            make_volume()
            volumeOpenFlag = True
    elif playMenu.winfo_width() - 243 < i.x < playMenu.winfo_width() - 58 and 20 < i.y < 42:
        volume = int((i.x - (playMenu.winfo_width() - 243)) / 1.77)
        if volume > 100: volume = 100
        elif volume < 0: volume = 0
        make_volume()

def scroll_on_PM(i):
    global volumeOpenFlag, volume
    if volumeOpenFlag:
        if playMenu.winfo_width() - 295 < i.x < playMenu.winfo_width() - 86 and 8 < i.y < 58:
            if i.delta > 0: volume += 2
            else: volume -= 2
            if volume > 100: volume = 100
            elif volume < 0: volume = 0
        make_volume()

def resize_PM(event): #rearrange the ui when window is resized
    global timeR, diff, bpfs, volumeOpenFlag

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
    
    playMenu.delete('volume main', 'volume menu', 'volume part')
    playMenu.create_text(playMenu.winfo_width() - 165, 72, #volume control
                    text='🔊', font=('Consolas', 16),
                    fill='#FFFFFF', anchor='w', tags=('volume main',))
    if volumeOpenFlag:
        make_volume()
    
    make_pause_button() #pause button

r.bind('<space>', pause_action)
playMenu.bind('<Button-1>', click_on_PM)
playMenu.bind('<MouseWheel>', scroll_on_PM)
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

foldersShownFlag = False
def show_folder_cmd(i):
    global foldersShownFlag
    if foldersShownFlag:
        highMenu.delete('showfolderbox')
        foldersShownFlag = False
    else:
        highMenu.create_rectangle(
            1300, 66, 1565, 155, fill='#353535',
            outline='#696969', tags=('showfolderbox',))
        highMenu.create_text(
            1301, 75, text='Folders:', font=('Consolas', 10),
            anchor='w', fill='#FFFFFF', tags=('showfolderbox',))
        with open(D + 'settings.json', 'r') as f:
            playlists = j.load(f)['songFolders']
            for s in range(len(playlists)):
                highMenu.create_text(
                    1301, 93 + s * 18, text=(playlists[s]), font=('Consolas', 10),
                    anchor='w', fill='#FFFFFF', tags=('showfolderbox',))
        foldersShownFlag = True

showFoldersButton = tk.Canvas(
    highMenu, width=29, height=29, bg='#353535',
    highlightthickness=1, highlightbackground='#696969')
showFoldersButton.place(x=1535, y=36)
showFoldersButton.create_text(
    15, 5, text='⌄', font=('Consolas', 20), fill='#FFFFFF')
showFoldersButton.bind('<Button-1>', show_folder_cmd)

def add_folder_cmd(i):
    with open(D + 'settings.json', 'r') as f:
        settings = j.load(f)
    newFolder = filedialog.askdirectory(title='Select Song Folder')
    if newFolder != '':
        if newFolder in settings['songFolders']:
            settings['songFolders'].remove(newFolder)
            with open(D + 'settings.json', 'w') as f:
                j.dump(settings, f, indent=4)
        else:
            settings['songFolders'].append(newFolder)
            with open(D + 'settings.json', 'w') as f:
                j.dump(settings, f, indent=4)
    dir_to_playlist()
    song_title()
    show_folder_cmd(i)
    show_folder_cmd(i)

addFolderButton = tk.Canvas(
    highMenu, width=235, height=29, bg='#353535',
    highlightthickness=0)
addFolderButton.place(x=1300, y=37)
addFolderButton.create_text(
    118, 14, text='Add/Remove Folder',
    font=('Consolas', 16), fill='#FFFFFF')
addFolderButton.bind('<Button-1>', add_folder_cmd)

remake_HM_buttons(0, 100)
highMenu.bind('<Motion>', lambda i: remake_HM_buttons(i.x, i.y)) #highlight effect
highMenu.bind('<Button-1>', click_choice_HM)
#endregion

#region main menu
mainMenu = tk.Canvas(
    r, width=WID - 320, height=HEI - 272,
    bg='#2B2B2B', highlightthickness=0)
mainMenu.pack(side='right', fill='y')

def song_title():
    mainMenu.delete('songtext')
    for s in range(max(-scroll // 36 - 1, 0), min(len(allSongs), (HEI - 272 - scroll) // 36)): #only render seen songs
        if s == songCurrentlyPlaying:
            mainMenu.create_rectangle(
                36, songCurrentlyPlaying * 36 + scroll + 20,
                mainMenu.winfo_width() - 36, songCurrentlyPlaying * 36 + scroll + 52,
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
                    mainMenu.winfo_width() - 36, s * 36 + scroll + 52,
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
    try: pos = i.y
    except AttributeError: pos = i
    mainMenu.delete('highlightbox')
    if 18 < pos - scroll < (len(allSongs) * 36 + 18):
        mainMenu.create_rectangle(
            36, ((pos - scroll - 18) // 36) * 36 + 20 + scroll,
            mainMenu.winfo_width() - 36, ((pos - scroll - 18) // 36) * 36 + 52 + scroll,
            fill='#323232', width=0, tags='highlightbox')
        mainMenu.create_text(
            48, ((pos - scroll - 18) // 36) * 36 + 36 + scroll,
            text='.'.join(allSongs[(pos - scroll - 18) // 36].split('/')[-1].split('.')[:-1]),
            font=('Consolas', 16, 'bold'), anchor='w',
            fill='#ffffff', tags='highlightbox')

def click_on_song(i):
    global songCurrentlyPlaying, bpfs, paused
    mainMenu.delete('chosenbox')
    if 18 < i.y - scroll < (len(allSongs) * 36 + 18):
        sound.music.stop()
        sound.music.load(allSongs[(i.y - scroll - 18) // 36])
        sound.music.play()
        paused = False
        songCurrentlyPlaying = (i.y - scroll - 18) // 36
        bpfs = 0
        make_pause_button()
        song_title()

def menu_scroll(i):
    global scroll
    if i.delta < 0:
        scroll -= 27
        song_title()
        song_highlight(i)
    else:
        if scroll < 0:
            scroll += 27
            song_title()
            song_highlight(i)

def resize_MM(event):
    song_title()
    mainMenu.delete('highlightbox')

mainMenu.bind('<Motion>', song_highlight)
mainMenu.bind('<Button-1>', click_on_song)
mainMenu.bind('<MouseWheel>', menu_scroll)
mainMenu.bind('<Configure>', resize_MM)
#endregion

def on_close():
    with open(D + 'settings.json', 'r') as f:
        settings = j.load(f)
    
    settings['volume'] = volume
    settings['scroll'] = scroll
    settings['SCP'] = songCurrentlyPlaying

    with open(D + 'settings.json', 'w') as f:
        j.dump(settings, f, indent=4)
    r.destroy()
r.protocol('WM_DELETE_WINDOW', on_close)

r.mainloop()
