__author__ = 'Richard W. Lincoln, r.w.lincoln@gmail.com'

import os
import sys
import logging
import platform
import webbrowser
import tempfile

import Image # PIL
import PIL.Image, PIL.ImageTk
from StringIO import StringIO

from matplotlib.backends.backend_tkagg \
    import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import matplotlib.pyplot
import matplotlib.image
import matplotlib.figure

from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
import tkSimpleDialog

import pylon
import cvxopt.info

from pylon import \
    Case, DCPF, NewtonRaphson, FastDecoupled, DCOPF, ACOPF, UDOPF

from pylon.readwrite import \
    MATPOWERReader, MATPOWERWriter, ReSTWriter, PSSEReader, PSATReader, \
    CSVWriter, ExcelWriter, DotWriter, PickleReader, PickleWriter

from pylon.readwrite.dot_writer import create_graph

from pylon.readwrite.rst_writer import ReSTExperimentWriter

from pylon.pyreto.main import one_for_one

from pylon.readwrite.common import bus_attrs, branch_attrs, generator_attrs

logger = logging.getLogger('pylon')

CASE_6_WW = os.path.dirname(__file__) + "/test/data/case6ww.pkl"
CASE_30   = os.path.dirname(__file__) + "/test/data/case30pwl.pkl"


