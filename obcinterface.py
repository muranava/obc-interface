import tkinter as tk
from tkinter import ttk
import multiprocessing as mp
import math
import re
import os
import subprocess
import configparser
import platform
import sys
import obcconc
import obcsub
import obctools
import obcconf


"""
Old Bailey Corpus Interface by Magnus Nissel (www.u203d.net)
"""

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/.
"""




class OBCInterface:

    def __init__(self):
        self.root = tk.Tk()
        try:
             self.root.tk.call('console', 'hide')
        except tk.TclError:
             pass
        self.tool_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.draw_ui()
        self.maximize()
        self.list_all_files()
        self.root.mainloop()

    def maximize(self):
        toplevel = self.root.winfo_toplevel()
        try:
            toplevel.wm_state('zoomed')
        except tk.TclError:
            w = self.root.winfo_screenwidth()
            h = self.root.winfo_screenheight() - 60
            geom_string = "%dx%d+0+0" % (w,h)
            toplevel.wm_geometry(geom_string)

    def draw_ui(self):
        try:
            s = ttk.Style()
            s.theme_use('clam')
        except tk.TclError:
            pass
        frame_style = ttk.Style()
        frame_style.configure('obcFrame.TFrame', background='deepskyblue')
        self.root.title("OBC Offline")
        self.root.columnconfigure(0, weight=1) 
        self.root.rowconfigure(0, weight=1)
        self.main_frame = ttk.Frame(self.root, padding="3 3 3 3", style="obcFrame.TFrame")
        self.main_frame.grid(column=0, row=0, sticky="news")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_book = ttk.Notebook(self.main_frame)
        self.main_book.grid(column=0, row=0, sticky="news")

        self.conc_frame = obcconc.ConcordanceFrame(parent=self.main_frame, main=self)
        self.main_book.add(self.conc_frame, text="Concordance")

        self.sub_frame = obcsub.SubcorpusFrame(parent=self.main_frame, main=self)
        self.main_book.add(self.sub_frame, text="Subcorpus")

        self.conf_frame = obcconf.ConfigFrame(parent=self.main_frame, main=self)
        self.main_book.add(self.conf_frame, text="Configuration")

    def list_all_files(self):
        source = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "corpus")
        self.files = set([os.path.join(dp, f) for dp, dn, fn in
                     os.walk(os.path.expanduser(source))
                     for f in fn if '.xml' in f])
       

    def list_relevant_files(self, pos=False, ext=False, start_year=1720, end_year=1913):
        if pos:
            files = set([f for f in self.files if '.xml' in f and '-POS-' in f])
        else:
            files = set([f for f in self.files if '.xml' in f and '-POS-' not in f])
        
        if not ext:
            files = self.filter_core_files(files)
        relevant_files = set()
        for f in files:
            year = int(os.path.basename(f).replace(".xml", "")[-8:-4])
            if year >= start_year and year <= end_year:
                relevant_files.add(f)
        return relevant_files

    @staticmethod
    def filter_core_files(files):
        ext = set([17380113, 17390221, 17410405, 17420224, 17420428, 17491011,
               17590711, 17620714, 17741019, 17870112, 17921031, 18040111,
               18070916, 18170917, 18300218, 18350202, 18350302, 18350406,
               18350511, 18351214, 18360713, 18360815, 18370102, 18370227,
               18380226, 18390408, 18421128, 18430227, 18430403, 18430821,
               18451215, 18500408, 18511215, 18520223, 18520510, 18520705,
               18540403, 18550507, 18570706, 18610128, 18610225, 18610505,
               18620106, 18620512, 18620616, 18620707, 18640411, 18660507,
               18670506, 18670610, 18680406, 18690607, 18710109, 18710130,
               18710403, 18720708, 18730303, 18800803, 18801018, 18801123,
               18801213, 18820130, 18820327, 18820626, 18840421, 18880319,
               18900908, 18910112, 18910406, 18910525, 18991023, 19060430,
               19101206, 19120722])
        core_files = set()
        for f in files:
            fn = os.path.basename(f).replace(
                "OBCext-", "").replace("POS-", "").replace(".xml", "").strip()
            fn = int(fn)
            if fn not in ext:
                core_files.add(f)
        return core_files


def main():
    OBC = OBCInterface()

if __name__ == "__main__":
    main()