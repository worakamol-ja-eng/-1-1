import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox

# ---------- ค่าคงที่ ----------
FILE_NAME = "st.csv"
FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), FILE_NAME)
HEADERS = ["รหัสนักศึกษา", "ชื่อ-นามสกุล", "คะแนนเก็บ"]
GRADE_HEADER = "student_grade"

# ลำดับเกรด ใช้ตอนเรียงข้อมูลตามคอลัมน์เกรด
GRADE_ORDER = ["A", "B+", "B", "C+", "C", "D+", "D", "F"]

# สีธีมมืด
BG = "#1e1e1e"
BG_ROW_1 = "#252526"
BG_ROW_2 = "#1e1e1e"
BG_HEAD = "#333337"
FG = "#e6e6e6"
FG_FAIL = "#ff7b5c"
FG_MUTED = "#9a9a9a"


def calc_grade(score):
    """แปลงคะแนนเป็นเกรด"""
    if score >= 80:
        return "A"
    if score >= 75:
        return "B+"
    if score >= 70:
        return "B"
    if score >= 65:
        return "C+"
    if score >= 60:
        return "C"
    if score >= 55:
        return "D+"
    if score >= 50:
        return "D"
    return "F"


class GradeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ตารางคะแนนและเกรดนักศึกษา")
        self.configure(bg=BG)
        self.geometry("760x320")
        self.sort_reverse = {}  # จำว่าแต่ละคอลัมน์เรียงจากมากไปน้อยหรือยัง

        self.setup_style()
        self.create_widgets()
        self.load_and_grade()

    # ---------- ตั้งค่าสไตล์ตาราง ----------
    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=BG_ROW_1,
            fieldbackground=BG_ROW_1,
            foreground=FG,
            rowheight=34,
            borderwidth=0,
            font=("Tahoma", 11),
        )
        style.configure(
            "Treeview.Heading",
            background=BG_HEAD,
            foreground=FG,
            relief="flat",
            font=("Tahoma", 11, "bold"),
        )
        style.map("Treeview.Heading", background=[("active", "#44444a")])
        style.map("Treeview", background=[("selected", "#094771")])

    # ---------- สร้างหน้าจอ ----------
    def create_widgets(self):
        container = tk.Frame(self, bg=BG, highlightbackground="#555555", highlightthickness=1)
        container.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # show="tree headings" -> คอลัมน์ #0 ใช้แสดงลำดับ
        cols = ("sid", "name", "score", "grade")
        self.tree = ttk.Treeview(container, columns=cols, show="tree headings", height=5)
        self.tree.pack(fill="both", expand=True)

        self.tree.heading("#0", text="")
        self.tree.column("#0", width=60, anchor="center", stretch=False)

        titles = [HEADERS[0], HEADERS[1], HEADERS[2], GRADE_HEADER]
        anchors = ["e", "w", "e", "center"]
        widths = [140, 240, 120, 140]
        for col, title, anc, w in zip(cols, titles, anchors, widths):
            # คลิกหัวคอลัมน์เพื่อเรียงข้อมูล
            self.tree.heading(col, text=title, command=lambda c=col: self.sort_by(c))
            self.tree.column(col, anchor=anc, width=w)

        # สีแถวสลับ และสีแดงสำหรับเกรด F
        self.tree.tag_configure("odd", background=BG_ROW_1)
        self.tree.tag_configure("even", background=BG_ROW_2)
        self.tree.tag_configure("fail", foreground=FG_FAIL)

        self.status = tk.Label(self, text="", bg=BG, fg=FG_MUTED, font=("Tahoma", 9))
        self.status.pack(pady=8)

    # ---------- อ่านไฟล์ + คำนวณเกรด + บันทึกกลับ ----------
    def load_and_grade(self):
        if not os.path.exists(FILE_PATH):
            messagebox.showerror("ไม่พบไฟล์", f"ไม่พบไฟล์ {FILE_NAME}\nกรุณาบันทึกข้อมูลจากโปรแกรมแรกก่อน")
            return

        rows = []
        try:
            with open(FILE_PATH, newline="", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                next(reader, None)  # ข้ามหัวตาราง
                for row in reader:
                    if len(row) < 3:
                        continue
                    sid, name, score = row[0], row[1], float(row[2])
                    rows.append([sid, name, row[2], calc_grade(score)])
        except Exception as ex:
            messagebox.showerror("ผิดพลาด", f"อ่านไฟล์ไม่สำเร็จ: {ex}")
            return

        # บันทึกคอลัมน์ student_grade ลงไฟล์เดิม
        try:
            with open(FILE_PATH, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(HEADERS + [GRADE_HEADER])
                writer.writerows(rows)
        except Exception as ex:
            messagebox.showerror("ผิดพลาด", f"บันทึกไฟล์ไม่สำเร็จ: {ex}")
            return

        # แสดงในตาราง
        for i, (sid, name, score, grade) in enumerate(rows, start=1):
            tags = ["odd" if i % 2 else "even"]
            if grade == "F":
                tags.append("fail")
            self.tree.insert("", "end", text=str(i), values=(sid, name, score, grade), tags=tags)

        self.status.config(
            text=f"บันทึกคอลัมน์ {GRADE_HEADER} ลงไฟล์ {FILE_NAME} เรียบร้อยแล้ว | คลิกหัวคอลัมน์เพื่อเรียงข้อมูล"
        )

    # ---------- เรียงข้อมูลเมื่อคลิกหัวคอลัมน์ ----------
    def sort_by(self, col):
        def key(item_id):
            value = self.tree.set(item_id, col)
            if col == "grade":
                return GRADE_ORDER.index(value) if value in GRADE_ORDER else len(GRADE_ORDER)
            try:
                return float(value)  # รหัสและคะแนนเรียงแบบตัวเลข
            except ValueError:
                return value  # ชื่อเรียงแบบตัวอักษร

        reverse = self.sort_reverse.get(col, False)
        items = sorted(self.tree.get_children(""), key=key, reverse=reverse)

        for index, item_id in enumerate(items):
            self.tree.move(item_id, "", index)
            self.tree.item(item_id, text=str(index + 1))  # ลำดับใหม่
            # สลับสีแถวใหม่ให้ถูกต้อง โดยคงแท็ก fail ไว้
            tags = ["odd" if (index + 1) % 2 else "even"]
            if self.tree.set(item_id, "grade") == "F":
                tags.append("fail")
            self.tree.item(item_id, tags=tags)

        self.sort_reverse[col] = not reverse


if __name__ == "__main__":
    GradeApp().mainloop()