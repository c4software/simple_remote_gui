#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import system
import curses
from sys import exit

from param import menu
from file_listing import FileListing

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--title', help='Menu title', default="Remote GUI")
args = parser.parse_args()

def get_param(prompt_string):
    try:
        win = curses.newwin(5, 40, 7, 20)
        screen.clear()
        win.border(0)
        win.addstr(2, 2, prompt_string)
        win.refresh()
        return win.getstr(2, len(prompt_string) + 5, 60)
    except:
        return ''

mode = 'SSH'
pending_send_file = ''

def draw_menu(menu_name, datasource, sub_menu=False):
    global mode, pending_send_file
    selected = 4
    x = 0
    while x not in [ord("q"), 27]: # 27 is ESC_KEY
        try:
            screen = curses.initscr()
            screen.keypad(1)
            (maxY, maxX) = screen.getmaxyx()
            screen.clear()
            screen.border(0)

            screen.addstr(2, 2, menu_name, curses.A_BOLD)

            i = 4
            for elem in datasource:
                screen.addstr(i, 4, str(list(elem.keys())[0]) + ' - ' + str(list(elem[list(elem.keys())[0]].keys())[0]), (curses.A_STANDOUT if i == selected  else 0))
                i = i + 1

            # Affichage du bas de la fenetre
            for u in range(maxX):
                if u == 0:
                    screen.addch(maxY - 3, u, curses.ACS_LTEE)
                elif u == maxX - 1:
                    screen.addch(maxY - 3, u, curses.ACS_RTEE)
                else:
                    screen.addch(maxY - 3, u, curses.ACS_HLINE)

            screen.addstr(maxY - 2, 1, mode, curses.A_BOLD)
            screen.addch(maxY - 2, 5, curses.ACS_VLINE)
            screen.addstr(maxY - 2, 7, 'a - Via IP')
            screen.addch(maxY - 2, 21, curses.ACS_VLINE)

            screen.addstr(maxY - 2, 23, 'c - {0}'.format(mode))
            screen.addch(maxY - 2, 31, curses.ACS_VLINE)

            if sub_menu:
                screen.addstr(maxY - 2, 33, 'q - Retour')
            else:
                screen.addstr(maxY - 2, 33, 'q - Quit')

            if mode == 'SCP':
                screen.addch(maxY - 2, 56, curses.ACS_VLINE)
                pending_send_file_text = (pending_send_file[:60] + '..' if len(pending_send_file) > 60 else pending_send_file)
                screen.addstr(maxY - 2, 58, 'Attente : {0}'.format(pending_send_file_text), curses.A_BOLD)

            screen.refresh()

            x = screen.getch()
            if x == 258 or x == ord('j'):
                # Fleche vers le bas
                selected += 1
                if selected - 4 >= len(datasource):
                    selected = 4
            elif x == 259 or x == ord('k'):
                # Fleche vers le haut
                selected += -1
                if selected - 4 <= 0:
                    selected = 4
            elif x not in [ord('a'), ord('l'), ord('q'), ord('c'), 27]: # 27 is ESC_KEY
                # Gestion de la navigation dans les menus
                try:
                    if x == ord('\n'):
                        # Validation de la ligne active
                        # alors on converti l'indice en position
                        x = int(selected - 4)
                        key = list(datasource[x].keys())[0]
                        title = list(datasource[x][key].keys())[0]
                        values = datasource[x][key][title]

                    if type(values) is list:
                        # Sous menu necessaire
                        draw_menu(title, values, True)
                        curses.endwin()
                    else:
                        curses.endwin()
                        if mode == 'SSH':
                            system('ssh {0}'.format(values))
                        else:
                            system('scp {0} {1}:'.format(pending_send_file, values))
                except Exception as e:
                    pass
            else:
                if x == ord('a'):
                    ip = str(get_param('Adresse IP :'), 'utf-8')
                    if ip:
                        utilisateur = str(get_param('Utilisateur :'), 'utf-8')
                        curses.endwin()
                        if utilisateur:
                            system('ssh {0}@{1}'.format(utilisateur, ip))
                        else:
                            system('ssh {0}'.format(ip))
                if x == ord('c'):
                    # Passage entre les modes SSH / SCP
                    if mode == 'SSH':
                        pending_send_file = ' '.join(FileListing().run())
                        if pending_send_file:
                            mode = 'SCP'
                        screen = curses.initscr()
                        curses.raw()
                        continue
                    else:
                        mode = 'SSH'
        except KeyboardInterrupt:
            curses.endwin()
            x = ord('q')

if __name__ == "__main__":
    draw_menu(args.title, menu)
    curses.endwin()
    exit(0)
