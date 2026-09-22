import os

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------- ตั้งค่าหน้าเว็บ ----------
st.set_page_config(page_title="แดชบอร์ดเกรดนักศึกษา", page_icon="🎓", layout="centered")

# ---------- ค่าคงที่ ----------
# ลองหาไฟล์ตามลำดับนี้ (อยู่โฟลเดอร์เดียวกับ app.py)
CANDIDATE_FILES = ["student.csv", "st.csv"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GRADE_ORDER = ["A", "B+", "B", "C+", "C", "D+", "D", "F"]
GRADE_COLORS = {
    "A": "#0068c9",
    "B+": "#29b09d",
    "B": "#7defa1",
    "C+": "#83c9ff",
    "C": "#ffd16a",
    "D+": "#ff2b2b",
    "D": "#ff8700",
    "F": "#ffabab",
}


def calc_grade(score):
    """แปลงคะแนนเป็นเกรด (ใช้เมื่อไฟล์ยังไม่มีคอลัมน์เกรด)"""
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


@st.cache_data
def load_data():
    """อ่าน CSV แล้วตั้งชื่อคอลัมน์ตามตำแหน่ง (รองรับทั้งหัวตารางภาษาไทยและอังกฤษ)"""
    path = next(
        (os.path.join(BASE_DIR, f) for f in CANDIDATE_FILES if os.path.exists(os.path.join(BASE_DIR, f))),
        None,
    )
    if path is None:
        return None, None

    df = pd.read_csv(path, encoding="utf-8-sig", dtype={0: str})
    df = df.iloc[:, :4].copy()
    names = ["Student_ID", "Student_Name", "Student_Score", "Student_Grade"]
    df.columns = names[: df.shape[1]]

    df["Student_Score"] = pd.to_numeric(df["Student_Score"])
    if "Student_Grade" not in df.columns:
        df["Student_Grade"] = df["Student_Score"].apply(calc_grade)
    return df, os.path.basename(path)


df, file_name = load_data()

# ---------- หัวข้อ ----------
st.title("🎓 แดชบอร์ดนำเสนอข้อมูลเกรดนักศึกษา")

if df is None:
    st.error(f"ไม่พบไฟล์ข้อมูล ({' หรือ '.join(CANDIDATE_FILES)}) ในโฟลเดอร์เดียวกับ app.py")
    st.stop()

st.caption(f"ระบบอ่านไฟล์ {file_name} คำนวณเกรด และนำเสนอผลในรูปแบบแดชบอร์ดบนเครื่องมือ Streamlit")

# ---------- ตัวเลขสรุป ----------
total = len(df)
avg_score = df["Student_Score"].mean()
max_score = df["Student_Score"].max()
min_score = df["Student_Score"].min()
pass_rate = (df["Student_Grade"] != "F").sum() / total * 100

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("จำนวนนักเรียน", f"{total} คน")
c2.metric("คะแนนเฉลี่ย", f"{avg_score:.2f}")
c3.metric("คะแนนสูงสุด", f"{max_score:g}")
c4.metric("คะแนนต่ำสุด", f"{min_score:g}")
c5.metric("ผ่านเกณฑ์", f"{pass_rate:.2f}%")

st.divider()

# ---------- ตารางผลการเรียน ----------
st.subheader("📋 รายงานผลการเรียน")
st.dataframe(df, hide_index=True)

# ---------- กราฟ ----------
counts = (
    df["Student_Grade"]
    .value_counts()
    .reindex(GRADE_ORDER, fill_value=0)
    .rename_axis("เกรด")
    .reset_index(name="จำนวน (คน)")
)

left, right = st.columns(2)

with left:
    st.subheader("📊 จำนวนผู้เรียนตามเกรด")
    bar = px.bar(counts, x="เกรด", y="จำนวน (คน)", text="จำนวน (คน)")
    bar.update_traces(marker_color="#0068c9", textposition="outside")
    bar.update_layout(margin=dict(t=20, b=20), yaxis=dict(dtick=1))
    st.plotly_chart(bar)

with right:
    st.subheader("🍩 สัดส่วนผู้เรียนตามเกรด")
    present = counts[counts["จำนวน (คน)"] > 0]  # แสดงเฉพาะเกรดที่มีคน
    pie = px.pie(
        present,
        names="เกรด",
        values="จำนวน (คน)",
        hole=0.4,
        color="เกรด",
        color_discrete_map=GRADE_COLORS,
        category_orders={"เกรด": GRADE_ORDER},
    )
    pie.update_traces(textinfo="label+percent", sort=False)
    pie.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(pie)