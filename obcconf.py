import tkinter as tk
from tkinter import ttk
import os
import sys
import configparser
import obcinterface


class ConfigFrame(tk.Frame):

    def __init__(self, parent, main, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.main = main
        self.parent = parent
        self.draw_ui()

    def draw_ui(self):
        self.columnconfigure(0, weight=0)
        self.rowconfigure(0, weight=0)
        self.auto_open = tk.IntVar()
        self.add_search_info = tk.IntVar()
        self.csv_quotechar = tk.StringVar()
        self.csv_delimiter = tk.StringVar()
        self.auto_open_check = ttk.Checkbutton(self, text="Open .csv files after export",
            variable=self.auto_open, onvalue=1, offvalue=0)
        self.auto_open_check.grid(column=0, row=1, columnspan=2, sticky="w")
        self.add_search_info_check = ttk.Checkbutton(self, text="Add search info to concordance files",
            variable=self.add_search_info, onvalue=1, offvalue=0)
        self.add_search_info_check.grid(column=0, row=2, columnspan=2, sticky="w")
        ttk.Label(self, text="CSV delimiter").grid(row=3, column=0, sticky="w")
        ttk.Label(self, text="CSV quote character").grid(row=4, column=0, sticky="w")
        self.csv_delimiter_entry = ttk.Entry(self, width=1, textvariable=self.csv_delimiter)
        self.csv_quotechar_entry = ttk.Entry(self, width=1, textvariable=self.csv_quotechar)
        self.csv_delimiter_entry.grid(row=3, column=1)
        self.csv_quotechar_entry.grid(row=4, column=1)
        self.config_button = ttk.Button(self, text="Save configuration as default", command=self.on_config_click)
        self.config_button.grid(row=5, column=0, columnspan=2, sticky="ew")
        self.check_config()
        self.auto_open.set(self.config.get("CSV","AutoOpen"))
        self.add_search_info.set(self.config.get("CSV","SearchInfo"))
        self.csv_quotechar.set(self.config.get("CSV","QuoteChar"))
        self.csv_delimiter.set(self.config.get("CSV","Delimiter"))
        for child in self.winfo_children():
            child.grid_configure(padx=3, pady=3)

    def on_config_click(self):
            self.config.set("CSV","AutoOpen", str(self.auto_open.get()))
            self.config.set("CSV","SearchInfo", str(self.add_search_info.get()))
            if len(self.csv_delimiter.get()) > 0:   
                self.config.set("CSV","Delimiter", self.csv_delimiter.get())
            if len(self.csv_quotechar.get()) > 0:
                self.config.set("CSV","QuoteChar", self.csv_quotechar.get())
            with open(self.config_path, 'w') as f:
                self.config.write(f)

    def create_default_config(self):
        self.config = configparser.SafeConfigParser()
        self.config.optionxform = str
        self.config.add_section("CSV")
        self.config.set("CSV","Delimiter",",")
        self.config.set("CSV","QuoteChar",'"')
        self.config.set("CSV","AutoOpen","1")
        self.config.set("CSV","SearchInfo","0")
        with open(self.config_path, 'w') as f:
            self.config.write(f)


    def check_config(self):
        self.config_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),"config.ini")
        self.config = configparser.SafeConfigParser()
        if not os.path.exists(self.config_path):
            self.create_default_config()
        else: # do basic sanity checks on config, set to defaults if values off
            self.config.optionxform = str
            self.config.read(self.config_path)
            if self.config.get("CSV","AutoOpen") not in ("0","1"):
                self.config.set("CSV","AutoOpen","1")
            if self.config.get("CSV","SearchInfo") not in ("0","1"):
                self.config.set("CSV","SearchInfo","1")
            if len(self.config.get("CSV","Delimiter"))<1:
                self.config.set("CSV","Delimiter",",")
            if len(self.config.get("CSV","QuoteChar"))<1:
                self.config.set("CSV","QuoteChar",'"')
            if self.config.get("CSV","Delimiter") == self.config.get("CSV","QuoteChar"):
                self.config.set("CSV","Delimiter",",")
                self.config.set("CSV","QuoteChar",'"')



if __name__ == "__main__":
    obcinterface.main()