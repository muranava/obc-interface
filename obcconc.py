import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as etree
import multiprocessing as mp
import re
import os
import sys
import math
import csv
import random
import datetime
import operator
import obcinterface
import obctools

class ConcordanceFrame(tk.Frame):

    def __init__(self, parent, main, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.main = main
        self.parent = parent
        self.draw_ui()

    def yview(self, *args):
        self.index_text.yview(*args)
        self.line_text.yview(*args)
        for key, m_text in self.meta_text.items():
            m_text.yview(*args)
        
    def draw_ui(self):
        # init vars
        self.search_str = tk.StringVar()
        self.search_label = tk.StringVar()
        self.start_year = tk.IntVar()
        self.end_year = tk.IntVar()
        self.context_left = tk.IntVar()
        self.context_right = tk.IntVar()
        self.case_sensitive = tk.IntVar()
        self.whole_words = tk.IntVar()
        self.show_pos = tk.IntVar()
        self.show_pos_key = tk.IntVar()
        self.use_regex = tk.IntVar()
        self.corpus = tk.StringVar()
        # frame config
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)

        self.info_label = ttk.Label(self, text="", wraplength=600)
        self.info_label.grid(column=0, row=2, sticky="new", columnspan=5)

        self.tool_frame = ttk.Frame(self, padding="5 5 5 5")
        self.tool_frame.grid(row=1, column=0, sticky="news")
        self.display_frame = ttk.Frame(self, padding="5 5 5 5")
        self.display_frame.rowconfigure(0, weight=1)
        self.display_frame.rowconfigure(1, weight=0)
        self.display_frame.columnconfigure(0, weight=0)
        self.display_frame.columnconfigure(1, weight=1)
        self.display_frame.columnconfigure(2, weight=0)
        self.display_frame.columnconfigure(3, weight=1)
        self.display_frame.grid(row=0, column=0, sticky="news")
        
        #  display frame
        self.ybar = ttk.Scrollbar(self.display_frame, command=self.yview)
        self.ybar.grid(row=0, column=2, sticky="news")
        self.line_xbar = ttk.Scrollbar(self.display_frame, orient="horizontal")
        self.line_xbar.grid(row=1, column=1, sticky="news")
        self.line_text = tk.Text(self.display_frame, wrap="none", height=30,
                                 yscrollcommand=self.ybar.set,
                                 xscrollcommand=self.line_xbar.set, width=100)
        self.line_text.grid(row=0, column=1, sticky="nesw")
        self.line_xbar.config(command=self.line_text.xview)
        self.index_text = tk.Text(self.display_frame, width=6, yscrollcommand=self.ybar.set, height=30)
        self.index_text.grid(row=0, column=0, sticky="nesw")

        self.meta_xbar = ttk.Scrollbar(self.display_frame, orient="horizontal")
        self.meta_xbar.grid(row=1, column=3, sticky="news")
        
        self.main.root.update_idletasks()


        self.meta_canvas = tk.Canvas(self.display_frame, background="white",
                                   xscrollcommand=self.meta_xbar.set)  # , width=w, height=h
        self.meta_canvas.grid(row=0, column=3, sticky="news")
        self.meta_xbar.config(command=self.meta_canvas.xview)
        
        metadata = ["Year", "Gender", "Speaker role", "2-Class", "HISCLASS", "Trial", "Scribe", "Publisher", "Printer", "HISCO code", "HISCO label"]
        self.meta_text = {}
        self.meta_canvas_frame = tk.Frame(self.meta_canvas)
        #self.meta_canvas_frame.grid(row=0, column=0, sticky="news")
        #self.meta_canvas_frame.rowconfigure(0, weight=1)
            
        for i, m in enumerate(metadata):
            self.meta_text[m] = tk.Text(self.meta_canvas_frame, wrap="none", width=20, height=30)
            self.meta_text[m].grid(row=0, column=i, sticky="news")
        self.meta_text["Year"]["width"] = 5
        self.meta_text["Gender"]["width"] = 2
        self.meta_text["Speaker role"]["width"] = 10
        self.meta_text["2-Class"]["width"] = 13
        self.meta_text["Printer"]["width"] = 28
        self.meta_text["HISCO code"]["width"] = 6
        self.meta_text["HISCLASS"]["width"] = 3
        self.meta_text["HISCO label"]["width"] = 75
        self.meta_text["Trial"]["width"] = 15
        self.main.root.update_idletasks()
        x2 = self.meta_canvas_frame.winfo_reqwidth()
        self.meta_canvas.create_window(0, 0, anchor="nw", window=self.meta_canvas_frame)
        self.meta_canvas.config(scrollregion=(0, 0, x2, 0))

        #  tool frame
        tk.Label(self.tool_frame, text="Search string").grid(column=0, row=1, sticky="nw")
        tk.Label(self.tool_frame, text="Export name").grid(column=0, row=2, sticky="nw")
        tk.Label(self.tool_frame, text="From year").grid(column=0, row=3, sticky="nw")
        tk.Label(self.tool_frame, text="to year").grid(column=2, row=3, sticky="nw")
        tk.Label(self.tool_frame, text="Context left").grid(column=0, row=4, sticky="nw")
        tk.Label(self.tool_frame, text="Context right").grid(column=2, row=4, sticky="nw")
        self.search_str_entry = ttk.Entry(self.tool_frame, width=64, textvariable=self.search_str)
        self.label_entry = ttk.Entry(self.tool_frame, width=64, textvariable=self.search_label)
        self.start_year_entry = ttk.Entry(self.tool_frame, width=4, textvariable=self.start_year)
        self.end_year_entry = ttk.Entry(self.tool_frame, width=4, textvariable=self.end_year)
        self.left_entry = ttk.Entry(self.tool_frame, width=4, textvariable=self.context_left)
        self.right_entry = ttk.Entry(self.tool_frame, width=4, textvariable=self.context_right)
        self.use_regex_check = ttk.Checkbutton(self.tool_frame, text="Regular expressions", variable=self.use_regex, onvalue=1, offvalue=0)
        self.case_sensitive_check = ttk.Checkbutton(self.tool_frame, text="Case sensitive", variable=self.case_sensitive, onvalue=1, offvalue=0)
        self.whole_words_check = ttk.Checkbutton(self.tool_frame, text="Whole words", variable=self.whole_words, onvalue=1, offvalue=0)
        self.show_pos_key_check = ttk.Checkbutton(self.tool_frame, text="Show POS tags (key)", variable=self.show_pos_key, onvalue=1, offvalue=0)
        self.show_pos_check = ttk.Checkbutton(self.tool_frame, text="Show POS tags (all)", variable=self.show_pos, onvalue=1, offvalue=0)
        self.obc_radio = ttk.Radiobutton(self.tool_frame, text="OBC", variable=self.corpus, value="OBC").grid(column=0, row=6, sticky="w")
        self.obc_pos_radio = ttk.Radiobutton(self.tool_frame, text="OBC-POS", variable=self.corpus, value="OBC-POS").grid(column=1, row=6, sticky="w")
        self.obc_ext_radio = ttk.Radiobutton(self.tool_frame, text="OBCext", variable=self.corpus, value="OBCext").grid(column=2, row=6, sticky="w")
        self.obc_ext_pos_radio = ttk.Radiobutton(self.tool_frame, text="OBCext-POS", variable=self.corpus, value="OBCext-POS").grid(column=3, row=6, sticky="w")
        self.search_str_entry.grid(column=1, row=1, columnspan=4, sticky="nwe")
        self.label_entry.grid(column=1, row=2, columnspan=4, sticky="new")
        self.start_year_entry.grid(column=1, row=3, sticky="new")
        self.end_year_entry.grid(column=3, row=3, sticky="new")
        self.left_entry.grid(column=1, row=4, sticky="new")
        self.right_entry.grid(column=3, row=4, sticky="new")
        self.use_regex_check.grid(column=0, row=5, sticky="new")
        self.whole_words_check.grid(column=1, row=5, sticky="new")
        self.case_sensitive_check.grid(column=2, row=5, sticky="new")
        self.show_pos_key_check.grid(column=3, row=5, sticky="new")
        self.show_pos_check.grid(column=4, row=5, sticky="new")
        # set defaults
        self.search_str.set("type your search string here")
        self.search_label.set("enter a name for this query here")
        self.start_year.set("1720")
        self.end_year.set("1913")
        self.context_left.set("64")
        self.context_right.set("64")
        self.whole_words.set(1)
        self.use_regex.set(1)
        self.case_sensitive.set(0)
        self.show_pos_key.set(0)
        self.show_pos.set(0)
        self.corpus.set("OBC")

        self.search_button = ttk.Button(self.tool_frame, text="Start search", command=self.on_search_click)
        self.search_button.grid(column=0, row=7, columnspan=3, sticky="ew")
        self.export_button = ttk.Button(self.tool_frame, text="Export detailed concordance", command=self.on_export_click)
        self.export_button.grid(column=3, row=7, columnspan=2, sticky="ew")
        self.export_button["state"] = "disabled"
        self.bind('<Return>', self.on_search_click)
        self.search_str_entry.focus()

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.main.root.update()

    def on_search_click(self):
        if self.search_button["text"] == "Start search":
            self.search_cancelled = False
            self.search_button.configure(text="Cancel", state="normal")
            self.info_label.config(text="Searching. Please wait.")
            self.main.root.update_idletasks()
            """ evaluate search options and compile regex """
            if self.case_sensitive.get() == 1:
                self.flags = re.UNICODE
            else:
                self.flags = re.UNICODE | re.IGNORECASE
            if self.whole_words.get() == 1:
                b = r"\b"
            else:
                b = ""
            if self.use_regex.get() == 1:
                s = r'{0}{1}{0}'.format(b, self.search_str.get())
                self.regex = re.compile(s, flags=self.flags)
            else:
                s = r'{0}{1}{0}'.format(
                    b, re.escape(self.search_str.get().strip()))
                self.regex = re.compile(s, flags=self.flags)
            if len(self.search_str.get().strip()) > 0:
                self.do_search()
        else:
            self.search_button["text"] = "Start search"
            self.search_cancelled = True
            self.search_results = None
            self.search_job = None
            self.main.root.update_idletasks()
            self.pipe.close()
            
    def on_export_click(self):
        if self.search_results is not None:
            output_csv = self.init_csv_for_search()
            output_csv.writeheader()
            random.seed()
            for i, r in enumerate(self.search_results):
                r["ID"] = i+1
                r["Random"] = random.random()
                output_csv.writerow(r)
            self.csv_file.close()
            info = bool(self.main.conf_frame.add_search_info.get()) 
            if info:
                self.add_search_info_to_csv() 
            self.info_label["text"] = "Saved {} results to {}.".format(len(self.search_results), os.path.basename(self.filename))
            auto = bool(self.main.conf_frame.auto_open.get())    
            if auto:
                obctools.open_file_externally(self.filename)
            self.main.root.update_idletasks()


    @staticmethod
    def summarize_line_metadata(l):
        """
        ['Filename', '5-Periods', 'ID', 'Speaker-ID', '3-Periods', 'Left', 'Publisher', 'Scribe', 'Speaker role', 'HISCO label', 'HISCO code', 'Editor', '2-Class', 'Printer', 'Gender', 'Random', 'Search name', '4-Periods', '6-Periods', 'Trial', 'Key', 'Right', '2-Periods', 'HISCLASS', 'Year'])
        """
        m_str = "{}|{}|{}|{}|{}\n".format(l["Year"], l["Gender"], l["2-Class"], l["HISCO code"], l["Trial"])
        return m_str

    def add_metadata(self, l):
        for key, m_text in self.meta_text.items():
            m_text.insert("end", "{}\n".format(l[key]))


    def add_concordance_line(self, l, i=0):
        l['Left'] = l['Left'].rjust(self.context_left.get())
        l['Right'] = l['Right'].ljust(self.context_right.get())
        conc_line = "{0}\t\t{1}\t\t{2}\n".format(l['Left'],
                                                 l['Key'],
                                                 l['Right'])
        self.add_metadata(l)
        self.line_text.insert(tk.END, conc_line)
        i = int(self.line_text.index('end-1c').split('.')[0]) -1  # last line of text
        self.index_text.insert(tk.END, "{}\n".format(i))

    def clear_concordance(self):
        self.line_text.delete("0.0", "end")
        self.index_text.delete("0.0", "end")
        for key, m_text in self.meta_text.items():
            m_text.delete("0.0", "end")
    def display_concordance(self):
        self.clear_concordance()
        if self.search_results is not None:
            #longest_line = 0
            for i, l in enumerate(self.search_results):
                self.add_concordance_line(l, i)
            #self.line_text.configure(width=longest_line)
            #self.index_text.configure(width=len(str(i)))
            self.main.root.update_idletasks()

    def do_search(self):
        self.search_results = []
        self.clear_concordance()
        self.export_button["state"] = "disabled"  
        start_year = self.start_year.get()
        end_year = self.end_year.get()  
        corpus = self.corpus.get()
        if "ext" in corpus:
            ext = True
        else:
            ext = False
        if "POS" in corpus:
            pos = True
        else:
            pos = False
        files = list(self.main.list_relevant_files(pos, ext, start_year, end_year))
        self.num_files = len(files)
        options = {}
        options['search_label'] = self.search_label.get()
        options['regex'] = self.regex
        options['context_left'] = self.context_left.get()
        options['context_right'] = self.context_right.get()
        options['show_pos'] = self.show_pos.get()
        options['show_pos_key'] = self.show_pos_key.get()
        manager = mp.Manager()
        self.pipe, worker_pipe = mp.Pipe()
        self.return_shared = manager.list()
        self.search_job = mp.Process(target=worker_search_files,
                                     args=(files, options, self.return_shared, worker_pipe,))
   
        self.search_job.start()
        self.main.root.update_idletasks()
        self.main.root.after(500, self.check_proc_status)
    
    def check_proc_status(self):
        try:
            if self.search_job.is_alive():
                try:
                    if self.pipe.poll():
                        try:
                            results = self.pipe.recv()
                        except OSError:
                            pass
                        else:
                            for r in results:
                                self.add_concordance_line(r)
                                self.search_results.append(r)
                except OSError:
                    pass
                self.main.root.update()
                self.after_job = self.main.root.after(250, self.check_proc_status)
            else:
                self.after_cancel(self.after_job)
                self.search_button["text"] = "Start search"
                self.search_job.terminate()
                if self.search_cancelled:
                    self.clear_concordance()
                else:
                    self.search_results = sorted(self.search_results, key=operator.itemgetter('Filename'))
                    self.finish_search()
        except AttributeError:
            pass
        
    def finish_search(self):
        self.info_label["text"] = "Found {0} results.".format(len(self.search_results))
        self.export_button["state"] = "normal"
        self.display_concordance()

    def add_search_info_to_csv(self):
        csv_text = open(self.filename,"r" )
        rows = csv_text.readlines()
        csv_text.close()
        today = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
        active_str = ""
        if self.use_regex.get() == 1:
            active_str += "RegEx "
        if self.whole_words.get() == 1:
            active_str += "Whole_words "
        if self.case_sensitive.get() == 1:
            active_str += "Case_sensitive "
        if self.show_pos.get() == 1:
            active_str += "Show_all_POS_tags "
        elif self.show_pos_key.get() == 1:
            active_str += "Show_POS_tags_in_key "
        active_str = active_str.strip().replace(" "," | ").replace("_"," ")
        corpus_str = self.corpus.get()
        year_str = "{0}-{1}".format(self.start_year.get(),self.end_year.get())
        param_line = '"Search string: {0}, Years: {1}, Corpus: {2}, Options: {3}, Search executed: {4}"\n\n'.format(self.search_str.get().strip(),year_str,corpus_str,active_str,today)
        rows.insert(0, param_line)
        csv_text = open(self.filename,"w")
        for r in rows:
            csv_text.write(r)
        csv_text.close()


    def init_csv_for_search(self):
        if len(self.search_label.get()) > 0 and "enter a name" not in self.search_label.get():
            label = self.search_label.get().replace(
                " ", "_").replace(".", "_").strip()
        else:
            label = self.search_str.get().replace(
                " ", "_").replace(".", "_").strip()
        label = "".join(x for x in label if (x.isalnum() or x == "_"))
        day = datetime.datetime.now().date()
        d_time = str(datetime.datetime.now().time()).replace(":","-")  #.503886
        dotpos = d_time.find(".")
        if dotpos>0:
            d_time = d_time[:dotpos]
        csv_path = os.path.join(self.main.tool_path, 'concordances', '{0}__{1}__{2}.csv'
        .format(label, day, d_time))
        self.filename = csv_path
        fieldnames = ['ID', 'Left', 'Key', 'Right', 'Year',
                      'Gender', 'Speaker role', '2-Class', 'HISCLASS', 'HISCO code',
                      'HISCO label', 'Scribe', 'Publisher', 'Printer',
                      'Editor', 'Filename', 'Trial', 'Speaker-ID', 'Search name', '2-Periods', '3-Periods', '4-Periods', '5-Periods', '6-Periods', 'Random']
        delim = self.main.conf_frame.csv_delimiter.get()     
        quote = self.main.conf_frame.csv_quotechar.get()
        self.csv_file = open(csv_path, 'w+')
        try:
            writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames,lineterminator="\n",
                                    delimiter=delim, quotechar=quote)
            return writer
        except IOError:
            return None


