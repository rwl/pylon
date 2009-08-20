__author__ = 'Richard W. Lincoln, r.w.lincoln@gmail.com'

import os
import sys
import logging

from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
import tkSimpleDialog

from pylon.readwrite import \
    MATPOWERReader, MATPOWERWriter, ReSTWriter, PSSEReader, PSATReader, \
    CSVWriter, ExcelWriter, DotWriter

from pylon import \
    Network, DCPF, NewtonRaphson, FastDecoupled, DCOPF, ACOPF, UDOPF

logger = logging.getLogger('pylon')

CASE_6_WW = os.path.dirname(__file__) + "/test/data/case6ww.m"
CASE_30   = os.path.dirname(__file__) + "/test/data/case30pwl.m"


class PylonTk(object):
    def __init__(self, master):
        self.root = master

        self.frame = Frame(master)
        self.frame.pack(expand=YES, fill=BOTH)

        self._init_menubar()
        self._init_buttonbar()
        self._init_logframe()

        self.on_new()


    def _init_menubar(self):
        menu = Menu(self.root)
        self.root.config(menu=menu)

        filemenu = Menu(menu, tearoff=False)
        filemenu.add_command(label="New", command=self.on_new)
        filemenu.add_separator()
        filemenu.add_command(label="Open...", command=self.on_open)
        menu.add_cascade(label="Case", menu=filemenu)

        presetmenu = Menu(filemenu, tearoff=False)
        filemenu.add_cascade(label='Preset', menu=presetmenu)
        presetmenu.add_command(label="6 bus", command=self.on_6_bus)
        presetmenu.add_command(label="30 bus", command=self.on_30_bus)
        filemenu.add_separator()

        filemenu.add_command(label="Save As...", command=self.on_save_as)
        filemenu.add_separator()

        importmenu = Menu(filemenu, tearoff=False)
        filemenu.add_cascade(label='Import', menu=importmenu)
        importmenu.add_command(label="Pickle", command=self.on_unpickle)
        importmenu.add_command(label="PSS/E", command=self.on_psse)
        importmenu.add_command(label="PSAT", command=self.on_psat)

        exportmenu = Menu(filemenu, tearoff=False)
        filemenu.add_cascade(label='Export', menu=exportmenu)
        exportmenu.add_command(label="Pickle", command=self.on_pickle)
        exportmenu.add_command(label="Excel", command=self.on_excel)
        exportmenu.add_command(label="CSV", command=self.on_csv)
        exportmenu.add_command(label="ReST", command=self.on_rest)
        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=self.on_exit,
                             accelerator="Alt-X")
        self.root.bind('<Alt-x>', self.on_exit)


        viewmenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Graph", menu=viewmenu)
        viewmenu.add_command(label="Graph", command=self.on_graph)

        pfmenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Power Flow", menu=pfmenu)
        pfmenu.add_command(label="DC PF", command=self.on_dcpf)
        pfmenu.add_command(label="Newton-Raphson", command=self.on_newton)
        pfmenu.add_command(label="Fast Decoupled", command=self.on_fd)

        opfmenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="OPF", menu=opfmenu)
        opfmenu.add_command(label="DC OPF", command=self.on_dcopf)
        opfmenu.add_command(label="AC OPF", command=self.on_acopf)
        opfmenu.add_command(label="DC (UD) OPF", command=self.on_duopf)
        opfmenu.add_command(label="AC (UD) OPF", command=self.on_uopf)

#        helpmenu = Menu(menu, tearoff=False)
#        menu.add_cascade(label="Help", menu=helpmenu)
#        helpmenu.add_command(label="About", command=self.on_about)


    def _init_buttonbar(self):
        buttonbar = Frame(self.frame)
        buttonbar.pack(side=LEFT, fill=Y)

        Button(buttonbar, text="Summary",
               command=self.on_summary).pack(fill=X)
        Button(buttonbar, text="Bus",
               command=self.on_bus_info).pack(fill=X)
        Button(buttonbar, text="Branch",
               command=self.on_branch_info).pack(fill=X)
        Button(buttonbar, text="Generator",
               command=self.on_generator_info).pack(fill=X)

        self.writer_map = {"ReST": ReSTWriter(),
                           "MATPOWER": MATPOWERWriter(),
                           "CSV": CSVWriter(),
                           "DOT": DotWriter()}

        writer_type = self.writer_type = StringVar(buttonbar)
        writer_type.set("ReST") # default value

        writer = OptionMenu(buttonbar, writer_type,
                            "ReST", "MATPOWER", "CSV", "DOT")
        writer.pack(fill=X)

