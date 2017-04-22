#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import system
import curses
from sys import exit

from param import menu
from file_listing import FileListing


def get_param(prompt_string):
    try:
        begin_x = 20
        begin_y = 7
        height = 5
        width = 40
        win = curses.newwin(height, width, begin_y, begin_x)
        screen.clear()
        win.border(0)
        win.addstr(2, 2, prompt_string)
        win.refresh()
        return win.getstr(2, len(prompt_string) + 5, 60)
    except:
        return ''


def sub_menu(name, datasources, mode, pending_send_file):
    x = 0
    selected = 5
    while x != ord('0'):
        screen.clear()
        screen.border(0)
        screen.addstr(2, 2, name, curses.A_BOLD)
        if selected == 4:
            screen.addstr(4, 4, '0 - Retour', curses.A_STANDOUT)
        else:
            screen.addstr(4, 4, '0 - Retour')

        x = 5
        u = 1
        for elements in datasources:
            if x == selected:
                screen.addstr(x, 4, str(u) + ' - ' + str(elements[0]),
                              curses.A_STANDOUT)
            else:
                screen.addstr(x, 4, str(u) + ' - ' + str(elements[0]))
            x = x + 1
            u = u + 1

        screen.refresh()
        x = screen.getch()
        if x == 258 or x == ord('j'):
            # Fleche vers le bas
            selected += 1
            if selected - 5 >= len(datasources):
                selected = 4
        elif x == 259 or x == ord('k'):
            # Fleche vers le haut
            selected += -1
            if selected - 4 < 0:
                selected = len(datasources) + 4
        elif x != ord('0'):
            try:
                if x == ord('\n'):
                    x = selected - 4
                    if x == 0:
                        return 0
                else:
                    x = chr(x)
                curses.endwin()
                if mode == 'SSH':
                    system('ssh {0}'.format(datasources[int(x) - 1][1]))
                else:
                    system('scp {0} {1}:'.format(pending_send_file, datasources[int(x) - 1][1]))
            except:
                pass

    return 0


x = 0
mode = 'SSH'
pending_send_file = ''
selected = 4

while x != ord('q'):
    try:
        screen = curses.initscr()
        screen.keypad(1)
        (maxY, maxX) = screen.getmaxyx()
        screen.clear()
        screen.border(0)

        screen.addstr(2, 2, 'Remote GUI', curses.A_BOLD)
        i = 4
        for elem in menu:
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
        screen.addstr(maxY - 2, 7, 'a - Autre SSH')
        screen.addch(maxY - 2, 21, curses.ACS_VLINE)

        if mode == 'SSH':
            screen.addstr(maxY - 2, 23, 'c - SCP')
        else:
            screen.addstr(maxY - 2, 23, 'c - SSH')

        screen.addch(maxY - 2, 31, curses.ACS_VLINE)
        screen.addstr(maxY - 2, 33, 'q - Quit')

        if mode == 'SCP':
            screen.addch(maxY - 2, 56, curses.ACS_VLINE)
            pending_send_file_text = (pending_send_file[:60] + '..' if len(pending_send_file) > 60 else pending_send_file)
            screen.addstr(maxY - 2, 58, 'Pending : {0}'.format(pending_send_file_text), curses.A_BOLD)

        screen.refresh()

        x = screen.getch()
        if x == 258 or x == ord('j'):
            # Fleche vers le bas
            selected += 1
            if selected - 4 >= len(menu):
                selected = 4
        elif x == 259 or x == ord('k'):
            # Fleche vers le haut
            selected += -1
            if selected - 4 < 0:
                selected = len(menu) + 2
        elif x not in [ord('a'), ord('l'), ord('q'), ord('c')]:
            # Gestion de la navigation dans les menus
            try:
                if x == ord('\n'):
                    # Touche entrer alors on converti l'indice en position
                    x = int(selected - 4)
                    key = list(menu[x].keys())[0]
                    values = menu[x][key]
                    key = list(menu[x][key].keys())[0]
                    values = values[key]
                else:
                    # Sinon on prend la valeur utilisateurs
                    try:
                        x = chr(x)
                        elem = next(item for item in menu if x in item)
                        key = list(elem[x].keys())[0]
                        values = elem[x][key]
                    except:
                        pass

                if type(values) is list:
                    # Sous menu necessaire
                    sub_menu(key, values, mode, pending_send_file)
                    curses.endwin()
                else:
                    curses.endwin()
                    if mode == 'SSH':
                        system('ssh {0}'.format(values))
                    else:
                        system('scp {0} {1}:'.format(pending_send_file,
                               values))
            except:
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

curses.endwin()
exit(0)
