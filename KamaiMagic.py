import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys
import threading
import time
import webbrowser
import base64
from typing import List, Union, Optional
from PIL import Image, ImageTk

# --- CLIPBOARD SAFETY ---
try:
    import pyperclip
except ImportError:
    pyperclip = None

# --- RESOURCE PATH HANDLING ---
def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS # type: ignore
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class KamaiGuardianJourney:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.withdraw() # Hide main UI while login is active
        
        # --- THEME & PATHS ---
        self.PURPLE_BG = "#4b0082" 
        self.HEADER_PURPLE = "#3c004d"
        self.DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
        self.GUI_PASSWORD = "MAGIC is coding"
        
        # --- ROLE SELECTION ---
        prompt_text = "Identify Your Role:\n1. Senior Infrastructure Admin\n2. Junior IT Support\n3. General User / Fanclub"
        choice = simpledialog.askstring("KAMAI NOC LOGIN", prompt_text, parent=self.root)
        
        roles = {"1": "SENIOR", "2": "JUNIOR", "3": "USER"}
        self.role = roles.get(choice if choice else "3", "USER")

        # --- JOURNEY SETUP ---
        # This handles file creation for the manual decryption journey
        self.kamai_filename = ""
        self.setup_journey_artifacts()

        # --- UI INITIALIZATION ---
        self.root.deiconify() # Bring the window back
        self.build_authentic_ui()
        self.update_timers()

    def setup_journey_artifacts(self):
            """ ONLY drops the initial clues for Senior/Junior. NO rewards. """
            if self.role == "SENIOR":
                # 1. Drop the Config (XOR Puzzle)
                self.kamai_filename = os.path.join(self.DESKTOP, "NOC_CONFIG.kamai")
                msg = "QWNjZXNzIEdhdGV3YXk6IE5PQ19HQVRFV0FZX0FDQ0VTUy50eHQ="
                self.create_xor_file(self.kamai_filename, msg, [80, 443, 22, 53])
                
                # 2. Drop the Gateway Log (HEX Puzzle)
                hint_path = os.path.join(self.DESKTOP, "NOC_GATEWAY_ACCESS.txt")
                with open(hint_path, "w", encoding="utf-8") as f:
                    f.write("--- NOC GATEWAY ACCESS LOG ---\n")
                    f.write("[DEBUG] Token: 4b414d41495f4d414749435f53595354454d5f4f56455252494445\n")
                    f.write("[INFO] Use HEX to ASCII to recover the override key.")
                
                # --- drop_reward REMOVED: It won't drop on startup anymore! ---

            elif self.role == "JUNIOR":
                self.kamai_filename = os.path.join(self.DESKTOP, "IT_TICKET.kamai")
                msg = "STEP 1 CLEARED. Solve the Git error in 'GIT_RECOVERY_LOG.txt'."
                self.create_xor_file(self.kamai_filename, msg, "REBOOT")
                
                hint_path = os.path.join(self.DESKTOP, "GIT_RECOVERY_LOG.txt")
                with open(hint_path, "w", encoding="utf-8") as f:
                    f.write("TOKEN: 4b414d4149\nInstruction: Convert TOKEN to ASCII.")

    def action(self):
        """ TRIGGER: The reward ONLY drops when you enter the correct secret key. """
        k = simpledialog.askstring("System Guard", "Enter Key:")
        if k is None: return

        # 1. Main Unlock
        if k == self.GUI_PASSWORD:
            messagebox.showinfo("Status", "NOC Clearance Granted. Deleting Journey Artifacts...")
            self.cleanup(); self.root.destroy()
            
        # 2. Senior WIN Trigger (Triggered by the result of the HEX puzzle)
        elif self.role == "SENIOR" and k.upper() == "KAMAI_MAGIC_SYSTEM_OVERRIDE":
            # This is the ONLY place MAGIC_YAIMAK.jpg is ever created!
            self.drop_reward("MAGIC_YAIMAK.jpg", "KAMAI_MAGIC_SYSTEM_OVERRIDE")
            messagebox.showinfo("Easter Egg", "NOC OVERRIDE DETECTED!\n'MAGIC_YAIMAK.jpg' has dropped on your Desktop.")
            
        # 3. Junior WIN Trigger (Triggered by the result of the HEX token)
        elif self.role == "JUNIOR" and k.upper() == "KAMAI":
            # This is the ONLY place the Force-Push image is ever created!
            self.drop_reward("You force-pushed to main-Bold strategy.jpg", "JUNIOR_RECOVERY_COMPLETE")
            messagebox.showinfo("Easter Egg", "JUNIOR RECOVERY SUCCESS!\nReward dropped on Desktop.")
            
        else:
            messagebox.showerror("Error", "BGP Authentication Failure.")

    def create_xor_file(self, path: str, msg: str, key: Union[List[int], str]):
            """ Simple XOR logic with a fix for port numbers > 255 """
            encrypted = bytearray()
            for i, char in enumerate(msg):
                # Get the raw key (either a character from "REBOOT" or a Port number)
                k = key[i % len(key)]
                
                # If it's a string (Junior), get the ASCII value
                # If it's an integer (Senior), use it directly
                key_val = ord(k) if isinstance(k, str) else k
                
                # THE FIX: Ensure the key value is within 0-255 using modulo
                # 443 % 256 = 187, which is a valid byte!
                final_key_byte = key_val % 256
                
                encrypted.append(ord(char) ^ final_key_byte)
            
            try:
                with open(path, "wb") as f:
                    f.write(encrypted)
            except Exception as e:
                print(f"Error creating artifact: {e}")

    def drop_reward(self, filename: str, secret: str):
        """ Dropping the JPG reward and appending the secret key to the binary data """
        src = resource_path(filename)
        dest = os.path.join(self.DESKTOP, filename)
        
        if os.path.exists(src):
            try:
                with open(src, "rb") as f:
                    img_data = f.read()
                # Simulate Steganography by appending to EOF
                with open(dest, "wb") as f:
                    f.write(img_data)
                    f.write(f"\n\nSECRET_KEY: {secret}".encode())
            except Exception as e:
                print(f"Reward error: {e}")

    def build_authentic_ui(self):
        """ Recreates the actual WannaCry layout with pixel precision """
        self.root.title("Wana Decrypt0r 2.0")
        self.root.geometry("820x680")
        self.root.configure(bg=self.PURPLE_BG)
        self.root.resizable(False, False)

        # --- HEADER AREA ---
        header = tk.Frame(self.root, bg=self.HEADER_PURPLE, height=55)
        header.place(x=0, y=0, width=820)
        
        center_f = tk.Frame(header, bg=self.HEADER_PURPLE)
        center_f.place(relx=0.5, rely=0.5, anchor="center")
        
        self.lbl_head = tk.Label(center_f, text="Ooops, your files have been encrypted!", 
                               fg="white", bg=self.HEADER_PURPLE, font=("Arial", 19, "bold"))
        self.lbl_head.pack(side="left")
        
        self.lang_var = tk.StringVar(value="English")
        self.lang_menu = ttk.Combobox(center_f, textvariable=self.lang_var, 
                                     values=["English", "Thai"], width=8, state="readonly")
        self.lang_menu.pack(side="left", padx=(15, 0))
        self.lang_menu.bind("<<ComboboxSelected>>", self.change_language)

        # --- SIDEBAR AREA ---
        # Image
        img_frame = tk.Frame(self.root, bg="black", bd=2, relief="solid")
        img_frame.place(x=45, y=75, width=180, height=180)
        
        try:
            path = resource_path("kamai_lock.jpg")
            load = Image.open(path).resize((176, 176), Image.Resampling.LANCZOS)
            render = ImageTk.PhotoImage(load)
            img_lbl = tk.Label(img_frame, image=render, bg="black")
            img_lbl.image = render # type: ignore
            img_lbl.pack()
        except:
            tk.Label(img_frame, text="SERVER\nGUARDIAN", fg="white", bg="black", font=("Arial", 18)).pack(expand=True)

        # Timer 1
        t1 = tk.Frame(self.root, bg=self.PURPLE_BG, highlightthickness=1, highlightbackground="white")
        t1.place(x=15, y=270, width=240, height=125)
        self.pay_on_lbl = tk.Label(t1, text="Payment will be raised on", fg="yellow", bg=self.PURPLE_BG, font=("Arial", 10, "bold"))
        self.pay_on_lbl.pack(pady=3)
        tk.Label(t1, text=time.strftime("%m/%d/%Y %H:%M:%S"), fg="white", bg=self.PURPLE_BG).pack()
        self.time_l1 = tk.Label(t1, text="Time Left", fg="white", bg=self.PURPLE_BG)
        self.time_l1.pack()
        self.cnt1 = tk.Label(t1, text="02:23:20:54", fg="white", bg=self.PURPLE_BG, font=("Courier New", 18, "bold"))
        self.cnt1.pack()

        # Timer 2
        t2 = tk.Frame(self.root, bg=self.PURPLE_BG, highlightthickness=1, highlightbackground="white")
        t2.place(x=15, y=410, width=240, height=125)
        self.lost_on_lbl = tk.Label(t2, text="Your files will be lost on", fg="yellow", bg=self.PURPLE_BG, font=("Arial", 10, "bold"))
        self.lost_on_lbl.pack(pady=3)
        tk.Label(t2, text="03/29/2026 19:39:50", fg="white", bg=self.PURPLE_BG).pack()
        self.time_l2 = tk.Label(t2, text="Time Left", fg="white", bg=self.PURPLE_BG)
        self.time_l2.pack()
        self.cnt2 = tk.Label(t2, text="06:23:20:54", fg="white", bg=self.PURPLE_BG, font=("Courier New", 18, "bold"))
        self.cnt2.pack()

        # Navigation Links
        link_f = ("Arial", 9, "underline")
        self.lk1 = tk.Label(self.root, text="About bitcoin", fg="#add8e6", bg=self.PURPLE_BG, cursor="hand2", font=link_f)
        self.lk1.place(x=30, y=550)
        self.lk1.bind("<Button-1>", lambda e: webbrowser.open("https://www.youtube.com/@KamaiSanCh"))

        self.lk2 = tk.Label(self.root, text="How to buy bitcoins?", fg="#add8e6", bg=self.PURPLE_BG, cursor="hand2", font=link_f)
        self.lk2.place(x=30, y=575)
        self.lk2.bind("<Button-1>", lambda e: webbrowser.open("https://x.com/KaMaiT4Chi"))

        self.lk3 = tk.Label(self.root, text="Contact Us", fg="white", bg=self.PURPLE_BG, cursor="hand2", font=("Arial", 11, "bold", "underline"))
        self.lk3.place(x=30, y=610)
        self.lk3.bind("<Button-1>", lambda e: webbrowser.open("https://facebook.com/KaMaiTaChi0san"))

        # --- MAIN TEXT CANVAS ---
        text_f = tk.Frame(self.root, bg="white", bd=2, relief="sunken")
        text_f.place(x=270, y=75, width=530, height=360)
        
        self.txt_box = tk.Text(text_f, font=("Arial", 10), wrap="word", bd=0)
        self.txt_box.pack(side="left", fill="both", expand=True)
        self.set_lang_text("English")
        
        scroll = tk.Scrollbar(text_f, command=self.txt_box.yview)
        scroll.pack(side="right", fill="y")
        self.txt_box.config(yscrollcommand=scroll.set)

        # --- FOOTER & ACTION ---
        footer = tk.Frame(self.root, bg=self.PURPLE_BG)
        footer.place(x=270, y=445, width=530, height=100)
        
        logo = tk.Frame(footer, bg="white", bd=1, relief="solid")
        logo.place(x=0, y=0, width=150, height=85)
        tk.Label(logo, text="₿ bitcoin", font=("Arial", 14, "bold"), fg="#f7931a", bg="white").pack(pady=10)
        tk.Label(logo, text="ACCEPTED HERE", font=("Arial", 8), bg="white").pack()

        self.tip_lbl = tk.Label(footer, text="Send $300 worth of MAGIC to this address:", fg="yellow", bg=self.PURPLE_BG, font=("Arial", 9, "bold"))
        self.tip_lbl.place(x=170, y=5)
        
        self.addr = "MAGIC-is-coding-KAMAI-Fan-666"
        self.ent = tk.Entry(footer, bg="#e0e0e0", fg="black", font=("Arial", 11), relief="flat")
        self.ent.insert(0, self.addr)
        self.ent.config(state="readonly")
        self.ent.place(x=170, y=35, width=310, height=25)
        
        tk.Button(footer, text="Copy", command=self.copy_address).place(x=485, y=35, width=40, height=25)

        self.btn_check = tk.Button(self.root, text="Check Payment", width=34, command=self.action)
        self.btn_check.place(x=270, y=560)
        self.btn_decrypt = tk.Button(self.root, text="Decrypt", width=34, command=self.action)
        self.btn_decrypt.place(x=535, y=560)

    def set_lang_text(self, lang: str):
        self.txt_box.config(state="normal")
        self.txt_box.delete("1.0", tk.END)
        
        if lang == "English":
            content = (
                "What Happened to My Computer?\n\n"
                "Your important files are encrypted. Many of your documents, photos, videos, databases and other files are no longer "
                "accessible because they have been encrypted. Maybe you are busy looking for a way to recover your files, but do not waste your time. "
                "Nobody can recover your files without our decryption service.\n\n"
                "Can I Recover My Files?\n\n"
                "Sure. We guarantee that you can recover all your files safely and easily. But you have not so enough time.\n"
                "You can decrypt some of your files for free. Try now by clicking <Decrypt>.\n\n"
                "How Do I Pay?\n\n"
                "Payment is accepted in MAGIC only. For more information, click <About bitcoin>.\n"
                "Please check the current price of MAGIC and buy some. Then send the correct amount to the address specified in this window."
            )
        else: # Thai
            content = (
                "เกิดอะไรขึ้นกับคอมพิวเตอร์ของฉัน?\n\n"
                "ไฟล์สำคัญของคุณถูกเข้ารหัสแล้ว เอกสาร รูปภาพ วิดีโอ ฐานข้อมูล และไฟล์อื่นๆ ของคุณจำนวนมากไม่สามารถใช้งานได้"
                "เนื่องจากถูกเข้ารหัสไว้ คุณอาจกำลังยุ่งอยู่กับการหาวิธีกู้คืนไฟล์ แต่อย่าเสียเวลาเลย ไม่มีใครสามารถกู้คืนไฟล์ของคุณได้หากไม่มีบริการถอดรหัสของเรา\n\n"
                "ฉันสามารถกู้คืนไฟล์ได้หรือไม่?\n\n"
                "แน่นอน เราขอรับรองว่าคุณสามารถกู้คืนไฟล์ทั้งหมดได้อย่างปลอดภัยและง่ายดาย แต่คุณมีเวลาไม่มากนัก\n"
                "คุณสามารถทดลองถอดรหัสไฟล์บางส่วนได้ฟรีโดยคลิกที่ <ถอดรหัส>\n\n"
                "ฉันจะจ่ายเงินได้อย่างไร?\n\n"
                "เรารับชำระเงินผ่าน MAGIC เท่านั้น สำหรับข้อมูลเพิ่มเติม โปรดคลิกที่ <About bitcoin>\n"
                "โปรดตรวจสอบราคาปัจจุบันของ MAGIC และซื้อตามจำนวนที่กำหนด จากนั้นส่งไปยังที่อยู่ที่ระบุไว้ในหน้าต่างนี้"
            )
        self.txt_box.insert("1.0", content)
        self.txt_box.config(state="disabled")

    def change_language(self, event=None):
        role_l = self.lang_var.get()
        self.set_lang_text(role_l)
        if role_l == "Thai":
            self.lbl_head.config(text="อุ๊ย! ไฟล์ของคุณถูกเข้ารหัสแล้ว!")
            self.pay_on_lbl.config(text="จะเพิ่มค่าไถ่ในวันที่")
            self.lost_on_lbl.config(text="ไฟล์จะถูกลบในวันที่")
            self.time_l1.config(text="เวลาที่เหลือ")
            self.time_l2.config(text="เวลาที่เหลือ")
            self.tip_lbl.config(text="ส่งเงิน $300 MAGIC ไปที่ที่อยู่นี้:")
            self.btn_check.config(text="ตรวจสอบการชำระ")
            self.btn_decrypt.config(text="ถอดรหัส")
            self.lk1.config(text="เกี่ยวกับบิทคอยน์")
            self.lk2.config(text="ซื้อบิทคอยน์อย่างไร?")
            self.lk3.config(text="ติดต่อเรา")
        else:
            self.lbl_head.config(text="Ooops, your files have been encrypted!")
            self.pay_on_lbl.config(text="Payment will be raised on")
            self.lost_on_lbl.config(text="Your files will be lost on")
            # ... reset rest to English
            self.time_l1.config(text="Time Left")
            self.time_l2.config(text="Time Left")
            self.tip_lbl.config(text="Send $300 worth of MAGIC to this address:")
            self.btn_check.config(text="Check Payment")
            self.btn_decrypt.config(text="Decrypt")
            self.lk1.config(text="About bitcoin")
            self.lk2.config(text="How to buy bitcoins?")
            self.lk3.config(text="Contact Us")

    def copy_address(self):
        if pyperclip: pyperclip.copy(self.addr)
        else:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.addr)
        messagebox.showinfo("MAGIC", "Address copied to clipboard!")

    def cleanup(self):
        files = ["NOC_CONFIG.kamai", "NOC_GATEWAY_ACCESS.txt", "MAGIC_YAIMAK.jpg", 
                 "IT_TICKET.kamai", "GIT_RECOVERY_LOG.txt", "You force-pushed to main-Bold strategy.jpg"]
        for f in files:
            p = os.path.join(self.DESKTOP, f)
            try:
                if os.path.exists(p): os.remove(p)
            except: pass

    def update_timers(self):
        def loop():
            h, m, s = 23, 20, 54
            while True:
                try:
                    self.cnt1.config(text=f"02:23:{m:02d}:{s:02d}")
                    self.cnt2.config(text=f"06:23:{m:02d}:{s:02d}")
                    s -= 1
                    if s < 0: s=59; m-=1
                    time.sleep(1)
                except: break
        threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app_root = tk.Tk()
    app_instance = KamaiGuardianJourney(app_root)
    app_root.mainloop()