#        Button(buttonbar, text="Clear", activebackground="#CD0000",
#               command=self.on_clear).pack(fill=X, pady=5)

        alwaysclear = self.alwaysclear = IntVar()
        alwaysclear.set(0)
        c = Checkbutton(buttonbar, text="Clear", variable=alwaysclear,
                        justify=LEFT, indicatoron=0, command=self.on_clear)
        c.pack(fill=X, pady=5)

        Button(buttonbar, text="Save Log",
               command=self.on_save_log).pack(fill=X)


    def _init_logframe(self):
        self.ui_log = UILog(self.frame)

#        sys.stdout = self.ui_log
#        sys.stderr = self.ui_log

        handler = logging.StreamHandler(self.ui_log)
        logger.addHandler(handler)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)

        self.ui_log.level.set(logger.getEffectiveLevel())


    def set_network(self, n):
        self.n = n
        self.ui_log.n_name.set(n.name)


    def on_new(self):
        self.set_network(Network())


    def on_open(self):
        ftypes = [("MATPOWER file", ".m"), ("All files", "*")]
        filename = askopenfilename(filetypes=ftypes, defaultextension='.m')
        if filename:
            self.set_network(MATPOWERReader().read(filename))


    def on_6_bus(self):
        self.set_network(MATPOWERReader().read(CASE_6_WW))


    def on_30_bus(self):
        self.set_network(MATPOWERReader().read(CASE_30))


    def on_save_as(self):
        filename = asksaveasfilename(filetypes=[("MATPOWER file", ".m")])
        if filename:
            MATPOWERWriter().write(self.n, filename)

    # Import handlers ---------------------------------------------------------

    def on_unpickle(self):
        ftypes = [("Pickle file", ".pkl"), ("All files", "*")]
        filename = askopenfilename(filetypes=ftypes, defaultextension='.pkl')
        if filename:
            self.set_network(PickleReader().read(filename))


    def on_psse(self):
        ftypes = [("PSS/E file", ".raw"), ("All files", "*")]
        filename = askopenfilename(filetypes=ftypes, defaultextension='.raw')
        if filename:
            self.set_network(PSSEReader().read(filename))


    def on_psat(self):
        ftypes = [("PSAT file", ".m"), ("All files", "*")]
        filename = askopenfilename(filetypes=ftypes, defaultextension='.m')
        if filename:
            self.set_network(PSATReader().read(filename))

    # Export handlers ---------------------------------------------------------

    def on_pickle(self):
        filename = asksaveasfilename(filetypes=[("Pickle file", ".pkl")])
        if filename:
            PickleWriter().write(self.n, filename)


    def on_excel(self):
        filename = asksaveasfilename(filetypes=[("Excel file", ".xls")])
        if filename:
            ExcelWriter().write(self.n, filename)


    def on_csv(self):
        filename = asksaveasfilename(filetypes=[("CSV file", ".csv")])
        if filename:
            CSVWriter().write(self.n, filename)


    def on_rest(self):
        ftypes = [("ReStructuredText file", ".rst")]
        filename = asksaveasfilename(filetypes=ftypes)
        if filename:
            ReSTWriter().write(self.n, filename)

    # View --------------------------------------------------------------------

    def on_graph(self):
        GraphView(self.root)

    # UI Log ------------------------------------------------------------------

    def on_clear(self):
        if self.alwaysclear.get():
            self.ui_log.clear()


    def on_summary(self):
        if self.alwaysclear.get():
            self.ui_log.clear()
        writer = self.writer_map[self.writer_type.get()]
        writer.write_header(self.n, self.ui_log)
        del writer


    def on_bus_info(self):
        if self.alwaysclear.get():
            self.ui_log.clear()
        writer = self.writer_map[self.writer_type.get()]
        writer.write_bus_data(self.n, self.ui_log)
        del writer


    def on_branch_info(self):
        if self.alwaysclear.get():
            self.ui_log.clear()
        writer = self.writer_map[self.writer_type.get()]
        writer.write_branch_data(self.n, self.ui_log)
        del writer


    def on_generator_info(self):
        if self.alwaysclear.get():
            self.ui_log.clear()
        writer = self.writer_map[self.writer_type.get()]
        writer.write_generator_data(self.n, self.ui_log)
        del writer


    def on_save_log(self):
        ftypes = [("Log file", ".log"),
                  ("Text file", ".txt"),
                  ("All files", "*")]
        filename = asksaveasfilename(filetypes=ftypes)
        if filename:
            log = self.ui_log.log

            file = None
            try:
                file = open(filename, "wb")
                file.write(log.get(1.0, END))
            except:
                logger.error("Error writing to '%s'." % filename)
            finally:
                if file is not None:
                    file.close()

    # -------------------------------------------------------------------------

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


    def on_about(self):
        AboutDialog(self.root)