class PylonTk(object):
    def __init__(self, master, case=None):
        self.root = master

        frame = self.frame = Frame(master)
        frame.pack(expand=YES, fill=BOTH)

        self._init_menubar()

        nameframe = Frame(frame)

        n_name = self.case_name = StringVar()
        n_name_label = Label(nameframe, textvariable=n_name, relief=SUNKEN,
            anchor=W, padx=3, pady=3, justify=LEFT)
        n_name_label.pack(side=LEFT, expand=YES, fill=X)

        interactions = self.interactions = IntVar()
        Spinbox(nameframe, from_=0, to=1000, width=5, bg="#40E0D0",
                activebackground="#48D1CC",
                textvariable=interactions).pack(fill=Y, side=RIGHT, anchor=E)
        interactions.set(1)

        go = self.go = Button(nameframe, text="Run",
            bg="#FFD700", activebackground="#F4CE00",
            anchor=E, command=self.on_run).pack(side=RIGHT, anchor=E, padx=1)

        nameframe.pack(side=TOP, fill=X)

        n_name_label.bind('<ButtonRelease>', self.on_properties)

        self._init_buttonbar()
        self._init_logframe()

        statusbar = Frame(master)
        status = self.status = StringVar()
        status_label = Label(statusbar, textvariable=status, relief=SUNKEN,
            anchor=W, padx=3, pady=3, justify=LEFT)
        status_label.pack(side=LEFT, expand=YES, fill=X)
        status.set("Ready.")
        statusbar.pack(side=BOTTOM, fill=X)

        self.status_status = True # Is the status displayed and not versions.
        self._status = ""
        status_label.bind('<Button>', self.on_status_down)
        status_label.bind('<ButtonRelease>', self.on_status_leave)
        status_label.bind('<Enter>', self.on_status_enter)
        status_label.bind('<Leave>', self.on_status_leave)

        if case is not None: # Initialise the singleton case.
            self.set_case(case)
        else:
            self.on_new()


    def _init_menubar(self):
        menubar = Menu(self.root, name="menubar")
        self.root.config(menu=menubar)

        filemenu = Menu(menubar, tearoff=False)
        filemenu.add_command(label="New", command=self.on_new)
        filemenu.add_separator()
        filemenu.add_command(label="Open...", command=self.on_open)
        menubar.add_cascade(label="Case", menu=filemenu)

        presetmenu = Menu(filemenu, tearoff=False)
        filemenu.add_cascade(label='Preset', menu=presetmenu)
        presetmenu.add_command(label="6 bus", command=self.on_6_bus)
        presetmenu.add_command(label="30 bus", command=self.on_30_bus)
        filemenu.add_separator()

        filemenu.add_command(label="Save As...", command=self.on_save_as)
        filemenu.add_separator()

        importmenu = Menu(filemenu, tearoff=False)
        filemenu.add_cascade(label='Import', menu=importmenu)
        importmenu.add_command(label="PSS/E", command=self.on_psse)
        importmenu.add_command(label="PSAT", command=self.on_psat)
        importmenu.add_command(label="Pickle", command=self.on_unpickle)

        exportmenu = Menu(filemenu, tearoff=False)
        filemenu.add_cascade(label='Export', menu=exportmenu)
        exportmenu.add_command(label="Excel", command=self.on_excel)
        exportmenu.add_command(label="CSV", command=self.on_csv)
        exportmenu.add_command(label="ReST", command=self.on_rest)
        exportmenu.add_command(label="Pickle", command=self.on_pickle)
        filemenu.add_separator()

        filemenu.add_command(label="Properties", command=self.on_properties)
        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=self.on_exit,
                             accelerator="Alt-X")
        self.root.bind('<Alt-x>', self.on_exit)


        viewmenu = Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Graph", menu=viewmenu)
        viewmenu.add_command(label="Graph", command=self.on_graph)

        pfmenu = Menu(menubar, tearoff=True)
        menubar.add_cascade(label="Power Flow", menu=pfmenu)
        pfmenu.add_command(label="DC PF", command=self.on_dcpf)
        pfmenu.add_command(label="Newton-Raphson", command=self.on_newton)
        pfmenu.add_command(label="Fast Decoupled", command=self.on_fd)

        opfmenu = Menu(menubar, tearoff=True)
        menubar.add_cascade(label="OPF", menu=opfmenu)
        opfmenu.add_command(label="DC OPF", command=self.on_dcopf)
        opfmenu.add_command(label="AC OPF", command=self.on_acopf)
        opfmenu.add_command(label="DC (UD) OPF", command=self.on_duopf)
        opfmenu.add_command(label="AC (UD) OPF", command=self.on_uopf)

        mktmenu = Menu(menubar, tearoff=True)
        menubar.add_cascade(label="RL", menu=mktmenu)
        mktmenu.add_command(label="Run", command=self.on_run)

        help = Menu(menubar, tearoff=False, name="help")
        menubar.add_cascade(label="Help", menu=help)
        help.add_command(label="About PylonTk", command=self.on_about)
        help.add_command(label="Online Documentation", command=self.on_doc)


    def _init_buttonbar(self):
        buttonbar = Frame(self.frame, pady=1)
        buttonbar.pack(side=LEFT, fill=Y, pady=1)

        head = Label(buttonbar, text="Case", bg="#FFA07A")#"#FFD700")
        head.pack(fill=X, padx=1)

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
        writer.pack(fill=X, pady=2)

        sub = Label(buttonbar, text="RL", bg="#6495ED")
        sub.pack(fill=X, padx=1, pady=2)

        Button(buttonbar, text="State",
               command=self.on_state_info).pack(fill=X)
        Button(buttonbar, text="Action",
               command=self.on_action_info).pack(fill=X)
        Button(buttonbar, text="Reward",
               command=self.on_reward_info).pack(fill=X)

        foot = Label(buttonbar, text="Log", bg="#90EE90")
        foot.pack(fill=X, padx=1, pady=2)

        alwaysclear = self.alwaysclear = IntVar()
        alwaysclear.set(0)
        c = Checkbutton(buttonbar, text="Clear", variable=alwaysclear,
                        justify=LEFT, indicatoron=0, command=self.on_clear)
        c.pack(fill=X)

        Button(buttonbar, text="Save As",
               command=self.on_save_log).pack(fill=X, pady=2)



