import streamlit as st
import pandas as pd
import re
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AI Expense Analyzer", layout="wide")
st.title("💸 AI Expense Analyzer")

# =========================
# SESSION STATE
# =========================
if "df" not in st.session_state:
    st.session_state.df = None

if "learning" not in st.session_state:
    st.session_state.learning = {}

if "selected_category" not in st.session_state:
    st.session_state.selected_category = None

# =========================
# INPUT
# =========================
text_input = st.text_area("📥 Paste your expense data here", height=300)

# =========================
# PARSER
# =========================
def parse_text(text):
    lines = text.split("\n")
    data = []
    current_date = None

    date_pattern = re.compile(
        r"(\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
        r"January|February|March|April|June|July|August|September|October|November|December)\b)|"
        r"(\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
        r"January|February|March|April|June|July|August|September|October|November|December)\s+\d{1,2}\b)|"
        r"(\b\d{1,2}[/-]\d{1,2}([/-]\d{2,4})?\b)",
        re.IGNORECASE
    )

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = date_pattern.search(line)
        if match:
            current_date = match.group()
            continue

        nums = re.findall(r"\d+\.?\d*", line)
        if not nums:
            continue

        amount = sum(float(n) for n in nums)
        description = re.sub(r"\d+\.?\d*", "", line).replace("+", "").strip()

        data.append({
            "date": current_date,
            "description": description,
            "amount": amount
        })

    return pd.DataFrame(data)

# =========================
# CATEGORY
# =========================
def categorize(desc):
    d = desc.lower()

    categories = {
        "Food": ["breakfast", "bf", "idli", "dosa", "lunch", "meal", "dinner",
                 "tea", "coffee", "snacks", "egg", "juice", "lays", "cake",
                 "ice cream", "fruits", "momo", "milkshake", "biriyani", "sprouts", "biscuit"],
        "Travel": ["petrol", "uber", "bus", "metro"],
        "Bills": ["recharge", "wifi", "withdraw"],
        "Health": ["gym", "doctor"],
        "Shopping": ["shopping", "clothes"],
        "Maintainence": ["chain lube", "bike wash", "waterwash"]
    }

    for cat, keys in categories.items():
        if any(k in d for k in keys):
            return cat

    return None

VALID_CATEGORIES = ["Food", "Travel", "Shopping", "Bills", "Health", "Personal", "Maintainence"]

# =========================
# LLM
# =========================
@st.cache_data(show_spinner=False)
def batch_llm(descriptions):
    prompt = f"""
    Classify each expense into one category:

    {VALID_CATEGORIES}

    Return ONLY a JSON list.

    Expenses:
    {descriptions}
    """

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    try:
        return json.loads(res.choices[0].message.content)
    except:
        return [None] * len(descriptions)

# =========================
# APPLY CATEGORY
# =========================
def apply_categories(df):
    categories = []
    unknown_desc = []
    unknown_idx = []

    for i, row in df.iterrows():
        desc = row["description"]

        if desc in st.session_state.learning:
            categories.append(st.session_state.learning[desc])
            continue

        cat = categorize(desc)
        if cat:
            categories.append(cat)
            continue

        categories.append(None)
        unknown_desc.append(desc)
        unknown_idx.append(i)

    if unknown_desc:
        llm_results = batch_llm(unknown_desc)
        for idx, cat in zip(unknown_idx, llm_results):
            if cat in VALID_CATEGORIES:
                categories[idx] = cat

    df["category"] = categories
    return df

# =========================
# DATE CLEANING
# =========================
def clean_date(x):
    if pd.isna(x):
        return pd.NaT

    x = str(x).strip()

    for fmt in ["%d %B", "%d %b", "%B %d", "%b %d"]:
        try:
            return pd.to_datetime(x + " 2025", format=fmt + " %Y")
        except:
            continue

    return pd.NaT

# =========================
# ANALYZE
# =========================
if st.button("🚀 Analyze"):
    df = parse_text(text_input)
    df = apply_categories(df)

    df["date"] = df["date"].apply(clean_date)

    # Clean display column
    df["Date"] = df["date"].dt.strftime("%Y-%m-%d")

    st.session_state.df = df

# =========================
# DISPLAY
# =========================
if st.session_state.df is not None:

    df = st.session_state.df

    # -------------------------
    # FIX UNKNOWN
    # -------------------------
    unknown_rows = df[df["category"].isna()]

    display_cols = ["Date", "description", "amount", "category"]

    if not unknown_rows.empty:
        st.subheader("✏️ Fix Categories")

        edited_df = st.data_editor(
            df[display_cols],
            column_config={
                "category": st.column_config.SelectboxColumn(
                    "Category",
                    options=VALID_CATEGORIES
                )
            },
            use_container_width=True
        )

        if st.button("✅ Save Fixes"):
            for i, row in edited_df.iterrows():
                st.session_state.df.loc[i, "category"] = row["category"]
                if row["category"]:
                    st.session_state.learning[row["description"]] = row["category"]

            st.success("Saved & learned!")

    else:
        st.dataframe(df[display_cols], use_container_width=True)

    # -------------------------
    # SUMMARY
    # -------------------------
    st.subheader("📊 Summary")

    summary = df.groupby("category")["amount"].sum()

    cols = st.columns(len(summary))

    for i, (cat, amt) in enumerate(summary.items()):
        if cols[i].button(f"{cat}\n₹{amt:.2f}"):
            st.session_state.selected_category = cat

    # -------------------------
    # FILTERED VIEW
    # -------------------------
    if st.session_state.selected_category:
        selected = st.session_state.selected_category
        st.subheader(f"📄 Transactions for: {selected}")

        filtered_df = df[df["category"] == selected]

        st.dataframe(
            filtered_df[display_cols],
            use_container_width=True
        )    


