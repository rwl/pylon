import os
import sys
import logging

from Tkinter import *

from pylon.readwrite import MATPOWERReader
from pylon import DCPF, NewtonPFRoutine, DCOPF, ACOPF

CASE_6_WW = os.path.dirname(__file__) + "/test/data/case6ww.m"
CASE_30   = os.path.dirname(__file__) + "/test/data/case30pwl.m"

class PylonTk:
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        menu = Menu(master)
        master.config(menu=menu)

        filemenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="File", menu=filemenu)
        presetmenu = Menu(filemenu, tearoff=False)
        filemenu.add_cascade(label='Preset', menu=presetmenu)
        presetmenu.add_command(label="6 bus", command=self.on_6_bus)
        presetmenu.add_command(label="30 bus", command=self.on_30_bus)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_exit)

        pfmenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="PF", menu=pfmenu)
        pfmenu.add_command(label="DC", command=self.on_dcpf)
        pfmenu.add_command(label="AC", command=self.on_acpf)
#        pfmenu.add_command(label="Gauss", command=self.on_gauss)

        opfmenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="OPF", menu=opfmenu)
        opfmenu.add_command(label="DC", command=self.on_dcopf)
        opfmenu.add_command(label="AC", command=self.on_acopf)

        helpmenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About", command=self.on_about)


        self.button = Button(frame, text="Push", command=self.on_click)
        self.button.pack(side=LEFT)

        self.ui_log = UILog(frame)
        sys.stdout = self.ui_log
#        sys.stderr = self.ui_log
        self.ui_log.widget.pack(expand=YES, fill=BOTH)

    def on_click(self):
        print "PYLON"

    def on_6_bus(self):
        self.n = MATPOWERReader().read(CASE_6_WW)

    def on_30_bus(self):
        self.n = MATPOWERReader().read(CASE_30)

    def on_dcpf(self):
        DCPF().solve(self.n)

    def on_acpf(self):
        ACPF().solve(self.n)

    def on_dcopf(self):
        DCOPF().solve(self.n)

    def on_acopf(self):
        ACOPF().solve(self.n)

    def on_exit(self):
        sys.exit(0)

    def on_about(self):
#        frame = Frame(self.frame, width=200, height=200, bg='orange')
#        title = Label(frame, text='PYLON')
#        title.pack()
#        b = Button(frame, text="OK", command=frame.destroy)
#        b.pack(pady=5)
        pass

class UILog:
    def __init__(self, master):
        self.widget = Text(master)

    def write(self, buf):
        self.widget.insert(END, buf)#"%s%s" % (buf, self.widget.text))
#        self.widget.selected_line = -1

def main():
    root = Tk()
    root.title('PYLON')
    app = PylonTk(root)
    print "PYLON"
    root.mainloop()

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(levelname)s: %(message)s")
    main()
