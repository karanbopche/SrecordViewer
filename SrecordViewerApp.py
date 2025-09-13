import ttkbootstrap as tk
import bincopy
from tkinter import filedialog
import tkinter
from tkinter.messagebox import askyesno


class SrecordViewerApp(tk.Window):
    def __init__(self):
        super().__init__()
        self.title("Srecord Viewer")
        self.geometry("800x600")
        self.srecordfile = bincopy.BinFile()
        frame = tk.Frame(self)
        frame.pack(side="top", fill="x")
        self.fileMenu = tk.Menubutton(frame, text="File")
        self.fileMenu.pack(side="left")
        self.fileMenu.menu = tk.Menu(self.fileMenu)
        self.fileMenu["menu"] = self.fileMenu.menu
        self.fileMenu.menu.add_command(label="Add Srecord", command=self.__AddSrecordFile)
        self.fileMenu.menu.add_command(label="Clear", command=self.__ClearView)
        frame = tk.LabelFrame(self, text="Sections")
        frame.pack(side="left", fill="y")
        self.sectionList = tkinter.Listbox(frame, selectmode="single")
        self.sectionList.bind("<<ListboxSelect>>", self.__OnSectionListSelected)
        self.sectionList.pack(side="top", expand=True, fill="both")
        frame = tk.LabelFrame(self, text="Data")
        frame.pack(side="right", expand=True, fill="both")
        self.dataText = tk.Text(frame, font=tk.font.Font(family="Courier New"))
        self.dataText.pack(side="top", expand=True, fill="both")
        self.dataText.config(state="disabled")

    def UpdateView(self):
        self.sectionList.delete(0, "end")
        for segment in self.srecordfile.segments:
            self.sectionList.insert("end", f"{segment.address:08x}-{segment.address + len(segment.data):08x}")
        self.sectionList.select_set(0)
        self.__OnSectionListSelected()

    def __Chunks(self, lst, n):
        for i in range(0, len(lst), n):
            yield i*n, lst[i:i + n]

    def __ClearView(self):
        self.sectionList.delete(0, "end")
        self.dataText.config(state="normal")
        self.dataText.delete("1.0", "end")
        self.dataText.config(state="disabled")

    def __OnSectionListSelected(self, *args):
        selectedIndex = self.sectionList.curselection()
        if selectedIndex:
            self.dataText.config(state="normal")
            self.dataText.delete("1.0", "end")
            segment = self.srecordfile.segments[selectedIndex[0]]
            startAddress = segment.address
            for offset, data in self.__Chunks(segment.data, 8):
                hexStr = " ".join(map(lambda x: f"{x:02X}", data))
                asciiStr = " ".join(map(lambda x: chr(x) if chr(x).isalnum() else '.' , data))
                self.dataText.insert("end", f"{startAddress+offset:08X}: {hexStr}  {asciiStr}\n")
            self.dataText.config(state="disabled")

    def __AddSrecordFile(self):
        files = filedialog.askopenfilenames()
        for file in files:
            try:
                self.srecordfile.add_srec_file(file, overwrite=False)
            except bincopy.AddDataError:
                answer = askyesno("Overlapping Data", f"File contains data which overlaps with existing data\n\nfilename:{file}\n\nOverride data?")
                if answer:
                    self.srecordfile.add_srec_file(file, overwrite=True)
        self.UpdateView()