#        level = self.level = IntVar()
#
#        debug = Radiobutton(buttonbar, text="DEBUG", variable=level,
#                            value=logging.DEBUG, command=self.on_level)
#        debug.pack(anchor=W, pady=5)
#        info = Radiobutton(buttonbar, text="INFO", variable=level,
#                           value=logging.INFO, command=self.on_level)
#        info.pack(anchor=W)
#        warn = Radiobutton(buttonbar, text="WARN", variable=level,
#                           value=logging.WARNING, command=self.on_level)
#        warn.pack(anchor=W)
#        error = Radiobutton(buttonbar, text="ERROR", variable=level,
#                            value=logging.ERROR, command=self.on_level)
#        error.pack(anchor=W)
#
#        level.set(logger.getEffectiveLevel())


    def on_level(self):
        pass


    def _init_logframe(self):
        self.ui_log = UILog(self.frame)

#        sys.stdout = self.ui_log
#        sys.stderr = self.ui_log

        handler = logging.StreamHandler(self.ui_log)
        logger.addHandler(handler)
#        formatter = logging.Formatter("%(levelname)s: %(message)s")
#        handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)

        self.ui_log.level.set(logger.getEffectiveLevel())


    def set_case(self, case):
        self.case = case
        e = one_for_one(case)
        self.set_experiment(e)

        self.root.title("PylonTk:  %s" % self.case.name)
        self.case_name.set("Current Case:  %s" % self.case.name)
