import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import os
import io
import random
import datetime
import zipfile
import numpy as np
import sqlite3
import time

# =================== DATABASE SETUP ===================
def init_db():
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS visitors 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  ip_address TEXT,
                  user_agent TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  sender_name TEXT,
                  message TEXT,
                  contact_info TEXT,
                  is_review BOOLEAN DEFAULT 0,
                  rating INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS admin_credentials
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT)''')
    
    # Insert default admin credentials if none exist
    c.execute("SELECT COUNT(*) FROM admin_credentials")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO admin_credentials (username, password) VALUES (?, ?)", 
                 ("admin", "admin123"))  # Change this in production!
    
    conn.commit()
    conn.close()

init_db()

# =================== VISITOR TRACKING ===================
def track_visitor():
    try:
        # Get visitor info (simplified for Streamlit sharing)
        visitor_info = {
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'ip_address': "Streamlit_Cloud",  # Actual IP not available in Streamlit sharing
            'user_agent': st.experimental_get_query_params().get("user_agent", ["Unknown"])[0]
        }
        
        conn = sqlite3.connect('visitors.db')
        c = conn.cursor()
        c.execute("INSERT INTO visitors (timestamp, ip_address, user_agent) VALUES (?, ?, ?)",
                 (visitor_info['timestamp'], visitor_info['ip_address'], visitor_info['user_agent']))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error tracking visitor: {e}")

# Track the visitor when the app loads
track_visitor()

# =================== CHAT/REVIEW SYSTEM ===================
def save_message(sender_name, message, contact_info="", is_review=False, rating=None):
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender_name, message, contact_info, is_review, rating) VALUES (?, ?, ?, ?, ?)",
             (sender_name, message, contact_info, is_review, rating))
    conn.commit()
    conn.close()

def get_messages(limit=50, is_review=None):
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    
    query = "SELECT * FROM messages"
    if is_review is not None:
        query += f" WHERE is_review = {1 if is_review else 0}"
    query += " ORDER BY timestamp DESC LIMIT ?"
    
    c.execute(query, (limit,))
    messages = c.fetchall()
    conn.close()
    return messages

def get_visitor_stats():
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    
    # Total visitors
    c.execute("SELECT COUNT(*) FROM visitors")
    total_visitors = c.fetchone()[0]
    
    # Today's visitors
    c.execute("SELECT COUNT(*) FROM visitors WHERE date(timestamp) = date('now')")
    today_visitors = c.fetchone()[0]
    
    # This week's visitors
    c.execute("SELECT COUNT(*) FROM visitors WHERE strftime('%Y-%W', timestamp) = strftime('%Y-%W', 'now')")
    week_visitors = c.fetchone()[0]
    
    conn.close()
    return {
        'total': total_visitors,
        'today': today_visitors,
        'week': week_visitors
    }

# =================== ADMIN FUNCTIONS ===================
def admin_login(username, password):
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    c.execute("SELECT * FROM admin_credentials WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

# =================== CONFIG ===================
st.set_page_config(page_title="⚡ Instant Photo Generator", layout="wide")

# Custom CSS for black/white/yellow theme
st.markdown("""
    <style>
    .main {
        background-color: #000000;
    }
    .stButton>button {
        background-color: #000000;
        color: #ffff00;
        border: 2px solid #ffff00;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background-color: #000000;
        color: white;
        border-right: 1px solid #ffff00;
    }
    .stSlider>div>div>div>div {
        background-color: #ffff00;
    }
    .stCheckbox>div>label {
        color: white !important;
    }
    .stSelectbox>div>div>select {
        color: white !important;
    }
    .stImage>img {
        border: 2px solid #ffff00;
        border-radius: 8px;
    }
    .variant-container {
        display: flex;
        overflow-x: auto;
        gap: 10px;
        padding: 10px 0;
    }
    .variant-item {
        flex: 0 0 auto;
    }
    .download-btn {
        display: block;
        margin-top: 5px;
        text-align: center;
    }
    .chat-message {
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        background-color: #1a1a1a;
    }
    .admin-message {
        background-color: #333333;
    }
    .stats-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .stat-box {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        flex: 1;
        margin: 0 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
    <div style='background-color: #000000; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 2px solid #ffff00;'>
        <h1 style='text-align: center; color: #ffff00; margin: 0;'>⚡ Instant Photo Generator</h1>
    </div>
""", unsafe_allow_html=True)

# =================== UTILS ===================
# [Keep all your existing utility functions here unchanged]
# ... (all your existing utility functions remain the same)

# =================== ADMIN SECTION ===================
def show_admin_section():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔐 Admin Login")
    
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if admin_login(username, password):
            st.session_state.admin_logged_in = True
            st.sidebar.success("Logged in successfully!")
        else:
            st.sidebar.error("Invalid credentials")
    
    if st.session_state.get('admin_logged_in'):
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🛠️ Admin Tools")
        
        if st.sidebar.button("Logout"):
            st.session_state.admin_logged_in = False
            st.experimental_rerun()
        
        if st.sidebar.button("View Messages"):
            st.session_state.admin_view = "messages"
        
        if st.sidebar.button("View Reviews"):
            st.session_state.admin_view = "reviews"
        
        if st.sidebar.button("View Visitor Stats"):
            st.session_state.admin_view = "stats"
        
        # Admin main content
        if st.session_state.get('admin_view') == "messages":
            st.markdown("### 📨 User Messages")
            messages = get_messages(is_review=False)
            for msg in messages:
                st.markdown(f"""
                <div class="chat-message">
                    <strong>{msg[2]}</strong> ({msg[1]})<br>
                    {msg[3]}<br>
                    <small>Contact: {msg[4] if msg[4] else 'Not provided'}</small>
                </div>
                """, unsafe_allow_html=True)
            
            if not messages:
                st.info("No messages yet.")
        
        elif st.session_state.get('admin_view') == "reviews":
            st.markdown("### ⭐ User Reviews")
            reviews = get_messages(is_review=True)
            for review in reviews:
                stars = "⭐" * review[6] if review[6] else ""
                st.markdown(f"""
                <div class="chat-message">
                    <strong>{review[2]}</strong> ({review[1]}) {stars}<br>
                    {review[3]}<br>
                    <small>Contact: {review[4] if review[4] else 'Not provided'}</small>
                </div>
                """, unsafe_allow_html=True)
            
            if not reviews:
                st.info("No reviews yet.")
        
        elif st.session_state.get('admin_view') == "stats":
            stats = get_visitor_stats()
            st.markdown("### 📊 Visitor Statistics")
            
            st.markdown("""
            <div class="stats-container">
                <div class="stat-box">
                    <h3>Total Visitors</h3>
                    <h1>{total}</h1>
                </div>
                <div class="stat-box">
                    <h3>Today's Visitors</h3>
                    <h1>{today}</h1>
                </div>
                <div class="stat-box">
                    <h3>This Week</h3>
                    <h1>{week}</h1>
                </div>
            </div>
            """.format(**stats), unsafe_allow_html=True)
            
            # Visitor chart (last 7 days)
            conn = sqlite3.connect('visitors.db')
            c = conn.cursor()
            c.execute("""
                SELECT date(timestamp) as day, COUNT(*) as count 
                FROM visitors 
                WHERE date(timestamp) >= date('now', '-7 days')
                GROUP BY day
                ORDER BY day
            """)
            data = c.fetchall()
            conn.close()
            
            if data:
                days, counts = zip(*data)
                st.line_chart({day: count for day, count in zip(days, counts)})
            else:
                st.info("No visitor data for the last 7 days.")

# =================== CHAT/REVIEW SECTION ===================
def show_chat_section():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 Help & Feedback")
    
    tab1, tab2 = st.sidebar.tabs(["Send Message", "Leave Review"])
    
    with tab1:
        with st.form("chat_form"):
            name = st.text_input("Your Name", key="chat_name")
            message = st.text_area("Your Message", key="chat_message")
            contact = st.text_input("Contact Info (optional)", key="chat_contact")
            
            if st.form_submit_button("Send Message"):
                if name and message:
                    save_message(name, message, contact)
                    st.sidebar.success("Message sent successfully!")
                else:
                    st.sidebar.warning("Please enter your name and message")
    
    with tab2:
        with st.form("review_form"):
            name = st.text_input("Your Name", key="review_name")
            rating = st.selectbox("Rating", [None, 1, 2, 3, 4, 5], format_func=lambda x: "⭐"*x if x else "Select")
            message = st.text_area("Your Review", key="review_message")
            contact = st.text_input("Contact Info (optional)", key="review_contact")
            
            if st.form_submit_button("Submit Review"):
                if name and message and rating:
                    save_message(name, message, contact, is_review=True, rating=rating)
                    st.sidebar.success("Thank you for your review!")
                else:
                    st.sidebar.warning("Please complete all required fields")

# =================== WHATSAPP BUTTON ===================
def show_whatsapp_button():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📱 Contact via WhatsApp")
    st.sidebar.markdown(f"""
    <a href="https://wa.me/919140588751" target="_blank" style="text-decoration: none;">
        <button style="background-color: #25D366; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; width: 100%;">
            WhatsApp Us
        </button>
    </a>
    """, unsafe_allow_html=True)

# =================== MAIN APP ===================
# Store generated images in session state to persist after download
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

# Initialize admin session
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Show admin section if logged in
if st.session_state.get('admin_logged_in'):
    show_admin_section()
else:
    # Show chat/review section for normal users
    show_chat_section()
    show_whatsapp_button()

# [Rest of your existing code for the photo generator remains unchanged]
# ... (all your existing photo generator code remains the same)
uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Settings sidebar
with st.sidebar:
    # [Keep all your existing sidebar settings code unchanged]
    # ... (all your existing sidebar settings code remains the same)

# [Keep all your existing processing and display code unchanged]
# ... (all your existing processing and display code remains the same)
