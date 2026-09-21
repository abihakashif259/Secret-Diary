import streamlit as st
import sqlite3
import hashlib
from datetime import date

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="My Secret Diary 🔐",
    page_icon="📔",
    layout="centered"
)

# =========================================================
# DATABASE
# =========================================================

DB_NAME = "secret_diary.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            pin TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT,
            mood TEXT,
            title TEXT,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()


create_database()

# =========================================================
# PASSWORD FUNCTIONS
# =========================================================

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


def get_saved_pin():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT pin FROM settings WHERE id = 1")
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None


def save_pin(pin):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR REPLACE INTO settings (id, pin) VALUES (1, ?)",
        (hash_pin(pin),)
    )

    conn.commit()
    conn.close()


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================================================
# CUSTOM STYLE
# =========================================================

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #fff7fc;
}

/* All normal text */
.stApp,
.stApp p,
.stApp span,
.stApp label,
.stApp div {
    color: #3d2945;
}

/* Headings */
h1 {
    color: #7b3f98 !important;
}

h2, h3 {
    color: #6a347f !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #f4e8fa;
}

section[data-testid="stSidebar"] * {
    color: #3d2945 !important;
}

/* Input boxes */
input,
textarea {
    color: #3d2945 !important;
    background-color: white !important;
}

/* Text inside Streamlit inputs */
.stTextInput input,
.stTextArea textarea {
    color: #3d2945 !important;
    background-color: white !important;
}

/* Select boxes */
.stSelectbox div {
    color: #3d2945 !important;
}

/* Cards */
.diary-card {
    background-color: white;
    padding: 20px;
    border-radius: 18px;
    margin: 10px 0;
    box-shadow: 0 4px 15px rgba(120, 70, 140, 0.12);
}

.diary-card * {
    color: #3d2945 !important;
}

/* Secret text */
.secret-text {
    text-align: center;
    color: #8a5a9e !important;
}

/* Buttons */
.stButton button {
    color: white !important;
    background-color: #7b3f98 !important;
    border-radius: 12px;
    border: none;
}

/* Expander */
.streamlit-expanderHeader {
    color: #3d2945 !important;
}

/* Metrics */
[data-testid="stMetricValue"] {
    color: #6a347f !important;
}