#        self.ui_log.n_name.set(case.name)


    def set_experiment(self, e):
        self.e = e


    def on_run(self):
        number = self.interactions.get()
        self.e.doInteractions(number)


    def on_status_down(self, event=None):
        self._status = self.status.get()

        self.status_status = False

        python_version = platform.python_version()
        cvxopt_version = cvxopt.info.version
        tk_version = TkVersion
        pylon_version = pylon.__version__

        self.status.set("Python %s, CVXOPT %s, Tk %s" % \
            (python_version, cvxopt_version, tk_version))#, pylon_version))


    def on_status_enter(self, event=None):
        self._status = self.status.get()


    def on_status_leave(self, event=None):
        if not self.status_status:
            self.status.set(self._status)
            self.status_status = True


    def on_new(self):
        c = Case()
        self.set_case(c)


    def on_open(self):
        ftypes = [("MATPOWER file", ".m"), ("All files", "*")]
        filename = askopenfilename(filetypes=ftypes, defaultextension='.m')
        if filename:
            self.set_case(MATPOWERReader().read(filename))


    def on_6_bus(self):
        self.set_case(PickleReader().read(CASE_6_WW))


    def on_30_bus(self):
        self.set_case(PickleReader().read(CASE_30))


    def on_save_as(self):
        filename = asksaveasfilename(filetypes=[("MATPOWER file", ".m")])
        if filename:
            MATPOWERWriter().write(self.case, filename)


    def on_properties(self, event=None):
        CaseProperties(self.root, self.case)

    # Import handlers ---------------------------------------------------------

    def on_unpickle(self):
        ftypes = [("Pickle file", ".pkl"), ("All files", "*")]
        filename = askopenfilename(filetypes=ftypes, defaultextension='.pkl')
        if filename:
            self.set_case(PickleReader().read(filename))


    def on_psse(self):
        ftypes = [("PSS/E file", ".raw"), ("All files", "*")]
        filename = askopenfilename(filetypes=ftypes, defaultextension='.raw')
        if filename:
            self.set_case(PSSEReader().read(filename))


    def on_psat(self):
        ftypes = [("PSAT file", ".m"), ("All files", "*")]
        filename = askopenfilename(filetypes=ftypes, defaultextension='.m')
        if filename:
            self.set_case(PSATReader().read(filename))

    # Export handlers ---------------------------------------------------------

    def on_pickle(self):
        filename = asksaveasfilename(filetypes=[("Pickle file", ".pkl")])
        if filename:
            PickleWriter().write(self.case, filename)


    def on_excel(self):
        filename = asksaveasfilename(filetypes=[("Excel file", ".xls")])
        if filename:
            ExcelWriter().write(self.case, filename)


    def on_csv(self):
        filename = asksaveasfilename(filetypes=[("CSV file", ".csv")])
        if filename:
            CSVWriter().write(self.case, filename)


    def on_rest(self):
        ftypes = [("ReStructuredText file", ".rst")]
        filename = asksaveasfilename(filetypes=ftypes)
        if filename:
            ReSTWriter().write(self.case, filename)

    # View --------------------------------------------------------------------

    def on_graph(self):
        GraphView(self.root, self.case, self.e)

    # UI Log ------------------------------------------------------------------

    def on_clear(self):
        if self.alwaysclear.get():
            self.ui_log.clear()


    def on_summary(self):
        if self.alwaysclear.get():
            self.ui_log.clear()
        writer = self.writer_map[self.writer_type.get()]
        writer.write_header(self.case, self.ui_log)
        del writer


    def on_bus_info(self):
        if self.alwaysclear.get():
            self.ui_log.clear()
        writer = self.writer_map[self.writer_type.get()]
        writer.write_bus_data(self.case, self.ui_log)
        del writer


    def on_branch_info(self):
        if self.alwaysclear.get():
            self.ui_log.clear()
        writer = self.writer_map[self.writer_type.get()]
        writer.write_branch_data(self.case, self.ui_log)
        del writer


    def on_generator_info(self):
        if self.alwaysclear.get():
            self.ui_log.clear()
        writer = self.writer_map[self.writer_type.get()]
        writer.write_generator_data(self.case, self.ui_log)
        del writer


    def on_state_info(self):
        if self.alwaysclear.get():
            self.ui_log.clear()
        ReSTExperimentWriter().write_state_data(self.e, self.ui_log)


    def on_action_info(self):
        if self.alwaysclear.get():
            self.ui_log.clear()
        ReSTExperimentWriter().write_action_data(self.e, self.ui_log)


    def on_reward_info(self):
        if self.alwaysclear.get():
            self.ui_log.clear()
        ReSTExperimentWriter().write_reward_data(self.e, self.ui_log)


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
        DCPF().solve(self.case)


    def on_newton(self):
        NewtonRaphson().solve(self.case)


    def on_fd(self):
        FastDecoupled().solve(self.case)


    def on_dcopf(self):
        DCOPF().solve(self.case)


    def on_acopf(self):
        ACOPF().solve(self.case)


    def on_duopf(self):
        UDOPF(dc=True).solve(self.case)


    def on_uopf(self):
        UDOPF(dc=False).solve(self.case)


    def on_exit(self, event=None):
        self.root.destroy()

    # -------------------------------------------------------------------------

    def on_about(self):
        AboutDialog(self.root)

    def on_doc(self):
        webbrowser.open("http://pylon.eee.strath.ac.uk/")


class CaseProperties(tkSimpleDialog.Dialog):
    """ A dialog for editing the properties of a case.
    """

    def __init__(self, parent, case, title="Case Properties"):
        """ Initialises the font dialog.
        """
        self.case = case
        tkSimpleDialog.Dialog.__init__(self, parent, title)


    def body(self, frame):
        """ Creates the dialog body. Returns the widget that should have
            initial focus.
        """
        master = Frame(self)
        master.pack(padx=5, pady=0, expand=1, fill=BOTH)

        title = Label(master, text="Buses")
        title.pack(side=TOP)

        bus_lb = self.bus_lb = Listbox(master, selectmode=SINGLE, width=10)
        bus_lb.pack(side=LEFT)

        for bus in self.case.buses:
            bus_lb.insert(END, bus.name)

        bus_lb.bind("<<ListboxSelect>>", self.on_bus)

        self.bus_params = BusProperties(master)

        return bus_lb # Given initial focus.


    def on_bus(self, event=None):
        bus = self.case.buses[int(self.bus_lb.curselection()[0])]

        self.excluded = ["zone", "v_base", "v_magnitude_guess",
                         "v_angle_guess", "v_magnitude", "v_angle", "g_shunt",
                         "b_shunt", "zone"]
        for attr in [a for a in bus_attrs if a not in self.excluded]:
            value = getattr(bus, attr)
            getattr(self.bus_params, attr).set(value)


    def validate(self):
        ''' Validate the data. This method is called automatically to validate
            the data before the dialog is destroyed.
        '''
        return 1


    def apply(self):
        ''' Process the data. This method is called automatically to process
            the data, *after* the dialog is destroyed.
        '''
        bus = self.case.buses[int(self.bus_lb.curselection()[0])]

        for attr in [a for a in bus_attrs if a not in self.excluded+['mode']]:
            value = getattr(self.bus_params, attr).get()
            setattr(bus, attr, value)


