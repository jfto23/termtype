import curses
import time
import random
import os

def main(stdscr):

    curses.start_color()
    curses.use_default_colors()
    
    # colors
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_MAGENTA, -1)
    curses.init_pair(4, curses.COLOR_WHITE, -1)

    max_y, max_x = stdscr.getmaxyx()

    # text box
    text_win = curses.newwin(4,50,int(max_y/2)-5,int((max_x/2)-(50/2)))
    text_win_y, text_win_x = text_win.getmaxyx()

    # input box
    input_win = curses.newwin(1, 30, int(max_y/2), int((max_x/2)-(30/2)))
    stdscr.refresh()
    input_win.refresh()

    curses.curs_set(0)
    
    running = menu(stdscr) 
    while running:
        # add text
        text_win.clear()
        text_win.refresh()
        s = randomSentence()
        addstr_wordwrap(text_win,s,text_win_x, text_win_y, curses.color_pair(3))
        text_win.refresh()
        num_lines=count_lines(text_win)
        stdscr.refresh()
        text_win.refresh()
        # game loop. Initialize start variables
        typing = True
        word_count = 0
        line_counter = 0
        end = 0
        # timer
        started = False;
        while typing:
            c = input_win.getch()
            if not started:
                start_t = time.time()
                started = True

            text_list = text_win.instr(line_counter,0,300).split()
            #backspace
            if c == 127 or c == curses.KEY_BACKSPACE:
                input_win.addstr("\b \b") 
            #ctrl + backspace
            elif c == 8:
                input_win.clear()
                input_win.refresh()
            #ctrl + r (quick restart)
            elif c == 18:
                typing = False
                end = 114
            #ctrl + i (quick exit) 
            elif c == 9:
                typing = False
                end = 113
            #restrict possible characters
            elif c >= 32 and c <= 126:
                try:
                    input_win.addch(c)
                except:
                    pass
            

            #Read input_box and re-position cursor
            current_y, current_x = input_win.getyx() 
            input_content = input_win.instr(0,0,100).decode('utf-8').strip()
            input_win.move(current_y,current_x)
            
            # win condition. Avoids having to press space at the end
            if input_content == text_list[word_count].decode('utf-8') and \
            line_counter == num_lines-1 and word_count == len(text_list)-1:
                is_substring(text_win, text_list, word_count, line_counter,input_content, True)
                text_win.refresh()
                break

            # checks if input is substring
            is_substring(text_win,text_list,word_count,line_counter,input_content,False)

            # Word match verification
            if c == 32 and input_content == text_list[word_count].decode('utf-8'):
                input_win.clear()
                input_win.refresh()
                is_substring(text_win, text_list, word_count, line_counter,input_content, True)
                word_count+=1
                try:
                    t = text_list[word_count]
                except IndexError:
                    line_counter += 1
                    word_count = 0
        
        input_win.clear()
        input_win.refresh()
        typing = False
        
        end_t = time.time()
        gross_wpm = int((len(s)/5)/((end_t-start_t)/60))
        input_win.addstr(str(gross_wpm)+" wpm")
        input_win.refresh()
        stdscr.addstr("Press <r> to replay, <q> to quit.")
        stdscr.refresh()

        while True:
            if end == 113:
                running = False
                break
            elif end == 114:
                stdscr.clear()
                stdscr.refresh()
                input_win.clear()
                input_win.refresh()
                break
            end = stdscr.getch() 
        

def menu(stdscr):
    '''Displays menu when the program is started.'''
    max_y, max_x = stdscr.getmaxyx()
    stdscr.addstr(int(max_y/2)-5, int(max_x/2)-5,"termtype")
    stdscr.addstr(int(max_y/2)-2, int(max_x/2)-18,"Press <enter> to start, <q> to quit.")
    while True:
        key = stdscr.getch()
        if key == 10:
            stdscr.clear()
            stdscr.refresh()
            return True
        if key == 113:
            stdscr.clear()
            stdscr.refresh()
            return False

def is_substring(text_win, text_list, word_count, line_counter,input_content, finished):
    '''Colors appropriately the text. The three possibilites are:
    -Word has been correctly written and the user pressed space
    -Word has no typo up to now
    -Word has a typo'''
    stringlist = [e.decode('utf-8') for e in text_list[0:word_count]]
    upto_previous = " ".join(stringlist)

    stringlist2 = [e.decode('utf-8') for e in text_list[0:word_count+1]]
    upto_current = " ".join(stringlist2) 
    
    if finished:
        text_win.addstr(line_counter,0,upto_current,curses.color_pair(2))
        text_win.refresh()
        return

    if stringlist2[word_count].startswith(input_content):
        text_win.addstr(line_counter,0,upto_current,curses.color_pair(3))
        text_win.addstr(line_counter,0,upto_previous,curses.color_pair(2))
        text_win.refresh()

    else:
        text_win.addstr(line_counter,0,upto_current,curses.color_pair(1))
        text_win.addstr(line_counter,0,upto_previous,curses.color_pair(2))
        text_win.refresh()

def addstr_wordwrap(window, s, width, height,mode):
    '''Modifies the addstr function of curses so text is left-justified.
    Inspired by: http://colinmorris.github.io/blog/word-wrap-in-pythons-curses-library'''
    y,x=window.getyx()

    if len(s) + x <= width:
        window.addstr(s,mode)

    else:
        for word in s.split():
            if len(word+" ") + x <= width:
                window.addstr(word+" ",mode)
            else:
                window.addstr(y+1,0,word+" ",mode)
            y,x=window.getyx()

def randomSentence():
    '''Returns a random line from the file 'sentences.txt'. The file must be in the
    same directory as the program'''
    script_dir = os.path.dirname(__file__)
    abs_path = os.path.join(script_dir, "sentences.txt")
    sentences = open(abs_path) 
    lines = sentences.readlines()
    return random.choice(lines)


def count_lines(text_win):
    '''Returns the number of lines once the text has been added. Returns either 3
    or 4'''
    if text_win.instr(3,0,1).decode('utf-8') == " ":
        return 3
    return 4

if __name__ == "__main__":
    curses.wrapper(main)