[data-testid="stMetricLabel"] {
    color: #3d2945 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGIN SCREEN
# =========================================================

saved_pin = get_saved_pin()

if not st.session_state.logged_in:

    st.markdown(
        "<h1 style='text-align:center;'>📔 My Secret Diary</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p class='secret-text'>🔐 A little private corner just for you 🌸</p>",
        unsafe_allow_html=True
    )

    st.write("")

    if saved_pin is None:

        st.subheader("🌷 Create Your Secret PIN")

        new_pin = st.text_input(
            "Create a 4–8 digit PIN",
            type="password"
        )

        confirm_pin = st.text_input(
            "Confirm your PIN",
            type="password"
        )

        if st.button("💜 Create Diary"):

            if not new_pin.isdigit():
                st.error("PIN should contain numbers only.")

            elif len(new_pin) < 4:
                st.error("PIN must contain at least 4 digits.")

            elif new_pin != confirm_pin:
                st.error("PINs do not match.")

            else:
                save_pin(new_pin)
                st.session_state.logged_in = True
                st.rerun()

    else:

        st.subheader("🔐 Welcome Back")

        pin = st.text_input(
            "Enter your secret PIN",
            type="password"
        )

        if st.button("🔓 Unlock Diary"):

            if hash_pin(pin) == saved_pin:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Wrong PIN")

    st.stop()

# =========================================================
# MAIN DIARY
# =========================================================

st.markdown(
    "<h1 style='text-align:center;'>🌸 My Secret Diary 🌸</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p class='secret-text'>✨ Your thoughts. Your memories. Your little secrets. ✨</p>",
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🌷 Diary Menu")

page = st.sidebar.radio(
    "Choose:",
    [
        "📝 New Entry",
        "📖 My Entries",
        "🔎 Search Diary",
        "📊 My Memories"
    ]
)

if st.sidebar.button("🔒 Lock Diary"):
    st.session_state.logged_in = False
    st.rerun()

# =========================================================
# NEW ENTRY
# =========================================================

if page == "📝 New Entry":

    st.header("📝 Write Today's Entry")

    entry_date = st.date_input(
        "📅 Date",
        value=date.today()
    )

    mood = st.selectbox(
        "😊 How are you feeling?",
        [
            "😊 Happy",
            "🥰 Loved",
            "😌 Calm",
            "🤩 Excited",
            "😔 Sad",
            "😡 Angry",
            "😴 Tired",
            "😰 Worried",
            "🤍 Normal"
        ]
    )

    title = st.text_input(
        "✨ Entry title",
        placeholder="Today was..."
    )

    content = st.text_area(
        "💭 Dear Diary...",
        height=250,
        placeholder="Write whatever is on your mind..."
    )

    if st.button("💾 Save Entry"):

        if not content.strip():
            st.warning("Please write something first 🌸")

        else:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO entries
                (entry_date, mood, title, content)
                VALUES (?, ?, ?, ?)
                """,
                (
                    str(entry_date),
                    mood,
                    title,
                    content
                )
            )

            conn.commit()
            conn.close()

            st.success("💜 Your secret memory has been saved!")

# =========================================================
# VIEW ENTRIES
# =========================================================

elif page == "📖 My Entries":

    st.header("📖 My Diary Entries")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, entry_date, mood, title, content
        FROM entries
        ORDER BY entry_date DESC, id DESC
    """)

    entries = cursor.fetchall()
    conn.close()

    if not entries:

        st.info("🌱 Your diary is empty. Write your first memory!")

    else:

        for entry in entries:

            entry_id, entry_date, mood, title, content = entry

            with st.expander(
                f"{mood}  {entry_date}  —  {title or 'Untitled'}"
            ):

                st.write(content)

                st.divider()

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{entry_id}"
                ):

                    conn = get_connection()
                    cursor = conn.cursor()

                    cursor.execute(
                        "DELETE FROM entries WHERE id = ?",
                        (entry_id,)
                    )

                    conn.commit()
                    conn.close()

                    st.success("Entry deleted.")
                    st.rerun()

# =========================================================
# SEARCH
# =========================================================

elif page == "🔎 Search Diary":

    st.header("🔎 Search Your Memories")

    search = st.text_input(
        "Search by title or diary text..."
    )

    if search:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT entry_date, mood, title, content
            FROM entries
            WHERE title LIKE ?
               OR content LIKE ?
            ORDER BY entry_date DESC
            """,
            (
                f"%{search}%",
                f"%{search}%"
            )
        )

        results = cursor.fetchall()
        conn.close()

        if not results:

            st.warning("No memories found 🌸")

        else:

            st.success(f"Found {len(results)} memory/memories 💜")

            for entry in results:

                entry_date, mood, title, content = entry

                st.markdown(
                    f"""
                    <div class="diary-card">
                        <h3>{mood} {title or "Untitled"}</h3>
                        <small>📅 {entry_date}</small>
                        <p>{content}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# =========================================================
# MEMORIES
# =========================================================

elif page == "📊 My Memories":

    st.header("📊 My Diary Memories")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM entries"
    )

    total_entries = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(DISTINCT entry_date) FROM entries"
    )

    days_written = cursor.fetchone()[0]

    conn.close()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "📔 Total Entries",
            total_entries
        )

    with col2:
        st.metric(
            "📅 Days Written",
            days_written
        )

    st.divider()

    st.subheader("💌 A little reminder")

    st.info(
        "Every memory you write today becomes a little piece "
        "of your story tomorrow. 🌷"
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    "<p style='text-align:center;color:#9a6aaa;'>"
    "🔐 Private • 🌸 Personal • 💜 Yours"
    "</p>",
    unsafe_allow_html=True
)