class BusProperties(object):
    def __init__(self, master):
        self.master = master
        frame = self.frame = Frame(master)
        frame.pack(side=RIGHT)

        name = self.name = StringVar()
        Label(frame, text="Name:").grid(row=0, sticky=W)
        nameentry = Entry(frame, textvariable=name)
        nameentry.grid(row=0, column=1)

        mode = self.mode = StringVar()
        Label(frame, text="Type:").grid(row=1, sticky=W)
        Label(frame, textvariable=mode).grid(row=1, column=1, sticky=W)
#        nameentry.grid(row=1, column=1)
        mode.set("PV")

        slack = self.slack = IntVar()
        Checkbutton(frame, text="Slack", variable=slack, justify=LEFT,
                    # command=self.on_clear
                    ).grid(row=2, columnspan=2)

        v_max = self.v_max = StringVar()
        Label(frame, text="Vmax:").grid(row=3, sticky=W)
        vmaxentry = Entry(frame, textvariable=v_max)
        vmaxentry.grid(row=3, column=1)

        v_min = self.v_min = StringVar()
        Label(frame, text="Vmin:").grid(row=4, sticky=W)
        vminentry = Entry(frame, textvariable=v_min)
        vminentry.grid(row=4, column=1)


class GraphView(tkSimpleDialog.Dialog):
    """ A dialog for graph viewing.
    """

    def __init__(self, parent, case, experiment):
        """ Initialises the font dialog.
        """
        self.case = case
        self.e = experiment

        tkSimpleDialog.Dialog.__init__(self, parent, title="Graph")


    def draw_graph(self):
        """ Creates a representation of the graph and draws it on the canvas.
        """
        case = self.case
        prog    = self.prog.get()
        format  = self.format.get()

        fig = self.fig

        sbplt = fig.add_subplot(111)

        dotdata = StringIO()
        DotWriter().write(case, dotdata)
        dotdata.seek(0) # rewind

        imagedata = create_graph(dotdata.getvalue(), prog, format)

        # Write the image data to a temporary file.
        suffix = ".%s" % self.format.get()
        # Matplotlib features native PNG support with '.png' suffix.
        tmp_fd, tmp_name = tempfile.mkstemp(suffix=suffix)
        os.close(tmp_fd)
        imagefd = file(tmp_name, "w+b")
        imagefd.write(imagedata) # DOT language.
        imagefd.close()

        im = matplotlib.pyplot.imread(tmp_name)

        fig = matplotlib.figure.Figure(figsize=(6, 6), dpi=100)
        ax = matplotlib.pyplot.axes([0, 0, 1, 1], frameon=False)
        ax.set_axis_off()
        img = matplotlib.pyplot.imshow(im)
        matplotlib.pyplot.show()

        # Remove the temporary file.
        os.remove(tmp_name)

#        stream = StringIO()
#        stream.write(imagedata)
#        stream.seek(0) # rewind
#        pil_image = PIL.Image.open(stream) # Either a string or a file object.

#        f = Figure(figsize=figsize)#, dpi=100)
#        figure(figsize=figsize)

#        ax = axes([0, 0, 1, 1], frameon=False)
#        ax.set_axis_off()

