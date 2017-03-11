'''

appka do odtwarzania plików *.mp3 (muszą być w tym samym folderze co plik programu)
powstała względnie "na szybko", z pewnością nie jest to wzór czytelnego kodu
w dodatku zaimplementowałem tu "StackOverflow Driven Development" i często nie zmieniałem nazw funkcji czy zmiennych

TO DO:
możliwość ustawienia momentu odtwarzania suwakiem
ogarnąć dlaczego przy zamknięciu okna program wypluwa błędy tkintera

'''

import pygame
from tkinter import *
import glob
import time
from mutagen.mp3 import MP3

#index używany w while(1) na końcu
#chyba z C została mi maniera do wyrzucania zmiennych o zasięgu globalnym na początek pliku
global_index = 0
time1 = '' #wystarczyło by żeby była to zmienna statyczna tick(), ale zmienne globalne jakoś bardziej mi leżą
global_audio = MP3() #obiekt do wyciągnięcia czasu trwania pliku mp3, pygame na to nie pozwala :/


#callbacki podpięte do wszystkich elementów GUI

#callback wykonywany po wybraniu pliku z playlisty
def onselect(evt):
    global global_index, playlist, global_audio

    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    pygame.mixer.music.load(value)

    global_audio = MP3(value) #potrzebne do wyciągnięcia czasu trwania pliku mp3

    pygame.mixer.music.play()

    global_index = playlist.index(value)

    pygame.mixer.music.set_endevent(pygame.USEREVENT) #po zakonczeniu odtwarzania pliku
    tick()


def tick():
    global time1, global_index

    time2 = time.strftime('%H:%M:%S')
    #update czasu odtwarzania tylko gdy minęła sekunda
    if time2 != time1:
        time1 = time2

        time_in_secs = int(pygame.mixer.music.get_pos() / 1000) #czas jaki upłynął od początku odtwarzania
        label2.config(text= "Time: " + str(int(time_in_secs / 60)) + ":" + str(time_in_secs % 60)) #ustawianie wartości label2 (czas)

        scale2.set((time_in_secs/ global_audio.info.length) * 100) #argument to wzór na procenty

    label2.after(200, tick) #coś w rodzaju przerwania co 200ms (przynajmniej ja tak to rozumiem)

#callback suwaka volume
def sel(evt):
   selection = "Volume: " + str(int(var.get()))
   label.config(text = selection) #label w którym znajduje się wartość głośności
   pygame.mixer.music.set_volume(var.get() / 100) # faktycznie ustawienie głośności (0.0-1.0)


#callbacki do pauzowania i wznawiania muzyki
def play_callback():
    pygame.mixer.music.unpause()


def pause_callback():
    pygame.mixer.music.pause()


#okno aplikacji, podpięcie callbacków, ogólna konfiguracja

#obiekty tkinter i pygame
root = Tk()
pygame.init()
pygame.mixer.init()

#kontener, rozmiar na sztywno
root.title("BiedaPlayer")
root.resizable(width=False, height=False)
root.geometry('{}x{}'.format(300, 300))

#scrollbar
scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)

#buttony do pauzowania i odtwarzania
play = Button(root, text="Play", command=play_callback)
play.pack(side="top",fill="both", expand=True)

pause = Button(root, text="Pause", command=pause_callback)
pause.pack(side="top",fill="both", expand=True)

#pierwszy label
label = Label(root)
label.pack()
label.config(text = "Volume: 100")

#suwak do regulacji głośności
var = DoubleVar()
scale = Scale( root, variable = var, command = sel, orient = HORIZONTAL, showvalue = 0 )
scale.pack(anchor=CENTER)
scale.set(100) #wartość początkowa, bez tego zaczyna się na 0

#label do czasu odtwarzania
label2 = Label(root)
label2.pack()
label2.config(text = "Time: 0")

#suwak czasu
var2 = DoubleVar()
scale2 = Scale( root, variable = var2, orient = HORIZONTAL, showvalue = 0 )
scale2.pack(anchor=CENTER)
scale2.set(0)

#playlista
listbox = Listbox(root)
listbox.pack(side="left",fill="both", expand=True)
listbox.bind('<<ListboxSelect>>', onselect)

#wyszukanie plików *.mp3 i dodanie ich do playlisty
playlist = list()
for file in glob.glob("*.mp3"):
    listbox.insert(END, file)
    playlist.append (file)


#podłączenie playlisty do scrollbara
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

#główna pętla programu
while 1:
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            if global_index < len(playlist) - 1: #trochę biedna playlista, nie chciało mi się walczyć z *.queue()
                global_index = global_index + 1
                pygame.mixer.music.load(playlist[global_index])

                global_audio = MP3(playlist[global_index]) #pobranie długości pliku

                pygame.mixer.music.play()
            else: #gdy skończy się ostatni utwór program zaczyna playlistę od początku
                global_index = 0
                pygame.mixer.music.load(playlist[global_index])
                pygame.mixer.music.play()

                global_audio = MP3(playlist[global_index])  #pobranie długości pliku
    #root.mainloop() "zawiesza" program i nie pozwala wykonać callbacka dla kliknięcia utworu na liście
    root.update_idletasks()
    root.update()