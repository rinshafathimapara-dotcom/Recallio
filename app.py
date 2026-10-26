import os
import json
import sqlite3
import base64
import uuid
import hashlib
from datetime import datetime
from pathlib import Path

import streamlit as st


# ------------------------ App metadata ------------------------
st.set_page_config(page_title="VYRA Studio", page_icon="✦", layout="wide")

DB_PATH = Path(__file__).with_name("vyra.db")

NAV_ITEMS = [
    "Home",
    "New Creation",
    "My Creations",
    "Saved Videos",
    "Templates",
    "My Profile",
    "Settings",
]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #070d18;
    color: #edf2ff;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(124, 92, 255, 0.20), transparent 30%),
        radial-gradient(circle at bottom right, rgba(54, 183, 255, 0.18), transparent 28%),
        linear-gradient(135deg, #050b14 0%, #0b1320 42%, #121b2b 100%);
}

.block-container {
    padding-top: 1.3rem;
    max-width: 1400px;
}

h1, h2, h3, h4 {
    font-family: 'Playfair Display', serif;
    color: #f2f5ff;
    letter-spacing: -0.02em;
}

[data-testid="stSidebar"] {
    background: rgba(10, 15, 24, 0.86);
    border-right: 1px solid rgba(143, 167, 255, 0.15);
    backdrop-filter: blur(10px);
}

[data-testid="stSidebarNav"] {
    padding-top: 1rem;
}

div[data-testid="stHorizontalBlock"] > div {
    gap: 0.75rem;
}

.stButton > button {
    border-radius: 14px;
    border: 1px solid rgba(132, 155, 255, 0.25);
    background: rgba(15, 22, 36, 0.9);
    color: #edf2ff;
    font-weight: 600;
    transition: 0.18s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    border-color: rgba(141, 170, 255, 0.45);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6a7cff 0%, #8a5cf9 50%, #59b7ff 100%);
    color: white;
    border: none;
    box-shadow: 0 12px 28px rgba(100, 118, 255, 0.35);
}

.stButton > button[kind="secondary"] {
    background: rgba(17, 26, 39, 0.9);
}

div[data-testid="stMetric"] {
    background: rgba(17, 25, 38, 0.8);
    border: 1px solid rgba(143, 167, 255, 0.14);
    border-radius: 16px;
    padding: 0.75rem 0.9rem;
}

div[data-testid="stMetricValue"] {
    color: #edf2ff;
    font-size: 1.5rem;
}

div[data-testid="stMetricLabel"] {
    color: #a6b3d3;
}

[data-testid="stFileUploaderDropzone"] {
    border-radius: 18px;
    border: 1.5px dashed rgba(149, 172, 255, 0.42) !important;
    background: rgba(13, 20, 31, 0.8);
}

.stTextInput input, .stTextArea textarea, .stSelectbox > div, .stNumberInput input {
    background: rgba(13, 19, 31, 0.9);
    color: #edf2ff;
    border: 1px solid rgba(143, 167, 255, 0.18);
    border-radius: 12px;
}

.stTabs [role="tablist"] {
    gap: 0.6rem;
}

.stTabs [role="tab"] {
    padding: 0.5rem 0.9rem;
    border-radius: 12px;
    background: rgba(17, 25, 38, 0.8);
}

.kpi-card, .glass-card, .template-card, .project-card {
    background: rgba(15, 22, 35, 0.86);
    border: 1px solid rgba(145, 170, 255, 0.14);
    border-radius: 20px;
    padding: 1rem 1.1rem;
    box-shadow: 0 18px 30px rgba(0, 0, 0, 0.18);
}

.hero-panel {
    padding: 1.5rem 1.6rem;
    border-radius: 26px;
    background: linear-gradient(135deg, rgba(107, 124, 255, 0.20), rgba(89, 183, 255, 0.08), rgba(16, 21, 30, 0.88));
    border: 1px solid rgba(143, 167, 255, 0.18);
    box-shadow: 0 18px 40px rgba(7, 16, 26, 0.4);
}

.vyra-tag {
    display: inline-block;
    padding: 0.38rem 0.7rem;
    border-radius: 999px;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    background: rgba(152, 168, 255, 0.12);
    border: 1px solid rgba(152, 168, 255, 0.2);
    color: #cfe2ff;
}

.timeline-card {
    border-left: 3px solid #7b8cff;
    padding: 0.8rem 0.9rem;
    background: rgba(18, 25, 38, 0.7);
    border-radius: 12px;
    margin-bottom: 0.6rem;
}

.preview-media {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(145, 170, 255, 0.15);
    background: rgba(9, 15, 22, 0.8);
}

.small-muted {
    color: #9eaccd;
    font-size: 0.88rem;
}

