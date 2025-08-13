import tkinter as tk
from PyJEM import TEM3
import threading
import keyboard
 
class BeamControllerApp:
    def __init__(self, master):
        self.master = master
        master.title("Beam Blank Controller")
 
        self.tem = TEM3
        self.is_blank = self.tem.Def3().GetBeamBlank()
        self.current_hotkey = 'alt+q'
 
        self.btn = tk.Button(master, text="Blank Beam", width=20, command=self.toggle_beam)
        self.btn.pack(padx=20, pady=10)
        if self.is_blank == True:
            self.btn.config(text="Unblank Beam", bg='#65A8E1')
        else:
            self.btn.config(text="Blank Beam", bg='#32CD32')

 
        # Hotkey entry
        tk.Label(master, text="Hotkey:").pack()
        self.hotkey_entry = tk.Entry(master)
        self.hotkey_entry.insert(0, self.current_hotkey)
        self.hotkey_entry.pack(pady=5)
 
        self.set_hotkey_btn = tk.Button(master, text="Set Hotkey", command=self.update_hotkey)
        self.set_hotkey_btn.pack(pady=10)
 
        threading.Thread(target=self.hotkey_listener, daemon=True).start()
 
    def toggle_beam(self):
        if self.is_blank:
            self.tem.Def3().SetBeamBlank(1)
            self.btn.config(text="Unblank Beam", bg='#65A8E1')
            self.is_blank = False
        else:
            self.tem.Def3().SetBeamBlank(0)
            self.btn.config(text="Blank Beam", bg='#32CD32')
            self.is_blank = True
 
    def hotkey_listener(self):
        keyboard.add_hotkey(self.current_hotkey, lambda: self.master.after(0, self.toggle_beam))
        keyboard.wait()
 
    def update_hotkey(self):
        new_hotkey = self.hotkey_entry.get().strip()
        if new_hotkey:
            keyboard.clear_all_hotkeys()
            self.current_hotkey = new_hotkey
            keyboard.add_hotkey(self.current_hotkey, lambda: self.master.after(0, self.toggle_beam))
 
def main():
    root = tk.Tk()
    app = BeamControllerApp(root)
    root.mainloop()
 
if __name__ == "__main__":
    main()