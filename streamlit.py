

import streamlit as st
from pathlib import Path
import sys
import time
import sqlite3
import hashlib
import os

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.config.config import Config
from src.document_ingestion.document_processor import DocumentProcessor
from src.vectorstore.vectorstore import VectorStore
from src.graph_builder.graph_builder import GraphBuilder

# --- DATABASE LOGIC ---
class UserDatabase:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL
                )
            """)
            conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(str.encode(password)).hexdigest()

    def create_user(self, username, password):
        try:
            with sqlite3.connect(self.db_path) as conn:
                hashed_pw = self.hash_password(password)
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username, password):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            hashed_pw = self.hash_password(password)
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
            return cursor.fetchone() is not None

# --- UTILITY FUNCTIONS ---
def is_relevant(question, subject):
    q = question.lower()
    s = subject.lower()
    
    # 1. Subject-specific keywords & aliases
    domain_map = {
        "machine learning": ["ml", "regression", "classification", "supervised", "unsupervised", "svm", "random forest", "scikit"],
        "deep learning": ["dl", "neural", "cnn", "rnn", "transformer", "pytorch", "tensorflow", "weights", "bias"],
        "python": ["py", "pandas", "numpy", "dataframe", "list", "dictionary", "function", "class", "pip", "def "]
    }

    # 2. STRICT CHECK: Does the question contain keywords from OTHER domains?
    # If I'm in AI, and the question is clearly about Python, block it.
    for other_subject, keywords in domain_map.items():
        if other_subject != s:
            if any(key in q for key in keywords):
                return False

    # 3. DOMAIN CHECK: Does it match the current subject?
    subject_words = [word for word in s.split() if len(word) > 2]
    matches_current_title = any(word in q for word in subject_words)
    matches_current_map = s in domain_map and any(keyword in q for keyword in domain_map[s])

    if matches_current_title or matches_current_map:
        return True

    # 4. REMOVED the generic "starters" check because it was causing the leak.
    # Instead, we only allow generic questions if they don't trigger other domains.
    generic_starters = ["how", "what", "explain", "why", "code", "show me", "implement"]
    is_generic = any(q.startswith(word) for word in generic_starters)
    
    # Only allow generic if it's not explicitly mentioning another subject's keywords
    return is_generic

# --- INITIALIZATION ---
db = UserDatabase()

st.set_page_config(
    page_title="🤖 SAGE: Learning Assistant",
    page_icon="🎓",
    layout="wide"
)

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'subjects' not in st.session_state:
        st.session_state.subjects = ["Machine Learning", "Deep Learning"]
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    if 'history' not in st.session_state:
        st.session_state.history = {} 

@st.cache_resource
def initialize_rag():
    try:
        llm = Config.get_llm()
        doc_processor = DocumentProcessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        vector_store = VectorStore()
        documents = doc_processor.process_urls(Config.DEFAULT_URLS)
        vector_store.create_vectorstore(documents)
        
        graph_builder = GraphBuilder(
            retriever=vector_store.get_retriever(),
            llm=llm
        )
        graph_builder.build()
        return graph_builder, len(documents)
    except Exception as e:
        st.error(f"Failed to initialize RAG: {str(e)}")
        return None, 0

# --- UI COMPONENTS ---
def login_page():
    st.title("🔐 SAGE Portal")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if db.verify_user(user, pw):
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error("Invalid credentials")
                    
    with tab2:
        with st.form("signup_form"):
            new_user = st.text_input("New Username")
            new_pw = st.text_input("New Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Create Account"):
                if new_pw == confirm and len(new_pw) >= 4:
                    if db.create_user(new_user, new_pw):
                        st.success("Account created! Login to continue.")
                    else:
                        st.error("User already exists")
                else:
                    st.error("Check password length or matching")

def main_app():
    with st.sidebar:
        st.title(f"👋 {st.session_state.username}")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()
            
        st.divider()
        st.subheader("📚 Learning Modules")
        new_sub = st.text_input("Add Subject:", placeholder="e.g. Computer Vision")
        if st.button("➕ Create") and new_sub:
            sub_name = new_sub.strip().title()
            if sub_name not in st.session_state.subjects:
                st.session_state.subjects.append(sub_name)
                st.rerun()
        
        st.divider()
        if not st.session_state.initialized:
            if st.button("🚀 Boot RAG Engine"):
                with st.spinner("Loading AI..."):
                    rag_system, _ = initialize_rag()
                    if rag_system:
                        st.session_state.rag_system = rag_system
                        st.session_state.initialized = True
                        st.rerun()
        else:
            st.success("RAG Engine Online")

    st.title("🔍 Multi-Subject Tutoring Agent")

    if not st.session_state.initialized:
        st.info("Please click 'Boot RAG Engine' in the sidebar to start learning.")
        return

    tabs = st.tabs(st.session_state.subjects)

    for i, subject in enumerate(st.session_state.subjects):
        with tabs[i]:
            st.header(f"{subject} Environment")
            question = st.chat_input(f"Ask SAGE about {subject}...", key=f"chat_{subject}")

            if question:
                # 1. RUN GUARDRAIL
                if not is_relevant(question, subject):
                    st.error(f"🚫 **Topic Mismatch**")
                    st.warning(f"This doesn't seem related to **{subject}**. Try switching tabs or being more specific.")
                    
                    # Suggest other tabs if keywords match
                    suggested = [s for s in st.session_state.subjects if s.lower() in question.lower()]
                    if suggested:
                        st.info(f"💡 Try the **{suggested[0]}** tab!")
                else:
                    # 2. RUN AGENTIC RAG
                    with st.spinner(f"Analyzing {subject} data..."):
                        # We give the LLM specific instructions about the current subject
                        isolated_prompt = (
                            f"### SYSTEM CONTEXT: You are an expert in {subject}.\n"
                            f"### CURRENT SUBJECT: {subject}\n"
                            f"User Question: {question}"
                        )
                        
                        try:
                            result = st.session_state.rag_system.run(isolated_prompt)
                            st.markdown(f"### 💡 Explanation")
                            st.write(result['answer'])
                            
                            # Update History
                            if subject not in st.session_state.history:
                                st.session_state.history[subject] = []
                            st.session_state.history[subject].append({"q": question, "a": result['answer']})
                        except Exception as e:
                            st.error(f"Error during retrieval: {e}")

            # 3. DISPLAY HISTORY
            if subject in st.session_state.history:
                with st.expander("📜 Recent Chat History"):
                    for item in reversed(st.session_state.history[subject][-3:]):
                        st.markdown(f"**Q:** {item['q']}")
                        st.caption(f"**A:** {item['a'][:150]}...")
                        st.divider()

def main():
    init_session_state()
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()