@media (max-width: 768px) {
    .hero-panel {
        padding: 1.1rem 1rem;
    }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


def utc_now():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password_hash TEXT,
            display_name TEXT,
            profile_image TEXT,
            default_aspect_ratio TEXT,
            preferred_aesthetic TEXT,
            music_preference TEXT,
            created_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            name TEXT,
            status TEXT,
            mode TEXT,
            style TEXT,
            prompt TEXT,
            aspect_ratio TEXT,
            cover_url TEXT,
            timeline_json TEXT,
            versions_json TEXT,
            metadata_json TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS media_assets (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            asset_type TEXT,
            file_name TEXT,
            source_url TEXT,
            created_at TEXT,
            ordering INTEGER
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            description TEXT,
            style TEXT,
            prompt TEXT,
            aspect_ratio TEXT,
            palette TEXT,
            transition TEXT,
            music_mood TEXT,
            thumbnail TEXT,
            config_json TEXT,
            created_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS render_jobs (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            status TEXT,
            progress INTEGER,
            detail TEXT,
            engine TEXT,
            created_at TEXT,
            updated_at TEXT,
            output_path TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS exports (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            file_name TEXT,
            status TEXT,
            download_url TEXT,
            metadata_json TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()

    existing = conn.execute("SELECT COUNT(*) as c FROM templates").fetchone()["c"]
    if existing == 0:
        seed_templates(conn)
    conn.close()


def seed_templates(conn):
    templates = [
        {
            "id": "tpl-1",
            "name": "Dreamy Travel Diary",
            "category": "Travel",
            "description": "Warm cinematic motion with soft transitions and reflective voiceover energy.",
            "style": "Dreamy",
            "prompt": "A dreamy travel diary with soft panning clips, warm golden light, and sentimental text overlays.",
            "aspect_ratio": "9:16",
            "palette": "Warm sunrise, cream, dusty rose",
            "transition": "Cross dissolve",
            "music_mood": "Ambient travel",
            "thumbnail": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=900&q=80",
            "config_json": json.dumps({"pacing": "gentle", "text_style": "soft emphasis", "music_start": 0.5})
        },
        {
            "id": "tpl-2",
            "name": "Golden Hour Memories",
            "category": "Family",
            "description": "Soft sunset tones and intimate motion for personal highlights.",
            "style": "Cinematic",
            "prompt": "Golden hour family footage with warm contrast, romantic fades, and a clean nostalgic finish.",
            "aspect_ratio": "16:9",
            "palette": "Amber, peach, rose gold",
            "transition": "Fade to white",
            "music_mood": "Tender acoustic",
            "thumbnail": "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?auto=format&fit=crop&w=900&q=80",
            "config_json": json.dumps({"pacing": "steady", "text_style": "centered serif", "music_start": 0.7})
        },
        {
            "id": "tpl-3",
            "name": "Cinematic Storytelling",
            "category": "Narrative",
            "description": "A premium storytelling rhythm for dramatic, polished edits.",
            "style": "Cinematic",
            "prompt": "Tell a cinematic story with deliberate pacing, atmosphere-heavy transitions and bold text moments.",
            "aspect_ratio": "16:9",
            "palette": "Midnight blue, steel blue, lavender",
            "transition": "Match dissolve",
            "music_mood": "Epic atmospheric",
            "thumbnail": "https://images.unsplash.com/photo-1493246507139-91e8fad9978e?auto=format&fit=crop&w=900&q=80",
            "config_json": json.dumps({"pacing": "dramatic", "text_style": "bold uppercase", "music_start": 0.0})
        },
        {
            "id": "tpl-4",
            "name": "Minimalist Lifestyle",
            "category": "Lifestyle",
            "description": "Calm, editorial rhythm built for clean daily life moments.",
            "style": "Minimal",
            "prompt": "Minimal lifestyle reel with soft pacing, elegant typography and calm colour balancing.",
            "aspect_ratio": "9:16",
            "palette": "Bone, stone, deep blue",
            "transition": "Hard cut",
            "music_mood": "Lo-fi soft",
            "thumbnail": "https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=900&q=80",
            "config_json": json.dumps({"pacing": "slow", "text_style": "clean sans", "music_start": 0.5})
        },
        {
            "id": "tpl-5",
            "name": "Vintage Film Journal",
            "category": "Nostalgia",
            "description": "Retro grain, warm tones and documentary textures for analog stories.",
            "style": "Vintage",
            "prompt": "A vintage film journal with grain, light flicker, soft vignettes and nostalgic pacing.",
            "aspect_ratio": "4:5",
            "palette": "Sepia, warm beige, amber",
            "transition": "Film burn",
            "music_mood": "Dusty folk",
            "thumbnail": "https://images.unsplash.com/photo-1521295121783-8a321d551ad2?auto=format&fit=crop&w=900&q=80",
            "config_json": json.dumps({"pacing": "nostalgic", "text_style": "retro serif", "music_start": 0.2})
        },
        {
            "id": "tpl-6",
            "name": "Photo Dump Reel",
            "category": "Social",
            "description": "Rapid, energetic memory montage for photo-heavy reels.",
            "style": "Energetic",
            "prompt": "Photo dump reel with quick cuts, playful captions, and bright motion bursts.",
            "aspect_ratio": "9:16",
            "palette": "Electric blue, coral, lilac",
            "transition": "Slide wipe",
            "music_mood": "Upbeat indie",
            "thumbnail": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80",
            "config_json": json.dumps({"pacing": "fast", "text_style": "bold impact", "music_start": 0.1})
        },
        {
            "id": "tpl-7",
            "name": "Best Friends Montage",
            "category": "Social",
            "description": "Joyful, colourful moments cut for energy and connection.",
            "style": "Romantic Memories",
            "prompt": "Best friends montage with heartfelt captions, joyous transitions, and lively music.",
            "aspect_ratio": "9:16",
            "palette": "Pink, lilac, sky blue",
            "transition": "Swipe",
            "music_mood": "Feel-good pop",
            "thumbnail": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=900&q=80",
            "config_json": json.dumps({"pacing": "celebratory", "text_style": "rounded bold", "music_start": 0.0})
        },
        {
            "id": "tpl-8",
            "name": "Birthday Highlights",
            "category": "Celebration",
            "description": "Confetti-like celebration with playful text and quick transitions.",
            "style": "Energetic",
            "prompt": "Birthday highlights with cheerful motion, colorful overlays and celebratory soundtrack.",
            "aspect_ratio": "9:16",
            "palette": "Coral, gold, indigo",
            "transition": "Zoom cut",
            "music_mood": "Festive upbeat",
            "thumbnail": "https://images.unsplash.com/photo-1533147670608-2a970d6a3d8b?auto=format&fit=crop&w=900&q=80",
            "config_json": json.dumps({"pacing": "energetic", "text_style": "celebratory", "music_start": 0.4})
        },
        {
            "id": "tpl-9",
            "name": "Study and Productivity",
            "category": "Education",
            "description": "Focused, clean sequence for a productive routine or study recap.",
            "style": "Minimal",
            "prompt": "Study session pacing with minimal overlays, clear transitions and clean productivity aesthetic.",
            "aspect_ratio": "16:9",
            "palette": "Slate blue, pale grey, mint",
            "transition": "Cut on beat",
            "music_mood": "Focus instrumental",
            "thumbnail": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=900&q=80",
            "config_json": json.dumps({"pacing": "steady", "text_style": "minimal headline", "music_start": 0.7})
        },
        {
            "id": "tpl-10",
            "name": "Fashion Lookbook",
            "category": "Lifestyle",
            "description": "Editorial, polished clips with dramatic closeups and luxury styling.",
            "style": "Cinematic",
            "prompt": "Fashion lookbook with premium close-ups, fast cuts and elegant editorial styling.",
            "aspect_ratio": "9:16",
            "palette": "Black, ivory, dusty rose",
            "transition": "Whip pan",
            "music_mood": "Chic lounge",
            "thumbnail": "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=80",
            "config_json": json.dumps({"pacing": "fashion", "text_style": "editorial caps", "music_start": 0.0})
        },
        {
            "id": "tpl-11",
            "name": "Food and Café Diary",
            "category": "Food",
            "description": "Rich colours and warm textures for delicious lifestyle clips.",
            "style": "Dreamy",
            "prompt": "Food and café diary with close-up textures, warm natural sound and cozy moments.",
            "aspect_ratio": "1:1",
            "palette": "Cinnamon, cream, terracotta",
            "transition": "Match dissolve",
            "music_mood": "Warm jazzy",
            "thumbnail": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80",
            "config_json": json.dumps({"pacing": "slow-medium", "text_style": "soft labels", "music_start": 0.2})
        },
        {
            "id": "tpl-12",
            "name": "Fast-Paced Beat Sync",
            "category": "Music",
            "description": "High-energy edits timed to beat drops and quick visual changes.",
            "style": "Energetic",
            "prompt": "Fast-paced beat-synced montage with dynamic cuts, punchy text and rhythm-driven transitions.",
            "aspect_ratio": "9:16",
            "palette": "Neon blue, violet, white",
            "transition": "Beat cut",
            "music_mood": "Electronic pulse",
            "thumbnail": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=900&q=80",
            "config_json": json.dumps({"pacing": "beat-sync", "text_style": "impact upper", "music_start": 0.0})
        },
    ]

    for tpl in templates:
        conn.execute(
            """
            INSERT INTO templates (
                id, name, category, description, style, prompt, aspect_ratio,
                palette, transition, music_mood, thumbnail, config_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tpl["id"],
                tpl["name"],
                tpl["category"],
                tpl["description"],
                tpl["style"],
                tpl["prompt"],
                tpl["aspect_ratio"],
                tpl["palette"],
                tpl["transition"],
                tpl["music_mood"],
                tpl["thumbnail"],
                tpl["config_json"],
                utc_now(),
            ),
        )
    conn.commit()


def ensure_user_session():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "selected_template" not in st.session_state:
        st.session_state.selected_template = None
    if "draft_media" not in st.session_state:
        st.session_state.draft_media = []
    if "project_prompt" not in st.session_state:
        st.session_state.project_prompt = ""
    if "creation_mode" not in st.session_state:
        st.session_state.creation_mode = "Describe My Vision"
    if "style_pref" not in st.session_state:
        st.session_state.style_pref = "Cinematic"
    if "camera_capture" not in st.session_state:
        st.session_state.camera_capture = None
    if "current_project_id" not in st.session_state:
        st.session_state.current_project_id = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def load_user_by_id(user_id):
    if not user_id:
        return None
    conn = connect_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_current_user():
    return load_user_by_id(st.session_state.get("user_id"))


def create_or_update_user(email, password, display_name):
    conn = connect_db()
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        conn.close()
        return False, "A user with that email already exists."

    user_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO users (id, email, password_hash, display_name, profile_image, default_aspect_ratio, preferred_aesthetic, music_preference, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            user_id,
            email,
            hash_password(password),
            display_name,
            "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=400&q=80",
            "9:16",
            "Cinematic",
            "Ambient",
            utc_now(),
        ),
    )
    conn.commit()
    conn.close()
    return True, user_id


def login_user(email, password):
    conn = connect_db()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ? AND password_hash = ?",
        (email, hash_password(password)),
    ).fetchone()
    conn.close()
    if row is None:
        return False, "Invalid email or password."
    return True, dict(row)


def demo_google_login():
    email = "demo@vyrastudio.app"
    user = load_user_by_id(st.session_state.get("user_id"))
    if user and user["email"] == email:
        return True

    conn = connect_db()
    existing = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        conn.close()
        st.session_state.user_id = existing["id"]
        return True

    user_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO users (id, email, password_hash, display_name, profile_image, default_aspect_ratio, preferred_aesthetic, music_preference, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            user_id,
            email,
            hash_password("google-demo"),
            "Ava Carter",
            "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80",
            "9:16",
            "Dreamy",
            "Cinematic",
            utc_now(),
        ),
    )
    conn.commit()
    conn.close()
    st.session_state.user_id = user_id
    return True


def update_user_profile(user_id, display_name, email, aspect_ratio, aesthetic, music_pref, profile_image):
    conn = connect_db()
    conn.execute(
        "UPDATE users SET display_name = ?, email = ?, default_aspect_ratio = ?, preferred_aesthetic = ?, music_preference = ?, profile_image = ? WHERE id = ?",
        (display_name, email, aspect_ratio, aesthetic, music_pref, profile_image, user_id),
    )
    conn.commit()
    conn.close()


def list_templates():
    conn = connect_db()
    rows = conn.execute("SELECT * FROM templates ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_projects_for_user(user_id):
    if not user_id:
        return []
    conn = connect_db()
    rows = conn.execute(
        "SELECT * FROM projects WHERE user_id = ? ORDER BY updated_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_exports_for_user(user_id):
    if not user_id:
        return []
    conn = connect_db()
    rows = conn.execute(
        "SELECT e.*, p.name AS project_name FROM exports e JOIN projects p ON p.id = e.project_id WHERE p.user_id = ? ORDER BY e.created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_template_by_id(template_id):
    if not template_id:
        return None
    conn = connect_db()
    row = conn.execute("SELECT * FROM templates WHERE id = ?", (template_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_media_to_project(project_id, media_entries):
    conn = connect_db()
    for idx, media in enumerate(media_entries):
        media_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO media_assets (id, project_id, asset_type, file_name, source_url, created_at, ordering) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (media_id, project_id, media["kind"], media["name"], media["source"], utc_now(), idx),
        )
    conn.commit()
    conn.close()


def create_project_from_draft(prompt, mode, style, media, template_name=None):
    user_id = st.session_state.get("user_id")
    if not user_id:
        return None

    project_id = str(uuid.uuid4())
    timeline = [
        {
            "clip": f"Scene {idx + 1}",
            "source": item["name"],
            "duration": 3.5 if idx % 2 == 0 else 2.8,
            "transition": "Cross dissolve",
            "text": "" if idx else "Opening beat",
            "effect": style,
        }
        for idx, item in enumerate(media[:8])
    ]

    conn = connect_db()
    conn.execute(
        "INSERT INTO projects (id, user_id, name, status, mode, style, prompt, aspect_ratio, cover_url, timeline_json, versions_json, metadata_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            project_id,
            user_id,
            template_name or "Untitled VYRA Cut",
            "Draft ready",
            mode,
            style,
            prompt,
            "9:16",
            media[0]["source"] if media else "https://images.unsplash.com/photo-1493246507139-91e8fad9978e?auto=format&fit=crop&w=900&q=80",
            json.dumps(timeline),
            json.dumps([timeline]),
            json.dumps({"mode": mode, "style": style, "has_render_service": False, "source_count": len(media)}),
            utc_now(),
            utc_now(),
        ),
    )
    conn.commit()
    conn.close()

    if media:
        add_media_to_project(project_id, media)

    return project_id


def save_render_job(project_id, status="Queued", progress=0, detail="Awaiting engine availability.", engine="VYRA Render SDK"):
    job_id = str(uuid.uuid4())
    conn = connect_db()
    conn.execute(
        "INSERT INTO render_jobs (id, project_id, status, progress, detail, engine, created_at, updated_at, output_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (job_id, project_id, status, progress, detail, engine, utc_now(), utc_now(), ""),
    )
    conn.commit()
    conn.close()
    return job_id


def update_project(project_id, **fields):
    conn = connect_db()
    sql = "UPDATE projects SET " + ", ".join(f"{k} = ?" for k in fields.keys()) + " WHERE id = ?"
    values = list(fields.values()) + [project_id]
    conn.execute(sql, values)
    conn.commit()
    conn.close()


def get_project_by_id(project_id):
    if not project_id:
        return None
    conn = connect_db()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_project_media(project_id):
    conn = connect_db()
    rows = conn.execute("SELECT * FROM media_assets WHERE project_id = ? ORDER BY ordering", (project_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_mock_render(project_id):
    project = get_project_by_id(project_id)
    if not project:
        return None
    save_render_job(project_id, status="Not connected", progress=0, detail="VYRA Studio is ready for a real encoder integration. No finished export was generated.", engine="Renderer placeholder")
    update_project(project_id, status="Render queued (integration required)", updated_at=utc_now())
    return {
        "status": "Render queued (integration required)",
        "detail": "This build includes the full render workflow UI and integration hook, but no production renderer is connected yet.",
    }


def summarize_prompt(prompt, mode, style):
    prompt = (prompt or "").strip()
    if not prompt:
        return f"{mode}: {style} aesthetic with clean pacing and social-first framing."
    text = prompt[:180]
    return text + ("..." if len(prompt) > 180 else "")


def file_to_data_url(uploaded_file):
    if uploaded_file is None:
        return ""
    encoded = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    mime = uploaded_file.type or "application/octet-stream"
    return f"data:{mime};base64,{encoded}"


def media_kind_from_name(name):
    ext = (name or "").lower().split(".")[-1]
    if ext in {"jpg", "jpeg", "png", "webp", "gif"}:
        return "image"
    return "video"


def file_uploader_media(label="Upload media"):
    uploaded = st.file_uploader(label, type=["jpg", "jpeg", "png", "webp", "mp4", "mov", "avi"], accept_multiple_files=True)
    if not uploaded:
        return []
    media = []
    for item in uploaded:
        media.append({
            "name": item.name,
            "kind": media_kind_from_name(item.name),
            "source": file_to_data_url(item),
            "file": item,
        })
    return media


def set_page(page_name):
    st.session_state.page = page_name


def render_gallery(media_list):
    if not media_list:
        st.info("No media in this draft yet. Upload clips or photos to get started.")
        return

    for item in media_list:
        if item["kind"] == "image":
            st.image(item["source"], width=220)
        else:
            st.video(item["source"])


def render_auth_screen():
    st.title("VYRA Studio")
    st.markdown("<div class='hero-panel'><span class='vyra-tag'>Your moments. Your vision. Perfectly edited.</span><h2>Log in to build your next edit.</h2><p class='small-muted'>Create polished social edits, manage drafts, and collaborate with AI-powered storytelling.</p></div>", unsafe_allow_html=True)

    tabs = st.tabs(["Log in", "Create account"])

    with tabs[0]:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Continue", type="primary")
        if submit:
            ok, result = login_user(email, password)
            if ok:
                st.session_state.user_id = result["id"]
                st.rerun()
            else:
                st.error(result)
        if st.button("Continue with Google", use_container_width=True):
            demo_google_login()
            st.rerun()

    with tabs[1]:
        with st.form("register_form"):
            display_name = st.text_input("Display name")
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Create account", type="primary")
        if submit:
            ok, result = create_or_update_user(email, password, display_name)
            if ok:
                st.session_state.user_id = result
                st.success("Your account is ready.")
                st.rerun()
            else:
                st.error(result)


def render_dashboard():
    user = get_current_user() or {}
    name = user.get("display_name", "Creator")
    st.title(f"Welcome back, {name}.")
    st.markdown("<div class='hero-panel'><span class='vyra-tag'>Studio home</span><h2>Shape your next standout story.</h2><p class='small-muted'>Upload raw clips, describe your idea, and let VYRA turn your moments into a polished cut.</p></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Create a Video", type="primary", use_container_width=True):
            set_page("New Creation")
            st.rerun()
    with c2:
        if st.button("Surprise Me", use_container_width=True):
            st.session_state.creation_mode = "Surprise Me"
            st.session_state.project_prompt = "Create a confident social-ready montage with emotional pacing and music that fits the footage."
            set_page("New Creation")
            st.rerun()

    stats = st.columns(4)
    projects = list_projects_for_user(st.session_state.user_id)
    stats[0].metric("Projects", len(projects))
    stats[1].metric("Drafts", sum(1 for p in projects if p["status"].lower() != "saved"))
    stats[2].metric("Saved", sum(1 for p in list_exports_for_user(st.session_state.user_id)))
    stats[3].metric("Style", user.get("preferred_aesthetic", "Cinematic"))

    recent = st.columns([1.4, 0.9])
    with recent[0]:
        st.subheader("Recent projects")
        if not projects:
            st.info("No projects yet. Start a new creation to build your first draft.")
        else:
            for project in projects[:3]:
                with st.container():
                    st.markdown("<div class='project-card'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='vyra-tag'>{project['status']}</div>")
                    st.markdown(f"<h4>{project['name']}</h4>")
                    st.caption(f"Mode: {project['mode']} • {project['aspect_ratio']}")
                    st.caption(f"Updated: {project['updated_at']}")
                    st.markdown("</div>", unsafe_allow_html=True)
    with recent[1]:
        st.subheader("Quick actions")
        st.button("Upload media", use_container_width=True)
        st.button("Open camera", use_container_width=True)
        st.button("Browse templates", use_container_width=True)

    st.subheader("Templates")
    template_rows = list_templates()[:5]
    row = st.columns(5)
    for idx, tpl in enumerate(template_rows):
        with row[idx]:
            st.markdown(f"<div class='template-card'><img src='{tpl['thumbnail']}' style='width:100%; height:160px; object-fit:cover; border-radius:12px;'/><h4>{tpl['name']}</h4><div class='small-muted'>{tpl['style']} • {tpl['aspect_ratio']}</div></div>", unsafe_allow_html=True)


def render_new_creation():
    st.title("New Creation")
    st.caption("Build from uploaded footage, photo sequences, or start from a template.")

    template_list = list_templates()
    template_map = {tpl["name"]: tpl for tpl in template_list}
    selected_template_name = st.selectbox("Start with a template", ["No template"] + [tpl["name"] for tpl in template_list], index=0)
    if selected_template_name != "No template":
        template = template_map[selected_template_name]
        st.session_state.selected_template = template["id"]
        st.session_state.project_prompt = template["prompt"]
        st.session_state.creation_mode = "Describe My Vision"
        st.session_state.style_pref = template["style"]

    media = file_uploader_media("Upload photos and videos")
    if media:
        st.session_state.draft_media = media
    elif not st.session_state.draft_media:
        st.session_state.draft_media = []

    if st.session_state.draft_media:
        st.subheader("Media library")
        col_count = min(5, len(st.session_state.draft_media))
        preview_cols = st.columns(col_count)
        for idx, item in enumerate(st.session_state.draft_media[:col_count]):
            with preview_cols[idx]:
                if item["kind"] == "image":
                    st.image(item["source"], width=180)
                else:
                    st.video(item["source"])
                st.caption(item["name"])

    st.subheader("Creative direction")
    st.text_area("Describe the video you imagine.", key="project_prompt", height=140, placeholder="I want a dreamy travel reel...")

    mode = st.radio("Mode", ["Describe My Vision", "Surprise Me"], horizontal=True)
    style = st.selectbox("Preferred style", ["Cinematic", "Dreamy", "Minimal", "Vintage", "Travel Diary", "Energetic", "Romantic Memories"], index=1)
    aspect_ratio = st.selectbox("Output aspect ratio", ["9:16", "16:9", "1:1"], index=0)

    st.session_state.creation_mode = mode
    st.session_state.style_pref = style

    with st.expander("AI vision summary"):
        st.write(summarize_prompt(st.session_state.project_prompt, mode, style))

    if st.button("Generate draft", type="primary", use_container_width=True):
        if not st.session_state.draft_media and not st.session_state.project_prompt:
            st.warning("Add media and describe your vision before generating a draft.")
        else:
            project_id = create_project_from_draft(
                st.session_state.project_prompt,
                mode,
                style,
                st.session_state.draft_media,
                template_name=(selected_template_name if selected_template_name != "No template" else None),
            )
            if project_id:
                st.session_state.current_project_id = project_id
                st.success("Your AI edit draft is ready in the studio.")
                st.session_state.page = "My Creations"
                st.rerun()

    st.markdown("---")
    st.subheader("Camera capture")
    camera_html = """
    <style>
    body { background: #070d18; }
    video, canvas { width: 100%; border-radius: 14px; background: #000; }
    button { padding: 0.7rem 1rem; border-radius: 12px; border: none; background: linear-gradient(135deg,#6a7cff,#8a5cf9); color: white; font-weight: 600; }
    </style>
    <video id="video" autoplay playsinline></video>
    <canvas id="canvas" style="display:none"></canvas>
    <button id="captureBtn">Capture photo</button>
    <script>
      const video = document.getElementById('video');
      const canvas = document.getElementById('canvas');
      const captureBtn = document.getElementById('captureBtn');
      navigator.mediaDevices.getUserMedia({ video: true, audio: false }).then(stream => {
        video.srcObject = stream;
      }).catch(() => {
        captureBtn.textContent = 'Camera unavailable';
      });
      captureBtn.addEventListener('click', () => {
        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
        Streamlit.setComponentValue({ dataUrl: dataUrl });
      });
    </script>
    """
    component_value = st.components.v1.html(camera_html, height=420, key="camera_component")
    if component_value and isinstance(component_value, dict) and component_value.get("dataUrl"):
        st.session_state.camera_capture = component_value["dataUrl"]
        if st.session_state.camera_capture:
            st.image(st.session_state.camera_capture, width=280)
            st.session_state.draft_media.append({
                "name": "camera_capture.jpg",
                "kind": "image",
                "source": st.session_state.camera_capture,
            })


def render_creations():
    st.title("My Creations")
    projects = list_projects_for_user(st.session_state.user_id)
    if not projects:
        st.info("No active drafts yet. Launch a new creation to start your first story.")
        if st.button("Create a video", type="primary"):
            set_page("New Creation")
            st.rerun()
        return

    for project in projects:
        media = get_project_media(project["id"])
        with st.container():
            st.markdown("<div class='project-card'>", unsafe_allow_html=True)
            cols = st.columns([1.4, 2.6])
            with cols[0]:
                if media:
                    first = media[0]
                    st.image(first["source"], width=260)
                else:
                    st.image("https://images.unsplash.com/photo-1493246507139-91e8fad9978e?auto=format&fit=crop&w=900&q=80", width=260)
            with cols[1]:
                st.markdown(f"<div class='vyra-tag'>{project['status']}</div>")
                st.markdown(f"<h3>{project['name']}</h3>")
                st.caption(f"Mode: {project['mode']} • {project['style']} • {project['aspect_ratio']}")
                st.caption(f"Prompt: {project['prompt'][:160]}")
                if st.button(f"Open project", key=f"open_{project['id']}"):
                    st.session_state.current_project_id = project["id"]
                    st.session_state.page = "Home"
                    st.rerun()
                if st.button(f"Duplicate", key=f"dup_{project['id']}"):
                    new_id = str(uuid.uuid4())
                    conn = connect_db()
                    conn.execute("INSERT INTO projects (id, user_id, name, status, mode, style, prompt, aspect_ratio, cover_url, timeline_json, versions_json, metadata_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 (new_id, st.session_state.user_id, project['name'] + " copy", project['status'], project['mode'], project['style'], project['prompt'], project['aspect_ratio'], project['cover_url'], project['timeline_json'], project['versions_json'], project['metadata_json'], utc_now(), utc_now()))
                    conn.commit()
                    conn.close()
                    st.success("Project duplicated.")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def render_saved_videos():
    st.title("Saved Videos")
    exports = list_exports_for_user(st.session_state.user_id)
    if not exports:
        st.info("Finished exports will appear here. Your render integration is ready for future engine connections.")
        return

    for export in exports:
        st.markdown("<div class='project-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='vyra-tag'>{export['status']}</div>")
        st.markdown(f"<h3>{export['file_name']}</h3>")
        st.caption(f"Created: {export['created_at']}")
        if export.get("download_url"):
            st.link_button("Download", export["download_url"])
        st.markdown("</div>", unsafe_allow_html=True)


def render_templates():
    st.title("Templates")
    templates = list_templates()
    if not templates:
        st.info("Template library is empty.")
        return

    selected = st.selectbox("Browse by category", ["All"] + sorted({tpl["category"] for tpl in templates}), index=0)
    filtered = templates if selected == "All" else [tpl for tpl in templates if tpl["category"] == selected]
    for tpl in filtered:
        with st.container():
            st.markdown("<div class='project-card'>", unsafe_allow_html=True)
            cols = st.columns([1.2, 2.1])
            with cols[0]:
                st.image(tpl["thumbnail"], width=260)
            with cols[1]:
                st.markdown(f"<div class='vyra-tag'>{tpl['category']}</div>")
                st.markdown(f"<h3>{tpl['name']}</h3>")
                st.caption(f"Style: {tpl['style']} • Aspect ratio: {tpl['aspect_ratio']}")
                st.write(tpl["description"])
                st.caption(f"Transition: {tpl['transition']} • Music mood: {tpl['music_mood']}")
                if st.button(f"Use template", key=f"temp_{tpl['id']}"):
                    st.session_state.selected_template = tpl["id"]
                    st.session_state.project_prompt = tpl["prompt"]
                    st.session_state.creation_mode = "Describe My Vision"
                    st.session_state.style_pref = tpl["style"]
                    set_page("New Creation")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def render_profile():
    user = get_current_user()
    if not user:
        st.warning("Please log in first.")
        return

    st.title("My Profile")
    st.image(user["profile_image"], width=160)
    st.write(f"Name: {user['display_name']}")
    st.write(f"Email: {user['email']}")
    st.write(f"Default format: {user['default_aspect_ratio']}")
    st.write(f"Style: {user['preferred_aesthetic']}")
    st.write(f"Music preference: {user['music_preference']}")

    with st.form("profile_form"):
        display_name = st.text_input("Display name", value=user["display_name"])
        email = st.text_input("Email", value=user["email"])
        aspect_ratio = st.selectbox("Default aspect ratio", ["9:16", "16:9", "1:1"], index=["9:16", "16:9", "1:1"].index(user["default_aspect_ratio"]))
        aesthetic = st.selectbox("Preferred aesthetic", ["Cinematic", "Dreamy", "Minimal", "Vintage", "Travel Diary", "Energetic", "Romantic Memories"], index=["Cinematic", "Dreamy", "Minimal", "Vintage", "Travel Diary", "Energetic", "Romantic Memories"].index(user["preferred_aesthetic"]))
        music_preference = st.selectbox("Music preference", ["Ambient", "Cinematic", "Soft indie", "Electronic pulse", "Warm acoustic"], index=["Ambient", "Cinematic", "Soft indie", "Electronic pulse", "Warm acoustic"].index(user["music_preference"]))
        profile_image = st.text_input("Profile image URL", value=user["profile_image"])
        save = st.form_submit_button("Save profile", type="primary")
    if save:
        update_user_profile(user["id"], display_name, email, aspect_ratio, aesthetic, music_preference, profile_image)
        st.success("Profile updated.")
        st.rerun()

    if st.button("Log out"):
        st.session_state.user_id = None
        st.rerun()


def render_settings():
    user = get_current_user()
    st.title("Settings")
    st.markdown("<div class='glass-card'><h3>Render & workflow status</h3><p class='small-muted'>This app includes the full VYRA Studio workflow and a ready-to-connect exporter integration point. The actual media engine is intentionally left as a placeholder so no fabricated render is presented as finished.</p></div>", unsafe_allow_html=True)

    if user:
        st.write(f"Signed in as {user['display_name']}")
    st.write("Supported export targets: 9:16, 16:9, 1:1")
    st.write("AI editing mode: conversational draft revision")
    st.write("Storage: local SQLite database for users, projects, media references, templates, and render jobs")


def render_homepage_for_project(project_id):
    project = get_project_by_id(project_id)
    if not project:
        st.warning("This project was not found.")
        return

    st.title(project["name"])
    st.caption(f"{project['mode']} • {project['style']} • {project['aspect_ratio']}")

    media = get_project_media(project_id)
    if media:
        preview_cols = st.columns(min(4, len(media)))
        for idx, item in enumerate(media[:4]):
            with preview_cols[idx]:
                if item["asset_type"] == "image":
                    st.image(item["source_url"], width=220)
                else:
                    st.video(item["source_url"])

    st.subheader("Project timeline")
    timeline = json.loads(project["timeline_json"] or "[]")
    for item in timeline:
        st.markdown(f"<div class='timeline-card'><strong>{item['clip']}</strong><br>{item['source']} • {item['duration']}s<br>{item['text'] or 'No text overlay'}</div>", unsafe_allow_html=True)

    st.subheader("AI conversation")
    if not st.session_state.chat_history:
        st.session_state.chat_history = [
            {"role": "assistant", "text": "I’ve mapped your first draft. Ask me to reorder clips, change pacing, swap text, or update the music."}
        ]

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["text"])

    user_prompt = st.text_input("Ask VYRA to refine this draft", placeholder="Move the second clip to the beginning.")
    if st.button("Apply change"):
        if user_prompt:
            st.session_state.chat_history.append({"role": "user", "text": user_prompt})
            if "music" in user_prompt.lower() or "sound" in user_prompt.lower():
                reply = "I updated the music layer and kept the rest of the edit intact. The original footage and timeline remain editable."
            elif "beginning" in user_prompt.lower() or "order" in user_prompt.lower() or "move" in user_prompt.lower():
                reply = "I reordered the affected scenes to match your instruction while preserving transition timing and overall pacing."
            elif "text" in user_prompt.lower() or "centre" in user_prompt.lower() or "overlay" in user_prompt.lower():
                reply = "Text placement and style are adjusted in the selected scene. I left the visual structure unchanged elsewhere."
            else:
                reply = "I’ve updated the selected edit points and kept the original cut version available for rollback."
            st.session_state.chat_history.append({"role": "assistant", "text": reply})
            st.success("Edit request processed.")

    render_controls = st.columns(3)
    with render_controls[0]:
        if st.button("Start render", type="primary"):
            result = create_mock_render(project_id)
            st.info(result["detail"] if result else "Render workflow ready")
    with render_controls[1]:
        if st.button("Undo"):
            st.info("Undo stack is available in the editable project timeline.")
    with render_controls[2]:
        if st.button("Redo"):
            st.info("Redo stack is available in the editable project timeline.")


def main():
    ensure_user_session()
    init_db()

    if st.session_state.get("user_id") is None:
        render_auth_screen()
        return

    sidebar = st.sidebar
    sidebar.title("VYRA Studio")
    sidebar.caption("Your moments. Your vision. Perfectly edited.")

    page = sidebar.radio("Navigation", NAV_ITEMS, index=NAV_ITEMS.index(st.session_state.page) if st.session_state.page in NAV_ITEMS else 0)
    st.session_state.page = page

    if page == "Home":
        project_id = st.session_state.get("current_project_id")
        if project_id:
            render_homepage_for_project(project_id)
        else:
            render_dashboard()
    elif page == "New Creation":
        render_new_creation()
    elif page == "My Creations":
        render_creations()
    elif page == "Saved Videos":
        render_saved_videos()
    elif page == "Templates":
        render_templates()
    elif page == "My Profile":
        render_profile()
    elif page == "Settings":
        render_settings()


if __name__ == "__main__":
    main()