#        im = imshow(graphimage, origin='lower')
#        im = matplotlib.image.frombuffer(graph_io)

#        im = matplotlib.image.pil_to_array(pil_image)

#        dpi = rcParams['figure.dpi']
#        figsize = im.size[0] / dpi, im.size[1] / dpi

        fig.figimage(im, 10, 10)


#        import base64
#        imagedata = base64.encodestring(imagedata)
#
#        if imagedata is not None:
#            stream = StringIO()
#            stream.write(imagedata)
#            stream.seek(0) # rewind
#
##            image = PIL.Image.open("/tmp/logo.png")
##            photo = PIL.ImageTk.PhotoImage(image)
#
##            imagedata = PIL.ImageTk.PhotoImage(data=imagedata)
#
##            pil_image = PIL.Image.open(stream)
##            photo = PIL.ImageTk.PhotoImage(pil_image)
#
#            photo = self.photo = PhotoImage(data=imagedata)
#
#            self.canvas.create_image(50, 50, image=photo, anchor=NW)

    # tkSimpleDialog.Dialog interface -----------------------------------------

    def body(self, frame):
        """ Creates the dialog body. Returns the widget that should have
            initial focus.
        """
        master = Frame(self)
#        master.pack(padx=5, pady=0, expand=1, fill=BOTH)

        buttonbar = Frame(master, pady=1)
        buttonbar.pack(side=LEFT, fill=Y, pady=1)

        head = Label(buttonbar, text="Graphviz", bg="#FFA07A")
        head.pack(fill=X, padx=1, pady=1)

        refresh = Button(buttonbar, text="Refresh",
                         command=self.draw_graph).pack(fill=X)

        # Graphviz layout program.
        prog = self.prog = StringVar(buttonbar)
        prog.set("dot") # default value
        OptionMenu(buttonbar, prog, "dot", "circo", "neato", "twopi",
                   "fdp").pack(fill=X, pady=2)

        # Image format.
        format = self.format = StringVar(buttonbar)
        format.set("png") # default value
        OptionMenu(buttonbar, format, "png", "jpg", "gif").pack(fill=X, pady=2)

        # Graph canvas frame.
        fig = self.fig = matplotlib.figure.Figure(figsize=(6, 4), dpi=100)

#        from numpy import arange, sin, pi
#        a = fig.add_subplot(111)
#        t = arange(0.0,3.0,0.01)
#        s = sin(2*pi*t)
#        a.plot(t,s)


        self.draw_graph()

        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        toolbar = NavigationToolbar2TkAgg(canvas, master)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)



#        drawframe = Frame(master)
#
#        drawframe.grid_rowconfigure(0, weight=1)
#        drawframe.grid_columnconfigure(0, weight=1)
#
#        xscrollbar = Scrollbar(drawframe, orient=HORIZONTAL)
#        xscrollbar.grid(row=1, column=0, sticky=E+W)
#
#        yscrollbar = Scrollbar(drawframe)
#        yscrollbar.grid(row=0, column=1, sticky=N+S)
#
#        canvas = self.canvas = Canvas(drawframe, width=600, height=400,
#            bg='white',
#            xscrollcommand=xscrollbar.set,
#            yscrollcommand=yscrollbar.set)
##        canvas.config(scrollregion=canvas.bbox(ALL))
#        canvas.config(scrollregion=(-800, -600, 1600, 1200))
#
#        canvas.grid(row=0, column=0, sticky=N+S+E+W)
#
#        xscrollbar.config(command=canvas.xview)
#        yscrollbar.config(command=canvas.yview)
#
#
#        xscrollbar.pack(side=BOTTOM, fill=X)
#        yscrollbar.pack(side=RIGHT, fill=Y)
#        canvas.pack(expand=YES, fill=BOTH)
#
#        drawframe.pack(expand=YES, fill=BOTH)

#        self.draw_graph()

        return refresh # Given initial focus.


    def buttonbox(self):
        ''' Adds a button box.
        '''