def worker_search_files(files, options, return_shared, pipe):
    args = ((i, options) for i in files)
    jobs = []
    pool_size = mp.cpu_count()
    if pool_size > 1:
        pool_size -= 1
    pool = mp.Pool(pool_size)
    for job in pool.imap_unordered(worker_search_in_file, args):
        jobs.append(job)
        if job:
            try:
                pipe.send(job)
            except OSError as e:
                print(e)
    pool.close()


def worker_search_in_file(args):
    f, o = args
    tree = etree.parse(f)
    root = tree.getroot()
    speech_nodes = root.findall('.//speech')
    results = []
    for s in speech_nodes:
        speech_text = obctools.prepare_speech(s)
        a = {}
        a['Gender'] = s.get('sex', '')
        a['Trial'] = s.get('trial', '').replace("o", "t").replace("t-", "t")
        a['Year'] = s.get('year', '')
        if a['Year']=='':
            a['Year'] = a['Trial'][1:5]
        a['2-Periods'] = obctools.get_periods(a['Year'],2)
        a['3-Periods'] = obctools.get_periods(a['Year'],3)
        a['4-Periods'] = obctools.get_periods(a['Year'],4)
        a['5-Periods'] = obctools.get_periods(a['Year'],5)
        a['6-Periods'] = obctools.get_periods(a['Year'],6)
        a['Speaker role'] = s.get('role', '')
        a['HISCLASS'] = s.get('HISCLASS', '')
        a['2-Class'] = obctools.convert_hisclass_to_binclass(a['HISCLASS'])
        a['HISCO code'] = s.get('HISCO-code', '')
        a['HISCO label'] = s.get('HISCO-label', '')
        a['Speaker-ID'] = s.get('speaker', '').replace(
            " ", "").replace("-", "").strip()
        a['Printer'] = s.get('printer', '')
        a['Publisher'] = s.get('publisher', '')
        a['Scribe'] = s.get('scribe', '')
        a['Editor'] = s.get('editor', '')
        for m in o['regex'].finditer(speech_text):
            r = {}
            r.update(a)
            if o['show_pos'] == 1:
                r['Key'] = m.group(0)
                r['Left'] = speech_text[:m.start()][-o['context_left']:]
                r['Right'] = speech_text[m.end():][:o['context_right']]
            elif o['show_pos_key'] == 1:
                r['Key'] = m.group(0)
                r['Left'] = speech_text[:m.start()][-o['context_left']:]
                r['Right'] = speech_text[m.end():][:o['context_right']]
                r['Left'] = obctools.strip_pos_tags(r['Left'])
                r['Right'] = obctools.strip_pos_tags(r['Right'])
            else:
                r['Key'] = obctools.strip_pos_tags(m.group(0))
                r['Left'] = speech_text[:m.start()][-o['context_left']:]
                r['Right'] = speech_text[m.end():][:o['context_right']]
                r['Left'] = obctools.strip_pos_tags(r['Left'])
                r['Right'] = obctools.strip_pos_tags(r['Right'])
            r['Filename'] = os.path.basename(f)
            r['Search name'] = o['search_label']
            results.append(r)
    return results


if __name__ == "__main__":
    obcinterface.main()