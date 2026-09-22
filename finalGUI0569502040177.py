import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox

# ---------- ค่าคงที่ ----------
FILE_NAME = "st.csv"
NUM_ROWS = 5
HEADERS = ["รหัสนักศึกษา", "ชื่อ-นามสกุล", "คะแนนเก็บ"]

# บันทึกไฟล์ไว้ในโฟลเดอร์เดียวกับโปรแกรม
FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), FILE_NAME)


class StudentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("บันทึกข้อมูลนักศึกษา")
        self.resizable(False, False)

        self.entries = []  # เก็บช่องกรอกข้อมูล [แถว][คอลัมน์]
        self.create_widgets()
        self.load_existing()  # ถ้ามี st.csv อยู่แล้วให้โหลดมาแสดง

    # ---------- สร้างหน้าจอ ----------
    def create_widgets(self):
        frame = ttk.Frame(self, padding=15)
        frame.grid(row=0, column=0)

        ttk.Label(
            frame,
            text=f"กรอกข้อมูลนักศึกษา {NUM_ROWS} รายการ",
            font=("Tahoma", 14, "bold"),
        ).grid(row=0, column=0, columnspan=4, pady=(0, 10))

        # หัวตาราง
        ttk.Label(frame, text="ลำดับ", font=("Tahoma", 10, "bold")).grid(row=1, column=0, padx=5)
        for c, h in enumerate(HEADERS, start=1):
            ttk.Label(frame, text=h, font=("Tahoma", 10, "bold")).grid(row=1, column=c, padx=5, pady=3)

        # ช่องกรอกข้อมูล 5 แถว x 3 คอลัมน์
        widths = [15, 30, 10]
        for r in range(NUM_ROWS):
            ttk.Label(frame, text=str(r + 1)).grid(row=r + 2, column=0, padx=5, pady=3)
            row_entries = []
            for c in range(3):
                e = ttk.Entry(frame, width=widths[c])
                e.grid(row=r + 2, column=c + 1, padx=5, pady=3)
                row_entries.append(e)
            self.entries.append(row_entries)

        # ปุ่ม
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=NUM_ROWS + 2, column=0, columnspan=4, pady=(12, 0))
        ttk.Button(btn_frame, text="บันทึก", command=self.save).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="ล้างข้อมูล", command=self.clear).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="ออก", command=self.destroy).grid(row=0, column=2, padx=5)

        self.status = ttk.Label(frame, text=f"ไฟล์: {FILE_NAME}", foreground="gray")
        self.status.grid(row=NUM_ROWS + 3, column=0, columnspan=4, pady=(8, 0))

    # ---------- โหลดข้อมูลเดิม ----------
    def load_existing(self):
        if not os.path.exists(FILE_PATH):
            return
        try:
            with open(FILE_PATH, newline="", encoding="utf-8-sig") as f:
                rows = list(csv.reader(f))[1:]  # ข้ามหัวตาราง
            for r, row in enumerate(rows[:NUM_ROWS]):
                for c, value in enumerate(row[:3]):
                    self.entries[r][c].insert(0, value)
        except Exception as ex:
            messagebox.showwarning("แจ้งเตือน", f"อ่านไฟล์เดิมไม่ได้: {ex}")

    # ---------- ล้างข้อมูล ----------
    def clear(self):
        for row in self.entries:
            for e in row:
                e.delete(0, tk.END)
        self.entries[0][0].focus()

    # ---------- บันทึกข้อมูล ----------
    def save(self):
        data = []
        for r, row in enumerate(self.entries, start=1):
            sid = row[0].get().strip()
            name = row[1].get().strip()
            score = row[2].get().strip()

            # ตรวจสอบว่ากรอกครบ
            if not sid or not name or not score:
                messagebox.showerror("ข้อมูลไม่ครบ", f"กรุณากรอกข้อมูลรายการที่ {r} ให้ครบทุกช่อง")
                return

            # ตรวจสอบว่าคะแนนเป็นตัวเลข
            try:
                float(score)
            except ValueError:
                messagebox.showerror("ข้อมูลไม่ถูกต้อง", f"คะแนนเก็บของรายการที่ {r} ต้องเป็นตัวเลข")
                return

            data.append([sid, name, score])

        # ตรวจสอบรหัสนักศึกษาซ้ำ
        ids = [d[0] for d in data]
        if len(set(ids)) != len(ids):
            messagebox.showerror("ข้อมูลซ้ำ", "พบรหัสนักศึกษาซ้ำกัน กรุณาตรวจสอบอีกครั้ง")
            return

        try:
            # utf-8-sig ทำให้เปิดใน Excel แล้วภาษาไทยไม่เพี้ยน
            with open(FILE_PATH, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(HEADERS)
                writer.writerows(data)
        except Exception as ex:
            messagebox.showerror("ผิดพลาด", f"บันทึกไฟล์ไม่สำเร็จ: {ex}")
            return

        self.status.config(text=f"บันทึกสำเร็จ → {FILE_PATH}", foreground="green")
        messagebox.showinfo("สำเร็จ", f"บันทึกข้อมูล {NUM_ROWS} รายการลงไฟล์ {FILE_NAME} เรียบร้อยแล้ว")


if __name__ == "__main__":
    StudentApp().mainloop()