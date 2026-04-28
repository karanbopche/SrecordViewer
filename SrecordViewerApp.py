import os
import ttkbootstrap as tk
import bincopy
from tkinter import filedialog, simpledialog, messagebox
import tkinter
from tkinter.messagebox import askyesno
from dataclasses import dataclass


class SrecordViewerApp(tk.Window):
    def __init__(self):
        super().__init__()
        self.title("Srecord Viewer")
        self.geometry("1200x720")
        self.custom_exception_handler = self.custom_exception_handler
        self.dataFile = bincopy.BinFile()
        self.loadedFiles = []
        self.sectionFileMappings: dict[int, str] = {}

        frame = tk.Frame(self)
        frame.pack(side="top", fill="x")
        self.fileMenu = tk.Menubutton(frame, text="File")
        self.fileMenu.pack(side="left", fill="x")
        self.fileMenu.menu = tk.Menu(self.fileMenu)
        self.fileMenu["menu"] = self.fileMenu.menu
        self.fileMenu.menu.add_command(
            label="Add Srecord", command=self.__AddSrecordFile
        )
        self.fileMenu.menu.add_command(label="Add IHex", command=self.__AddIhexFile)
        self.fileMenu.menu.add_command(label="Add ELF", command=self.__AddElfFile)
        self.fileMenu.menu.add_command(label="Add Bin", command=self.__AddBinaryFile)
        self.fileMenu.menu.add_command(
            label="Add Ti Text", command=self.__AddTiTextFile
        )
        self.fileMenu.menu.add_command(
            label="Add Microchip Hex", command=self.__AddMicrochipHexFile
        )
        self.fileMenu.menu.add_command(
            label="Add Verilog Vmem", command=self.__AddVerilogVmemFile
        )
        self.fileMenu.menu.add_command(label="Clear", command=self.__ClearView)

        frame = tk.Frame(self)
        frame.pack(side="top", fill="both", expand=True)
        section_frame = tk.LabelFrame(frame, text="Sections")
        section_frame.pack(side="left", fill="y")
        self.sectionList = tkinter.Listbox(
            section_frame, selectmode="single", font=tk.font.Font(family="Courier New")
        )
        self.sectionList.bind("<<ListboxSelect>>", self.__OnSectionListSelected)
        self.sectionList.pack(side="top", expand=True, fill="both")

        data_frame = tk.LabelFrame(frame, text="Data")
        data_frame.pack(side="right", expand=True, fill="both")
        self.dataText = tk.Text(data_frame, font=tk.font.Font(family="Courier New"))
        self.dataText.pack(side="left", expand=True, fill="both")
        self.dataText.config(state="disabled")
        self.dataText.yscrollbar = tk.Scrollbar(data_frame, command=self.dataText.yview)
        self.dataText.yscrollbar.pack(side="right", fill="y")
        self.dataText.config(yscrollcommand=self.dataText.yscrollbar.set)

        frame = tk.Frame(self)
        frame.pack(side="top", fill="x")
        self.statusLabel = tk.Label(frame, text="Ready")
        self.statusLabel.pack(side="left", fill="x")

    def UpdateView(self):
        self.title("Srecord Viewer - " + ", ".join(self.loadedFiles))
        self.sectionList.delete(0, "end")
        for segment in self.dataFile.segments:
            self.sectionList.insert(
                "end",
                f"{segment.address:08x}-{segment.address + len(segment.data):08x}",
            )
        self.sectionList.select_set(0)
        self.__OnSectionListSelected()

    def custom_exception_handler(exc_type, exc_value, exc_traceback):
        messagebox.showerror(
            "Unhandled Exception",
            f"An unhandled error occurred: {exc_value}\n" f"Type: {exc_type.__name__}",
        )

    def __Chunks(self, lst, n):
        for i in range(0, len(lst), n):
            yield i, lst[i : i + n]

    def __ClearView(self):
        self.loadedFiles = []
        self.sectionFileMappings = {}
        self.statusLabel.config(text="Ready")
        self.dataFile = bincopy.BinFile()
        self.sectionList.delete(0, "end")
        self.dataText.config(state="normal")
        self.dataText.delete("1.0", "end")
        self.dataText.config(state="disabled")

    def __update_section_file_mappings(self, datafile, filename: str):
        for segment in datafile.segments:
            if segment.address not in self.sectionFileMappings:
                self.sectionFileMappings[segment.address] = filename

    def __OnSectionListSelected(self, *args):
        selectedIndex = self.sectionList.curselection()
        if selectedIndex:
            self.dataText.config(state="normal")
            self.dataText.delete("1.0", "end")
            segment = self.dataFile.segments[selectedIndex[0]]
            startAddress = segment.address
            self.statusLabel.config(
                text=f"Address: {startAddress:08X} \tSize: {hex(len(segment.data))} bytes \tfile: {self.sectionFileMappings.get(startAddress, 'Unknown')}"
            )
            for offset, data in self.__Chunks(segment.data, 16):
                hexStr = " ".join(map(lambda x: f"{x:02X}", data))
                asciiStr = " ".join(
                    map(lambda x: chr(x) if chr(x).isalnum() else ".", data)
                )
                self.dataText.insert(
                    "end", f"{startAddress+offset:08X}: {hexStr}  {asciiStr}\n"
                )
            self.dataText.config(state="disabled")

    def __AddIhexFile(self):
        files = filedialog.askopenfilenames(
            title="Select File",
            filetypes=[
                ("file", "*.hex *.ihex"),
                ("all files", "*.*"),
            ],
        )
        for file in files:
            try:
                self.dataFile.add_ihex_file(file, overwrite=False)
                self.loadedFiles.append(os.path.basename(file))
                self.__update_section_file_mappings(self.dataFile, str(file))
            except bincopy.AddDataError:
                answer = askyesno(
                    "Overlapping Data",
                    f"File contains data which overlaps with existing data\n\nfilename:{file}\n\nOverride data?",
                )
                if answer:
                    self.dataFile.add_ihex_file(file, overwrite=True)
        self.UpdateView()

    def __AddMicrochipHexFile(self):
        files = filedialog.askopenfilenames(title="Select File")
        for file in files:
            try:
                self.dataFile.add_microchip_hex_file(file, overwrite=False)
                self.loadedFiles.append(os.path.basename(file))
                self.__update_section_file_mappings(self.dataFile, str(file))
            except bincopy.AddDataError:
                answer = askyesno(
                    "Overlapping Data",
                    f"File contains data which overlaps with existing data\n\nfilename:{file}\n\nOverride data?",
                )
                if answer:
                    self.dataFile.add_microchip_hex_file(file, overwrite=True)
        self.UpdateView()

    def __AddTiTextFile(self):
        files = filedialog.askopenfilenames(
            title="Select File",
            filetypes=[
                ("file", "*.hex *.s19 *.ptp *.bin *.elf"),
                ("all files", "*.*"),
            ],
        )
        for file in files:
            try:
                self.dataFile.add_ti_txt_file(file, overwrite=False)
                self.__update_section_file_mappings(self.dataFile, str(file))
                self.loadedFiles.append(os.path.basename(file))
            except bincopy.AddDataError:
                answer = askyesno(
                    "Overlapping Data",
                    f"File contains data which overlaps with existing data\n\nfilename:{file}\n\nOverride data?",
                )
                if answer:
                    self.dataFile.add_ti_txt_file(file, overwrite=True)
        self.UpdateView()

    def __AddVerilogVmemFile(self):
        files = filedialog.askopenfilenames(
            title="Select File",
            filetypes=[
                ("all files", "*.*"),
            ],
        )
        for file in files:
            try:
                self.dataFile.add_verilog_vmem_file(file, overwrite=False)
                self.__update_section_file_mappings(self.dataFile, str(file))
                self.loadedFiles.append(os.path.basename(file))
            except bincopy.AddDataError:
                answer = askyesno(
                    "Overlapping Data",
                    f"File contains data which overlaps with existing data\n\nfilename:{file}\n\nOverride data?",
                )
                if answer:
                    self.dataFile.add_verilog_vmem_file(file, overwrite=True)
        self.UpdateView()

    def __AddElfFile(self):
        files = filedialog.askopenfilenames(
            title="Select File",
            filetypes=[
                ("file", "*.elf"),
                ("all files", "*.*"),
            ],
        )
        for file in files:
            try:
                self.dataFile.add_elf_file(file, overwrite=False)
                self.__update_section_file_mappings(self.dataFile, str(file))
                self.loadedFiles.append(os.path.basename(file))
            except bincopy.AddDataError:
                answer = askyesno(
                    "Overlapping Data",
                    f"File contains data which overlaps with existing data\n\nfilename:{file}\n\nOverride data?",
                )
                if answer:
                    self.dataFile.add_elf_file(file, overwrite=True)
        self.UpdateView()

    def __AddBinaryFile(self):
        files = filedialog.askopenfilenames(title="Select File")
        for file in files:
            address = simpledialog.askinteger("Load Address", "Address of binary data")
            if address is not None:
                try:
                    self.dataFile.add_binary_file(
                        file, address=address, overwrite=False
                    )
                    self.__update_section_file_mappings(self.dataFile, str(file))
                    self.loadedFiles.append(os.path.basename(file))
                except bincopy.AddDataError:
                    answer = askyesno(
                        "Overlapping Data",
                        f"File contains data which overlaps with existing data\n\nfilename:{file}\n\nOverride data?",
                    )
                    if answer:
                        self.dataFile.add_binary_file(
                            file, address=address, overwrite=True
                        )
        self.UpdateView()

    def __AddSrecordFile(self):
        files = filedialog.askopenfilenames(
            title="Select File",
            filetypes=[
                ("file", "*.s19"),
                ("all files", "*.*"),
            ],
        )
        for file in files:
            try:
                self.dataFile.add_srec_file(file, overwrite=False)
                self.__update_section_file_mappings(
                    self.dataFile, str(file)
                )
                self.loadedFiles.append(os.path.basename(file))
            except bincopy.AddDataError:
                answer = askyesno(
                    "Overlapping Data",
                    f"File contains data which overlaps with existing data\n\nfilename:{file}\n\nOverride data?",
                )
                if answer:
                    self.dataFile.add_srec_file(file, overwrite=True)
        self.UpdateView()