class GraphView(tkSimpleDialog.Dialog):
    """ A dialog for graph viewing.
    """

    def __init__(self, parent, title="Graph"):
        """ Initialises the font dialog.
        """
        tkSimpleDialog.Dialog.__init__(self, parent, title)



    def body(self, frame):
        """ Creates the dialog body. Returns the widget that should have
            initial focus.
        """
        master = Frame(self)
        master.pack(padx=5, pady=0, expand=1, fill=BOTH)

        title = Label(master, text="Graph")
        title.pack(side=TOP)

        canvas = Canvas(master)
        canvas.pack(expand=YES, fill=BOTH)

        return canvas # Given initial focus.


    def buttonbox(self):
        ''' Adds a button box.
        '''
        box = Frame(self)

        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        w = Button(box, text="Select", width=10, command=self.ok,
                   default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack(side=RIGHT, padx=5, pady=5, anchor=S)


    def validate(self):
        ''' Validate the data. This method is called automatically to validate
            the data before the dialog is destroyed.
        '''
        return 1


    def apply(self):
        ''' Process the data. This method is called automatically to process
            the data, *after* the dialog is destroyed.
        '''
        pass


class UILog(object):

    def __init__(self, master):
        self.master = master

        self._init_text()
        self._init_levels()


    def _init_text(self):
        logframe = Frame(self.master)

        logframe.grid_rowconfigure(0, weight=1)
        logframe.grid_columnconfigure(0, weight=1)

        xscrollbar = Scrollbar(logframe, orient=HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky=E+W)

        yscrollbar = Scrollbar(logframe)
        yscrollbar.grid(row=0, column=1, sticky=N+S)

        log = self.log = Text(logframe, wrap=NONE, background="white",
                        xscrollcommand=xscrollbar.set,
                        yscrollcommand=yscrollbar.set)

        log.grid(row=0, column=0, sticky=N+S+E+W)

        xscrollbar.config(command=log.xview)
        yscrollbar.config(command=log.yview)

        logframe.pack(expand=YES, fill=BOTH)


    def _init_levels(self):
        loglevels = Frame(self.master)
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

        n_name = self.n_name = StringVar()
        Label(loglevels, textvariable=n_name).pack(side=RIGHT, padx=5)


    def write(self, buf):
        self.log.insert(END, buf)
        self.log.see(END)


    def flush(self):
        pass


    def clear(self):
        self.log.delete(1.0, END)


    def on_level(self):
        logger.setLevel(self.level.get())


class AboutDialog(object):

    def __init__(self, parent):
        top = self.top = Toplevel(parent)

        l = self.l = Label(top, text="Pylon")
        l.pack(padx=100, pady=15)

        b = Button(top, text="OK", command=self.ok)
        b.pack(pady=25)


    def ok(self):
        self.top.destroy()


def main():
    root = Tk()
    root.minsize(300, 300)
#    root.geometry("666x666")
    root.title('PYLON')
    app = PylonTk(root)
    root.mainloop()


if __name__ == "__main__":
#    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
#                        format="%(levelname)s: %(message)s")

#    logger.addHandler(logging.StreamHandler(sys.stdout))
#    logger.setLevel(logging.DEBUG)

    main()
