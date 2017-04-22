#!/usr/bin/env python

from os import system
import curses
from sys import exit

from param import menu
from file_listing import FileListing

def get_param(prompt_string):
     try:
          begin_x = 20 ; begin_y = 7
          height = 5 ; width = 40
          win = curses.newwin(height, width, begin_y, begin_x)
          screen.clear()
          win.border(0)
          win.addstr(2, 2, prompt_string)
          win.refresh()
          input = win.getstr(2, len(prompt_string)+5, 60)
     except:
          return ""
     return input

def sub_menu(name, datasources, mode, pending_send_file):
     x = 0
     selected = 5
     while x != ord('0'):
          screen.clear()
          screen.border(0)
          screen.addstr(2, 2, name, curses.A_BOLD)
          if selected == 4:
               screen.addstr(4, 4, "0 - Retour", curses.A_STANDOUT) 
          else:
               screen.addstr(4, 4, "0 - Retour")

          x = 5
          u = 1
          for elements in datasources:
               if x == selected:
                    screen.addstr(x, 4, str(u)+" - "+str(elements[0]), curses.A_STANDOUT)
               else:
                    screen.addstr(x, 4, str(u)+" - "+str(elements[0]))
               x = x+1
               u = u+1

          screen.refresh()            
          x =  screen.getch()
          if x == 258 or x == ord('j'):
               # Fleche vers le bas
               selected += 1
               if selected-5 >= len(datasources):
                    selected = 4
          elif x == 259 or x == ord('k'):
               # Fleche vers le haut
               selected += - 1
               if selected-4 < 0:
                    selected = len(datasources)+4
          elif x != ord('0'):
               try:
                    if x == ord('\n'):
                         x = selected-4
                         if x == 0:
                              return 0
                    else:
                         x = chr(x)
                    curses.endwin()
                    if mode == "SSH":
                         system("ssh "+datasources[int(x)-1][1])
                    else:
                         system("scp "+pending_send_file+" "+datasources[int(x)-1][1]+":")

               except:
                   pass

     return 0

x = 0
mode = "SSH"
pending_send_file = ""
selected = 3

while x != ord('q'):
     try:
          screen = curses.initscr()
          screen.keypad(1) 
          maxY, maxX = screen.getmaxyx()
          code = 255 # code de sorti de l'appli
          screen.clear()
          screen.border(0)

          screen.addstr(2, 2, "Remote GUI", curses.A_BOLD)
          i = 3
          for elem in menu:
               if i == selected:
                    screen.addstr(i, 4, str(list(elem.keys())[0])+" - "+str(list(elem[list(elem.keys())[0]].keys())[0]), curses.A_STANDOUT)
               else:
                    screen.addstr(i, 4, str(list(elem.keys())[0])+" - "+str(list(elem[list(elem.keys())[0]].keys())[0]))
               i = i+1

          # Affichage du bas de la fenetre
          for u in range(maxX):
               if u == 0:
                    screen.addch(maxY-3, u, curses.ACS_LTEE)
               elif u == maxX-1:
                    screen.addch(maxY-3, u, curses.ACS_RTEE)
               else:
                    screen.addch(maxY-3, u, curses.ACS_HLINE)

          screen.addstr(maxY-2, 1, mode,curses.A_BOLD)
          screen.addch(maxY-2, 5, curses.ACS_VLINE)
          screen.addstr(maxY-2, 7, "a - Autre SSH")
          screen.addch(maxY-2, 21, curses.ACS_VLINE)
          if mode == "SSH":
               screen.addstr(maxY-2, 23, "c - SCP")
          else:
               screen.addstr(maxY-2, 23, "c - SSH")
          screen.addch(maxY-2, 31, curses.ACS_VLINE)
          screen.addstr(maxY-2, 33, "l - Logout")
          screen.addch(maxY-2, 44, curses.ACS_VLINE)
          screen.addstr(maxY-2, 46, "q - Shell")

          if mode == "SCP":
               screen.addch(maxY-2, 56, curses.ACS_VLINE)
               if len(pending_send_file) > maxX-60:
                    screen.addstr(maxY-2, 58, "Pending : "+(pending_send_file[:maxX-60] + '..'), curses.A_BOLD)
               else:
                    screen.addstr(maxY-2, 58, "Pending : "+pending_send_file, curses.A_BOLD)
          screen.refresh()

          x =  screen.getch()
          if x == 258 or x == ord('j'):
               # Fleche vers le bas
               selected += 1
               if selected-3 >= len(menu):
                    selected = 3
          elif x == 259 or x == ord('k'):
               # Fleche vers le haut
               selected += - 1
               if selected-3 < 0:
                    selected = len(menu)+2
          elif x != ord('a') and x != ord('l') and x != ord('q') and x != ord('c'):
               try:
                    if x == ord('\n'):
                         # Si touche entrer alors on converti l'indice en position
                         x = int(selected-3)
                         key = list(menu[x].keys())[0]
                         values = menu[x][key]
                         key = list(menu[x][key].keys())[0]
                         values = values[key]
                    else:
                         # Sinon on prend la valeur utilisateurs
                         try:
                              x = chr(x)
                              elem = next((item for item in menu if x in item))
                              key = list(elem[x].keys())[0]
                              values = elem[x][key]
                         except:
                              pass
                   
                    if type(values) is list:
                         # Sous menu necessaire
                         sub_menu(key,values, mode, pending_send_file)
                         curses.endwin()
                    else:
                         curses.endwin()
                         if mode == "SSH":
                              system("ssh "+values)     
                         else:
                              system("scp "+pending_send_file+" "+values+":")
               except:
                    pass
          else:
               if x == ord('a'):   
                    ip = get_param("Adresse IP :")
                    if ip is not "":
                         utilisateur = get_param("Utilisateur :")
                         curses.endwin()
                         if utilisateur is not "":
                              system("ssh "+utilisateur+"@"+ip)
                         else:
                              system("ssh "+ip)
               if x == ord('c'):
                    if mode == "SSH":
                         mode = "SCP"
                         pending_send_file = " ".join(FileListing().run())
                         screen = curses.initscr()
                         curses.raw()
                    else:
                         mode = "SSH"
               if x == ord('l'):
                    # Sortie OK alors ==> Logout (si lance avec && logout
                    curses.endwin()
                    code = 0
                    x = ord('q')
     except KeyboardInterrupt:
          curses.endwin()
          code = 0
          x = ord('q')
curses.endwin()
exit(code)
