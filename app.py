import streamlit as st
import sqlite3
import hashlib
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.efficientnet import preprocess_input
from PIL import Image
import gdown
import os

# -----------------------------
# HIDE STREAMLIT HEADER & FOOTER
# -----------------------------
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# -----------------------------
# DOWNLOAD MODEL FROM DRIVE
# -----------------------------
MODEL_PATH = "newmodel.h5"
FILE_ID = "1sIAR8rj37TC7bmBFI38-oaI8xZ22xXs2"

@st.cache_resource
def load_my_model():
    if not os.path.exists(MODEL_PATH):
        url = f"https://drive.google.com/uc?id={FILE_ID}"
        gdown.download(url, MODEL_PATH, quiet=False)
    return load_model(MODEL_PATH, compile=False)

# -----------------------------
# DATABASE SETUP
# -----------------------------
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")
conn.commit()

# -----------------------------
# PASSWORD HASHING
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -----------------------------
# REGISTER FUNCTION
# -----------------------------
def register_user(username, password):
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, hash_password(password)))
        conn.commit()
        return True
    except:
        return False

# -----------------------------
# LOGIN FUNCTION
# -----------------------------
def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone()

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Pest Detection App")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "show_register" not in st.session_state:
    st.session_state.show_register = False

# -----------------------------
# LOGIN / REGISTER SCREEN
# -----------------------------
if not st.session_state.logged_in:

    st.title("🌿 Pest Detection System")

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password")

    with col2:
        if st.button("Register"):
            st.session_state.show_register = True

    # REGISTER FORM
    if st.session_state.show_register:
        st.subheader("Create New Account")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if register_user(new_user, new_pass):
                st.success("Account created successfully!")
                st.session_state.show_register = False
            else:
                st.error("Username already exists!")

# -----------------------------
# MAIN APP AFTER LOGIN
# -----------------------------
else:
    st.title("🌿 Pest Detection System")

    model = load_my_model()

    class_names = [
        'class1','class2','class3','class4',
        'class5','class6','class7','class8','class9'
    ]

    uploaded_file = st.file_uploader(
        "Upload Pest Image",
        type=["jpg", "png", "jpeg"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)

        if st.button("Predict"):
            image = image.resize((380, 380))
            img_array = np.array(image)
            img_array = preprocess_input(img_array)
            img_array = np.expand_dims(img_array, axis=0)

            predictions = model.predict(img_array)
            predicted_class = class_names[np.argmax(predictions)]
            confidence = float(np.max(predictions)) * 100

            st.success(f"Prediction: {predicted_class}")
            st.info(f"Confidence: {confidence:.2f}%")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
