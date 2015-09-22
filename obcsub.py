import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as etree
import multiprocessing as mp
import obctools
import obcinterface
import operator
import os

class SubcorpusFrame(tk.Frame):

    def __init__(self, parent, main, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.main = main
        self.parent = parent
        self.draw_ui()

    def draw_ui(self):
        self.subcorpus_label = tk.StringVar()
        self.start_year = tk.IntVar()
        self.end_year = tk.IntVar()
        self.corpus = tk.StringVar()
        self.subcorpus_format = tk.StringVar()
        self.start_year_entry = ttk.Entry(self, width=4, 
                                                    textvariable=self.start_year)
        self.end_year_entry = ttk.Entry(self, width=4,
                                                  textvariable=self.end_year)
        ttk.Label(self, text="Corpus").grid(column=0,  row=4,  sticky="w")
        self.subcorpus_obc_radio = ttk.Radiobutton(self, text="OBC", variable=self.corpus,
            value="OBC").grid(column=1, row=4, sticky="w")
        self.subcorpus_obc_pos_radio = ttk.Radiobutton(self, text="OBC-POS",
                                                       variable=self.corpus,
            value="OBC-POS").grid(column=2, row=4, sticky="w")
        self.subcorpus_obc_ext_radio = ttk.Radiobutton(self, text="OBCext",
                                                       variable=self.corpus,
            value="OBCext").grid(column=3, row=4, sticky="w")
        self.subcorpus_obc_ext_pos_radio = ttk.Radiobutton(self, text="OBCext-POS",
                                                           variable=self.corpus,
            value="OBCext-POS").grid(column=4, row=4, sticky="w")
        ttk.Label(self, text="Format").grid(column=0,  row=5,  sticky="w")
        self.subcorpus_txt_radio = ttk.Radiobutton(self, text="Plaintext",
                                                   variable=self.subcorpus_format,
            value=".txt").grid(column=1, row=5, sticky="w")
        self.subcorpus_xml_radio = ttk.Radiobutton(self, text="XML",
                                                   variable=self.subcorpus_format,
            value=".xml").grid(column=2, row=5, sticky="w")
        self.gender_list = tk.Listbox(self, height=3, selectmode='multiple',
                                                exportselection=0)
        self.gender_list.insert("end","female")
        self.gender_list.insert("end","male")
        self.gender_list.insert("end","unknown")
        ttk.Label(self, text="Gender").grid(column=0, row=2,  sticky="w")
        self.gender_list.grid(column=1,row=2,  sticky="w")
        hisclass = ['1 - Higher managers','2 - Higher professionals','3 - Lower managers',
                    '4 - Lower professionals, clerical and sales personnel',
                    '5 - Lower clerical and sales personnel','6 - Foremen', 
                    '7 - Foremen and skilled workers', '8 - Farmers and fishermen', 
                    '9 - Lower-skilled workers', '10 - Lower-skilled farm workers',
                    '11 - Unskilled workers', '12 - Unskilled farm workers',  
                    '13 - Unspecified workers', 'unknown']
        self.hisclass_list = tk.Listbox(self, height=14, width=45, selectmode='multiple',
                                                  exportselection=0)
        for c in hisclass:
            self.hisclass_list.insert("end", c)
        ttk.Label(self, text="HISCLASS").grid(column=4, row=2, sticky="w")
        self.hisclass_list.grid(column=5, row=2, sticky="ew")
        roles = ["defendant","interpreter","judge","lawyer","victim","witness","unknown"]
        self.role_list = tk.Listbox(self, height=7, width=10, selectmode='multiple',
                                              exportselection=0)
        for r in roles:
            self.role_list.insert("end", r)
        ttk.Label(self, text="Role").grid(column=2, row=2,  sticky="w")
        self.role_list.grid(column=3, row=2, sticky="w")
        self.start_year_entry.grid(column=1, row=1, sticky="w")
        self.end_year_entry.grid(column=3, row=1, sticky="w")
        self.start_year.set("1720")
        self.end_year.set("1913")
        self.corpus.set("OBC")
        self.subcorpus_format.set(".txt")
        ttk.Label(self, text="From year").grid(column=0, row=1, sticky="w")
        ttk.Label(self, text="to year").grid(column=2, row=1, sticky="w")
        self.info_label = ttk.Label(self, text="", wraplength=500)
        self.info_label.grid(column=0, row=7,columnspan=6, sticky="ew")
        self.subcorpus_button = ttk.Button(self, text="Create subcorpus",
                                           command=self.on_subcorpus_click)
        self.subcorpus_button.grid(column=0, row=6, columnspan=6, sticky="ew")
        for child in self.winfo_children():
            child.grid_configure(padx=3, pady=3) 


    def on_subcorpus_click(self):
        if self.subcorpus_button["text"] == "Create subcorpus":
            self.subcorpus_cancelled = False
            self.subcorpus_button.configure(text="Cancel", state="normal")
        
            self.info_label.config(text="Creating subcorpus. Please wait.")
            self.main.root.update_idletasks()
            self.create_subcorpus()
        else:
            self.subcorpus_button["text"] = "Create subcorpus"
            self.subcorpus_cancelled = True
            self.subcorpus_results = None
            self.subcorpus_job = None
            self.main.root.update_idletasks()
            self.pipe.close()


    def create_subcorpus(self):
        self.subcorpus_results = []
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
        self.options = {}
        self.options["Gender"] = obctools.convert_listbox_to_list(self.gender_list,
                                                                  "gender")
        self.options["HISCLASS"] =  obctools.convert_listbox_to_list(self.hisclass_list,
                                                                     "hisclass")
        self.options["Speaker role"] = obctools.convert_listbox_to_list(self.role_list,
                                                                        "role")
        # create filename based on selection criteria
        fn = "subcorpus__{}_{}".format(self.start_year.get(),
                                         self.end_year.get())
        if len(self.options['Gender']) > 0:
            g_str = "_".join(self.options['Gender'])
            fn = "{}__gender_{}".format(fn, g_str)
        if len(self.options['Speaker role']) > 0:
            r_str = "_".join(self.options['Speaker role'])
            fn = "{}__role_{}".format(fn, r_str)
        if len(self.options['HISCLASS']) > 0:
            h_str = "_".join(self.options['HISCLASS'])
            fn = "{}__class_{}".format(fn, h_str)
        self.filename = "{}__{}{}".format(self.corpus.get(), fn,
                                          self.subcorpus_format.get())
        manager = mp.Manager()
        self.return_shared = manager.list()
        self.pipe, worker_pipe = mp.Pipe()
        self.subcorpus_job = mp.Process(target=worker_select_files,
                                        args=(files, self.options, self.return_shared, worker_pipe,))
   
        self.subcorpus_job.start()
        self.main.root.update_idletasks()
        self.main.root.after(500, self.check_proc_status)


    def check_proc_status(self):
        try:
            if self.subcorpus_job.is_alive():
                try:
                    if self.pipe.poll():
                        try:
                            result = self.pipe.recv()
                        except OSError:
                            pass
                        else:
                            self.info_label["text"] = "Selecting from {}".format(result)
                except OSError:
                    pass
                self.main.root.update()
                self.after_job = self.main.root.after(250, self.check_proc_status)
            else:
                try:
                    self.after_cancel(self.after_job)
                except AttributeError:
                    pass
                self.subcorpus_button["text"] = "Create subcorpus"
                self.subcorpus_job.terminate()
                if not self.subcorpus_cancelled:
                    self.subcorpus_results = sorted(self.return_shared, 
                                                    key=operator.itemgetter('Filename'))
                    
                
                    self.finish_subcorpus()
        except AttributeError:
            pass

    @staticmethod
    def get_word_and_utterance_count(results):
        wc = 0
        uc = 0
        for r in results:
            for u in r['Nodes']:
                if u.text is not None:
                    wc += obctools.get_wc_from_string(u.text)
                    uc += 1
                else:
                    print(u)
        return wc, uc

    def finish_subcorpus(self):
        if self.subcorpus_results:
            pc = len(self.subcorpus_results)
            wc, uc = self.get_word_and_utterance_count(self.subcorpus_results)
            self.info_label["text"] = "{} utterances ({}) were selected" \
                                      " from {} proceedings.".format(uc, wc, pc)

            subcorpus_path = os.path.join(self.main.tool_path, "subcorpora")
            if obctools.make_dir(subcorpus_path):
                subcorpus_path = os.path.join(subcorpus_path, self.filename)
                if self.subcorpus_format.get() == ".txt":
                    with open(subcorpus_path, "w") as handler:
                        for r in self.subcorpus_results:
                            for sn in r['Nodes']:
                                s = obctools.prepare_speech(sn)
                                handler.write(s)
                                handler.write("\n\n")
                else:
                   
                    tree = etree.fromstring('<subcorpus filename="{0}"></subcorpus>'.format(self.filename))
                    xml = etree.ElementTree(tree)
                    root = xml.getroot()
                    root.set("utterances", str(uc))
                    root.set("words", str(wc))
                    root.set("proceedings", str(pc))
                    for r in self.subcorpus_results:
                        for sn in r['Nodes']:
                            sn.set("filename",r['Filename'])
                            root.append(sn)
                    with open(subcorpus_path,"wb") as handler:
                        try:
                            xml.write(handler, xml_declaration=True, encoding="utf-8")
                        except IOError as e:
                            print(e)
            self.info_label["text"] = "{:,} utterances ({:,} words) were selected" \
                                      " from {} proceedings" \
                                      " & saved as {}".format(uc, wc, len(self.subcorpus_results),
                                                              os.path.basename(self.filename))

            #self.info_label.config(text="Done. Subcorpus saved as {0}.".format(os.path.basename(self.filename)))

            self.subcorpus_results = None
            self.main.root.update_idletasks()


def worker_select_files(files, options, return_shared, pipe):
    args = ((i, options) for i in files)
    pool_size = mp.cpu_count()
    if pool_size > 1:
        pool_size -= 1
    pool = mp.Pool(pool_size)
    for job, f in pool.imap_unordered(worker_select_from_file, args):
        if job:
            return_shared += job
        try:
            pipe.send(f)
        except OSError as e:
            print(e)
    pool.close()



def worker_select_from_file(args):
    f, o = args
    tree = etree.parse(f)
    root = tree.getroot()
    r = {}
    r['Filename'] = os.path.basename(f)
    r['Nodes'] = []
    speech_nodes = root.findall('.//speech')
    results = []
    for s in speech_nodes:
        criteria = []
        speech_text = obctools.prepare_speech(s)
        a = {}
        a['Gender'] = s.get('sex', 'u')
        if a["Gender"] == "":
            a["Gender"] = "u"
        if len(o['Gender'])>0:
            if a['Gender'] in o['Gender']:
                criteria.append(True)
            else:
                criteria.append(False)
        if len(o['Speaker role'])>0:
            a['Speaker role'] = s.get('role', 'u').lower()
            if a["Speaker role"] == "":
                a["Speaker role"] = "u"
            if a["Speaker role"] in o["Speaker role"]:
                criteria.append(True)
            else:
                criteria.append(False)
        if len(o['HISCLASS'])>0:
            a['HISCLASS'] = s.get('HISCLASS', 'u')
            if a["HISCLASS"] == "":
                a["HISCLASS"] = "u"
            if a["HISCLASS"] in o["HISCLASS"]:
                criteria.append(True)
            else:
                criteria.append(False)
        if False not in criteria:
            r['Nodes'].append(s)
    results.append(r)

    return results, r['Filename']




if __name__ == "__main__":
    obcinterface.main()