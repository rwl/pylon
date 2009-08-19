__author__ = 'Richard W. Lincoln, r.w.lincoln@gmail.com'

import os
import sys
import logging

from Tkinter import *

from pylon.readwrite import MATPOWERReader, ReSTWriter

from pylon import \
    Network, DCPF, NewtonRaphson, FastDecoupled, DCOPF, ACOPF, UDOPF

logger = logging.getLogger(__name__)

CASE_6_WW = os.path.dirname(__file__) + "/test/data/case6ww.m"
CASE_30   = os.path.dirname(__file__) + "/test/data/case30pwl.m"


class PylonTk:
    def __init__(self, master):
        self.n = Network()

        self.root = master

        self.frame = Frame(master)
        self.frame.pack(expand=YES, fill=BOTH)

        self._init_menubar()
        self._init_buttonbar()
        self._init_logframe()


    def _init_menubar(self):
        menu = Menu(self.root)
        self.root.config(menu=menu)

        filemenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Case", menu=filemenu)
        presetmenu = Menu(filemenu, tearoff=False)
        filemenu.add_cascade(label='Preset', menu=presetmenu)
        presetmenu.add_command(label="6 bus", command=self.on_6_bus)
        presetmenu.add_command(label="30 bus", command=self.on_30_bus)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_exit,
                             accelerator="Alt-X")
        self.root.bind('<Alt-x>', self.on_exit)

        pfmenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Power Flow", menu=pfmenu)
        pfmenu.add_command(label="DC", command=self.on_dcpf)
        pfmenu.add_command(label="Newton-Raphson", command=self.on_newton)
        pfmenu.add_command(label="Fast Decoupled", command=self.on_fd)

        opfmenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="OPF", menu=opfmenu)
        opfmenu.add_command(label="DC", command=self.on_dcopf)
        opfmenu.add_command(label="AC", command=self.on_acopf)
        opfmenu.add_command(label="DC (UD)", command=self.on_duopf)
        opfmenu.add_command(label="AC (UD)", command=self.on_uopf)


    def _init_buttonbar(self):
        buttonbar = Frame(self.frame)
        buttonbar.pack(side=LEFT, fill=Y)
        Button(buttonbar, text="Summary",
               command=self.on_summary).pack(fill=X)
        Button(buttonbar, text="Bus Data",
               command=self.on_bus_info).pack(fill=X)
        Button(buttonbar, text="Branch Data",
               command=self.on_branch_info).pack(fill=X)
        Button(buttonbar, text="Generator Data",
               command=self.on_generator_info).pack(fill=X)
        Button(buttonbar, text="Load Data",
               command=self.on_load_info).pack(fill=X)


    def _init_logframe(self):
        self.ui_log = UILog(self.frame)

#        sys.stdout = self.ui_log
#        sys.stderr = self.ui_log
        logging.basicConfig(stream=self.ui_log, level=logging.DEBUG,
                            format="%(levelname)s: %(message)s")

        self.ui_log.level.set(logger.getEffectiveLevel())


    def on_summary(self):
        writer = ReSTWriter()
        writer.write_how_many(self.n, self.ui_log)
        writer.write_how_much(self.n, self.ui_log)
        writer.write_min_max(self.n, self.ui_log)
        del writer

    def on_bus_info(self):
        ReSTWriter().write_bus_data(self.n, self.ui_log)


    def on_branch_info(self):
        ReSTWriter().write_branch_data(self.n, self.ui_log)


    def on_generator_info(self):
        ReSTWriter().write_generator_data(self.n, self.ui_log)


    def on_load_info(self):
        ReSTWriter().write_load_data(self.n, self.ui_log)


    def on_6_bus(self):
        self.n = MATPOWERReader().read(CASE_6_WW)


    def on_30_bus(self):
        self.n = MATPOWERReader().read(CASE_30)


    def on_dcpf(self):
        DCPF().solve(self.n)


    def on_newton(self):
        NewtonRaphson().solve(self.n)


    def on_fd(self):
        FastDecoupled().solve(self.n)


    def on_dcopf(self):
        DCOPF().solve(self.n)


    def on_acopf(self):
        ACOPF().solve(self.n)


    def on_duopf(self):
        UDOPF(dc=True).solve(self.n)


    def on_uopf(self):
        UDOPF(dc=False).solve(self.n)


    def on_exit(self, event=None):
        self.root.destroy()
#        sys.exit(0)


class UILog:
    def __init__(self, master):
        logframe = Frame(master)
        logframe.pack(expand=YES, fill=BOTH)

        yscrollbar = Scrollbar(logframe)
        xscrollbar = Scrollbar(logframe, orient=HORIZONTAL)

        self.log = Text(logframe, background="white", wrap=NONE,
                        xscrollcommand=xscrollbar.set,
                        yscrollcommand=yscrollbar.set)

        yscrollbar.pack(side=RIGHT, fill=Y)
        xscrollbar.pack(side=BOTTOM, fill=X)

        self.log.pack(expand=YES, fill=BOTH)

        yscrollbar.config(command=self.log.yview)
        xscrollbar.config(command=self.log.xview)

        loglevels = Frame(master)
        loglevels.pack(fill=X)

        level = self.level = IntVar()

        debug = Radiobutton(loglevels, text="DEBUG", variable=level,
                            value=logging.DEBUG, command=self.on_level)
        debug.pack(side=LEFT, anchor=E)
        info = Radiobutton(loglevels, text="INFO", variable=level,
                           value=logging.INFO, command=self.on_level)
        info.pack(side=LEFT, anchor=E)
        warn = Radiobutton(loglevels, text="WARN", variable=level,
                           value=logging.WARNING, command=self.on_level)
        warn.pack(side=LEFT, anchor=E)
        error = Radiobutton(loglevels, text="ERROR", variable=level,
                            value=logging.ERROR, command=self.on_level)
        error.pack(side=LEFT, anchor=E)

        level.set(logger.getEffectiveLevel())


    def write(self, buf):
        self.log.insert(END, buf)
        self.log.see(END)


    def flush(self):
        pass


    def on_level(self):
#        logger.setLevel(self.level.get())

#        print logging.getLogger(__name__).getEffectiveLevel(), self.level.get()
        logging.basicConfig(stream=self, level=self.level.get(),
                            format="%(levelname)s: %(message)s")
#        print logging.getLogger(__name__).getEffectiveLevel(), self.level.get()


def main():
    root = Tk()
    root.title('PYLON')
    app = PylonTk(root)
    root.mainloop()


if __name__ == "__main__":
#    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
#                        format="%(levelname)s: %(message)s")

#    logger.addHandler(logging.StreamHandler(sys.stdout))
#    logger.setLevel(logging.DEBUG)

    main()