#        box = Frame(self)
#
#        w = Button(box, text="Cancel", width=10, command=self.cancel)
#        w.pack(side=LEFT, padx=5, pady=5)
#
#        w = Button(box, text="Select", width=10, command=self.ok,
#                   default=ACTIVE)
#        w.pack(side=LEFT, padx=5, pady=5)
#
#        self.bind("<Return>", self.ok)
#        self.bind("<Escape>", self.cancel)
#
#        box.pack(side=RIGHT, padx=5, pady=5, anchor=S)


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
#        self._init_levels()


    def _init_text(self):
        frame = Frame(self.master, bd=1, relief=SUNKEN)
        frame.pack(padx=2, pady=2)

        orange = None#"#FFD700"
        darker = "#D1B100"

        headframe = Frame(frame)
        head = Label(headframe, text="Pylon Log:", bg=orange,
                     justify=LEFT, anchor=W, padx=3, pady=1)
        head.pack(side=LEFT, fill=X, expand=YES)
        headframe.pack(side=TOP, fill=X, expand=YES)


        radioframe = Frame(headframe, bg=orange)
        radioframe.pack(side=RIGHT, padx=5)

#        Label(radioframe, text="Log Level:", bg=orange).grid(row=0)

        level = self.level = IntVar()

        debug = Radiobutton(radioframe, text="Debug", variable=level,
                            value=logging.DEBUG, command=self.on_level,
                            bg=orange, relief=FLAT,
                            offrelief=FLAT)
#        debug.pack(side=RIGHT, anchor=E)
        debug.grid(row=0, column=1)
        info = Radiobutton(radioframe, text="Info", variable=level,
                           value=logging.INFO, command=self.on_level,
                            bg=orange, relief=FLAT, offrelief=FLAT)
#        info.pack(side=RIGHT, anchor=E)
        info.grid(row=0, column=2)
        warn = Radiobutton(radioframe, text="Warning", variable=level,
                           value=logging.WARNING, command=self.on_level,
                            bg=orange, relief=FLAT, offrelief=FLAT)
#        warn.pack(side=RIGHT, anchor=E)
        warn.grid(row=0, column=3)
        error = Radiobutton(radioframe, text="Error", variable=level,
                            value=logging.ERROR, command=self.on_level,
                            bg=orange, relief=FLAT, offrelief=FLAT)
#        error.pack(side=RIGHT, anchor=E)
        error.grid(row=0, column=4)

        level.set(logger.getEffectiveLevel())



        logframe = Frame(frame)

        logframe.grid_rowconfigure(0, weight=1)
        logframe.grid_columnconfigure(0, weight=1)

        xscrollbar = Scrollbar(logframe, orient=HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky=E+W)

        yscrollbar = Scrollbar(logframe)
        yscrollbar.grid(row=0, column=1, sticky=N+S)

        log = self.log = Text(logframe, wrap=NONE, background="white",
                              xscrollcommand=xscrollbar.set,
                              yscrollcommand=yscrollbar.set)

#        log.insert(END, "Pylon " + str(pylon.__version__))

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

#        n_name = self.case_name = StringVar()
#        Label(loglevels, textvariable=n_name).pack(side=RIGHT, padx=5)


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

        l = self.l = Label(top, text="PylonTk")
        l.pack(padx=100, pady=15)

        license = Label(top, text="GNU GPLv2")
        license.pack(pady=5)

        b = Button(top, text="OK", command=self.ok)
        b.pack(pady=10)


    def ok(self):
        self.top.destroy()


def main(case=None):
    root = Tk()
    root.minsize(300, 300)
#    root.geometry("666x666")
    root.title('PylonTk')
    app = PylonTk(root, case)
    root.mainloop()


if __name__ == "__main__":
#    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
#                        format="%(levelname)s: %(message)s")

#    logger.addHandler(logging.StreamHandler(sys.stdout))
#    logger.setLevel(logging.DEBUG)

    main()
