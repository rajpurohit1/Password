import streamlit as st
import pandas as pd
import os
import random

# ------------------ Helper Functions ------------------

def get_original_data():
    return {
        'A': 54, 'B': 11, 'C': 10, 'D': 30, 'E': 50, 'F': 101, 'G': 85, 'H': 33, 'I': 102, ' ': 108, 'J': 69,
        'K': 107, 'L': 37, 'M': 72, 'N': 65, 'O': 75, 'P': 7, 'Q': 61, 'R': 52, 'S': 17, 'T': 87,
        'U': 12, 'V': 64, 'W': 60, 'X': 13, 'Y': 53, 'Z': 29,
        'a': 3, 'b': 71, 'c': 51, 'd': 44, 'e': 19, 'f': 42, 'g': 55, 'h': 88, 'i': 21, 'j': 98,
        'k': 104, 'l': 82, 'm': 56, 'n': 80, 'o': 31, 'p': 66, 'q': 6, 'r': 93, 's': 81, 't': 91,
        'u': 48, 'v': 23, 'w': 96, 'x': 83, 'y': 90, 'z': 78,
        '1': 63, '2': 84, '3': 24, '4': 58, '5': 79, '6': 14, '7': 103, '8': 67, '9': 16, '0': 109,
        '!': 9, '"': 99, '#': 59, '$': 94, '%': 74, '&': 100, "'": 105, '(': 62, ')': 76, '*': 27,
        '+': 92, ',': 5, '-': 18, '.': 36, '/': 73, ':': 97, ';': 86, '<': 4, '=': 57, '>': 106,
        '?': 40, '@': 95, '[': 25, '\\': 22, ']': 39, '^': 8, '_': 45, '`': 77, '{': 89, '|': 68,
        '}': 32, '~': 70
    }

def modify_data_dict(a, b, c):
    original_keys = list(get_original_data().keys())
    values = list(range(1, len(original_keys) + 1))
    seed = a * 100 + b * 10 + c
    random.seed(seed)
    random.shuffle(values)
    return dict(zip(original_keys, values))

def encode(text, data):
    return "-".join(str(data.get(char, "?")) for char in text)

def decode(code, reverse_data):
    decoded = ""
    parts = code.split("-")
    for part in parts:
        if part.isdigit() and int(part) in reverse_data:
            decoded += reverse_data[int(part)]
        else:
            decoded += "?"
    return decoded

def load_user_sheet(username):
    file_path = "encoded_data.xlsx"
    if os.path.exists(file_path):
        xls = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
        return xls.get(username, pd.DataFrame(columns=["Platform", "Password"]))
    else:
        return pd.DataFrame(columns=["Platform", "Password"])

def save_user_sheet(username, df):
    file_path = "encoded_data.xlsx"
    if os.path.exists(file_path):
        xls = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
    else:
        xls = {}
    xls[username] = df
    with pd.ExcelWriter(file_path, engine="openpyxl", mode="w") as writer:
        for sheet_name, sheet_df in xls.items():
            sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)

# ------------------ Streamlit App ------------------

st.set_page_config(page_title="Lock & Key", page_icon="🔐", layout="centered")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🔐 Lock & Key</h1>", unsafe_allow_html=True)

with st.expander("Enter PIN to Start", expanded=True):
    st.markdown("### Enter your 3-digit PIN and Username")
    username = st.text_input("👤 Username")
    col1, col2, col3 = st.columns(3)
    with col1:
        a = st.number_input("Digit A", min_value=0, value=1)
    with col2:
        b = st.number_input("Digit B", min_value=0, value=3)
    with col3:
        c = st.number_input("Digit C", min_value=0, value=3)

    if st.button("Log-in"):
        if username.strip() == "":
            st.error("Please enter a valid username.")
        else:
            st.session_state["unlocked"] = True
            st.session_state["username"] = username.strip()
            st.session_state["data_dict"] = modify_data_dict(a, b, c)
            st.success(f"Unlocked successfully for user: {username}!")

if st.session_state.get("unlocked"):
    st.markdown("---")
    st.markdown("### ➕ Add New Password and Id")
    platform = st.text_input("🌐 Platform Name")
    password = st.text_input("🔒 Password", type="password")

    if st.button("💾 Add"):
        data_dict = st.session_state["data_dict"]
        encoded_platform = encode(platform, data_dict)
        encoded_password = encode(password, data_dict)
        df = load_user_sheet(st.session_state["username"])
        df.loc[len(df)] = [encoded_platform, encoded_password]
        save_user_sheet(st.session_state["username"], df)
        st.success("✅ Saved successfully!")

    st.markdown("---")
    st.markdown("### 📋 View All Decoded Data")
    if st.button("👁️ Show All ID password"):
        df = load_user_sheet(st.session_state["username"])
        reverse_data = {v: k for k, v in st.session_state["data_dict"].items()}
        decoded_rows = []
        for index, row in df.iterrows():
            decoded_platform = decode(str(row["Platform"]), reverse_data)
            decoded_password = decode(str(row["Password"]), reverse_data)
            decoded_rows.append({"Platform": decoded_platform, "Password": decoded_password})
        decoded_df = pd.DataFrame(decoded_rows)
        st.dataframe(decoded_df, use_container_width=True)
