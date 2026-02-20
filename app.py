import streamlit as st
import numpy as np
import sqlite3
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.models import load_model

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Pest Detection App", layout="centered")

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT
)
""")
conn.commit()

# -----------------------------
# LOAD MODEL
# -----------------------------
@st.cache_resource
def load_my_model():
    return load_model("model.h5")

# -----------------------------
# SESSION STATE
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "home"

if "username" not in st.session_state:
    st.session_state.username = ""

# -----------------------------
# HOME SCREEN
# -----------------------------
if not st.session_state.logged_in:

    st.title("🌿 Pest Detection System")

    if st.session_state.page == "home":

        st.markdown("### Welcome to Smart Pest Detection App")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔐 Login"):
                st.session_state.page = "login"
                st.rerun()

        with col2:
            if st.button("📝 Register"):
                st.session_state.page = "register"
                st.rerun()

    # -----------------------------
    # REGISTER PAGE
    # -----------------------------
    elif st.session_state.page == "register":

        st.subheader("Create New Account")

        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Create Account"):
            if new_user and new_pass:
                try:
                    c.execute("INSERT INTO users VALUES (?,?)", (new_user, new_pass))
                    conn.commit()
                    st.success("Account Created Successfully!")
                except:
                    st.error("Username already exists!")
            else:
                st.warning("Please fill all fields")

        if st.button("⬅ Back"):
            st.session_state.page = "home"
            st.rerun()

    # -----------------------------
    # LOGIN PAGE
    # -----------------------------
    elif st.session_state.page == "login":

        st.subheader("Login to Your Account")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login Now"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            data = c.fetchone()

            if data:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Invalid Credentials")

        if st.button("⬅ Back"):
            st.session_state.page = "home"
            st.rerun()

# -----------------------------
# MAIN APP AFTER LOGIN
# -----------------------------
else:

    st.title("🌿 Pest Detection System")
    st.write(f"Welcome, **{st.session_state.username}** 👋")

    model = load_my_model()

    class_names = [
        "aphids",
        "armyworm",
        "beetle",
        "bollworm",
        "grasshopper",
        "mites",
        "mosquito",
        "sawfly",
        "stem_borer"
    ]

    remedies = {
        "aphids": ["Spray neem oil", "Use insecticidal soap", "Remove infected leaves"],
        "armyworm": ["Apply Bt spray", "Use recommended insecticide", "Monitor crops"],
        "beetle": ["Handpick beetles", "Apply neem oil", "Use light traps"],
        "bollworm": ["Use pheromone traps", "Apply Bt spray", "Remove damaged bolls"],
        "grasshopper": ["Use garlic spray", "Install net protection", "Eco pesticides"],
        "mites": ["Spray miticide", "Increase humidity", "Remove infected leaves"],
        "mosquito": ["Remove standing water", "Use repellents", "Apply larvicides"],
        "sawfly": ["Hand remove larvae", "Apply neem oil", "Use insecticidal soap"],
        "stem_borer": ["Remove affected stems", "Apply systemic insecticide", "Use traps"]
    }

    uploaded_file = st.file_uploader("Upload Pest Image", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:

        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)

        if st.button("🔍 Predict"):

            image = image.resize((380, 380))
            img_array = np.array(image)
            img_array = preprocess_input(img_array)
            img_array = np.expand_dims(img_array, axis=0)

            predictions = model.predict(img_array)
            predicted_class = class_names[np.argmax(predictions)]
            confidence = float(np.max(predictions)) * 100

            st.success(f"Prediction: {predicted_class}")
            st.info(f"Confidence: {confidence:.2f}%")

            st.subheader("🌱 Recommended Remedies")
            for remedy in remedies[predicted_class]:
                st.write("•", remedy)

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "home"
        st.session_state.username = ""
        st.rerun()
