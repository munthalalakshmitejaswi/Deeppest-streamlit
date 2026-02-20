import streamlit as st
import sqlite3
import hashlib
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.efficientnet import preprocess_input
from PIL import Image
import gdown
import os

# -----------------------------
# DOWNLOAD MODEL FROM DRIVE
# -----------------------------
MODEL_PATH = "newmodel.h5"
FILE_ID = "https://drive.google.com/file/d/1sIAR8rj37TC7bmBFI38-oaI8xZ22xXs2/view?usp=drive_link"   # <-- REPLACE THIS

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
# STREAMLIT CONFIG
# -----------------------------
st.set_page_config(page_title="Pest Detection App")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# -----------------------------
# REGISTER PAGE
# -----------------------------
if choice == "Register":
    st.subheader("Create New Account")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Register"):
        if register_user(new_user, new_pass):
            st.success("Account created successfully!")
        else:
            st.error("Username already exists!")

# -----------------------------
# LOGIN PAGE
# -----------------------------
elif choice == "Login":
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# -----------------------------
# MAIN APP AFTER LOGIN
# -----------------------------
if st.session_state.logged_in:
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
