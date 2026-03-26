# # """Streamlit UI for Agentic RAG System - Simplified Version"""

# # import streamlit as st
# # from pathlib import Path
# # import sys
# # import time

# # # Add src to path
# # sys.path.append(str(Path(__file__).parent))

# # from src.config.config import Config
# # from src.document_ingestion.document_processor import DocumentProcessor
# # from src.vectorstore.vectorstore import VectorStore
# # from src.graph_builder.graph_builder import GraphBuilder

# # # Page configuration
# # st.set_page_config(
# #     page_title="🤖 LEARNING ASSISTANT",
# #     page_icon="🔍",
# #     layout="centered"
# # )

# # # Simple CSS
# # st.markdown("""
# #     <style>
# #     .stButton > button {
# #         width: 100%;
# #         background-color: #4CAF50;
# #         color: white;
# #         font-weight: bold;
# #     }
# #     </style>
# # """, unsafe_allow_html=True)

# # def init_session_state():
# #     """Initialize session state variables"""
# #     if 'rag_system' not in st.session_state:
# #         st.session_state.rag_system = None
# #     if 'initialized' not in st.session_state:
# #         st.session_state.initialized = False
# #     if 'history' not in st.session_state:
# #         st.session_state.history = []

# # @st.cache_resource
# # def initialize_rag():
# #     """Initialize the RAG system (cached)"""
# #     try:
# #         # Initialize components
# #         llm = Config.get_llm()
# #         doc_processor = DocumentProcessor(
# #             chunk_size=Config.CHUNK_SIZE,
# #             chunk_overlap=Config.CHUNK_OVERLAP
# #         )
# #         vector_store = VectorStore()
        
# #         # Use default URLs
# #         urls = Config.DEFAULT_URLS
        
# #         # Process documents
# #         documents = doc_processor.process_urls(urls)
        
# #         # Create vector store
# #         vector_store.create_vectorstore(documents)
        
# #         # Build graph
# #         graph_builder = GraphBuilder(
# #             retriever=vector_store.get_retriever(),
# #             llm=llm
# #         )
# #         graph_builder.build()
        
# #         return graph_builder, len(documents)
# #     except Exception as e:
# #         st.error(f"Failed to initialize: {str(e)}")
# #         return None, 0

# # def main():
# #     """Main application"""
# #     init_session_state()
    
# #     # Title
# #     st.title("🔍 Ask me a question")
# #     st.markdown("Ask questions about the selected subject")
    
# #     # Initialize system
# #     if not st.session_state.initialized:
# #         with st.spinner("Loading system..."):
# #             rag_system, num_chunks = initialize_rag()
# #             if rag_system:
# #                 st.session_state.rag_system = rag_system
# #                 st.session_state.initialized = True
# #                 st.success(f"✅ System ready! ({num_chunks} document chunks loaded)")
    
# #     st.markdown("---")
    
# #     # Search interface
# #     with st.form("search_form"):
# #         question = st.text_input(
# #             "Enter your question:",
# #             placeholder="What would you like to know?"
# #         )
# #         submit = st.form_submit_button("🔍 Search")
    
# #     # Process search
# #     if submit and question:
# #         if st.session_state.rag_system:
# #             with st.spinner("Searching..."):
# #                 start_time = time.time()
                
# #                 # Get answer
# #                 result = st.session_state.rag_system.run(question)
                
# #                 elapsed_time = time.time() - start_time
                
# #                 # Add to history
# #                 st.session_state.history.append({
# #                     'question': question,
# #                     'answer': result['answer'],
# #                     'time': elapsed_time
# #                 })
                
# #                 # Display answer
# #                 st.markdown("### 💡 Answer")
# #                 st.success(result['answer'])
                
# #                 # Show retrieved docs in expander
# #                 with st.expander("📄 Source Documents"):
# #                     for i, doc in enumerate(result['retrieved_docs'], 1):
# #                         st.text_area(
# #                             f"Document {i}",
# #                             doc.page_content[:300] + "...",
# #                             height=100,
# #                             disabled=True
# #                         )
                
# #                 st.caption(f"⏱️ Response time: {elapsed_time:.2f} seconds")
    
# #     # Show history
# #     if st.session_state.history:
# #         st.markdown("---")
# #         st.markdown("### 📜 Recent Searches")
        
# #         for item in reversed(st.session_state.history[-3:]):  # Show last 3
# #             with st.container():
# #                 st.markdown(f"**Q:** {item['question']}")
# #                 st.markdown(f"**A:** {item['answer'][:200]}...")
# #                 st.caption(f"Time: {item['time']:.2f}s")
# #                 st.markdown("")

# # if __name__ == "__main__":
# #     main()

# # """Streamlit UI for Agentic RAG System - Dynamic Subject Isolation Version"""

# # import streamlit as st
# # from pathlib import Path
# # import sys
# # import time

# # # Add src to path
# # sys.path.append(str(Path(__file__).parent))

# # from src.config.config import Config
# # from src.document_ingestion.document_processor import DocumentProcessor
# # from src.vectorstore.vectorstore import VectorStore
# # from src.graph_builder.graph_builder import GraphBuilder

# # # Page configuration
# # st.set_page_config(
# #     page_title="🤖 SAGE: Subject Assistant",
# #     page_icon="🎓",
# #     layout="wide"
# # )

# # def init_session_state():
# #     """Initialize session state variables for Dynamic Subjects"""
# #     if 'subjects' not in st.session_state:
# #         # Default starting subjects
# #         st.session_state.subjects = ["Machine Learning", "Deep Learning"]
# #     if 'rag_system' not in st.session_state:
# #         st.session_state.rag_system = None
# #     if 'initialized' not in st.session_state:
# #         st.session_state.initialized = False
# #     if 'history' not in st.session_state:
# #         st.session_state.history = {} # Dict to isolate history per subject

# # @st.cache_resource
# # def initialize_rag():
# #     """Initialize the RAG system"""
# #     try:
# #         llm = Config.get_llm()
# #         doc_processor = DocumentProcessor(
# #             chunk_size=Config.CHUNK_SIZE,
# #             chunk_overlap=Config.CHUNK_OVERLAP
# #         )
# #         vector_store = VectorStore()
# #         documents = doc_processor.process_urls(Config.DEFAULT_URLS)
# #         vector_store.create_vectorstore(documents)
        
# #         graph_builder = GraphBuilder(
# #             retriever=vector_store.get_retriever(),
# #             llm=llm
# #         )
# #         graph_builder.build()
# #         return graph_builder, len(documents)
# #     except Exception as e:
# #         st.error(f"Failed to initialize: {str(e)}")
# #         return None, 0

# # def main():
# #     init_session_state()

# #     # --- SIDEBAR: SUBJECT MANAGEMENT ---
# #     with st.sidebar:
# #         st.title("🎓 SAGE Modules")
# #         st.markdown("Create and isolate your learning domains.")
        
# #         new_sub = st.text_input("Create New Subject:", placeholder="e.g. Natural Language Processing")
# #         if st.button("➕ Add Module") and new_sub:
# #             if new_sub not in st.session_state.subjects:
# #                 st.session_state.subjects.append(new_sub.title())
# #                 st.success(f"Created {new_sub.title()}")
# #                 st.rerun()
        
# #         st.divider()
# #         st.caption("System Status")
# #         if not st.session_state.initialized:
# #             if st.button("🚀 Boot RAG Engine"):
# #                 with st.spinner("Initializing Vector Store..."):
# #                     rag_system, num_chunks = initialize_rag()
# #                     if rag_system:
# #                         st.session_state.rag_system = rag_system
# #                         st.session_state.initialized = True
# #                         st.rerun()
# #         else:
# #             st.success("RAG Engine Online")

# #     # --- MAIN INTERFACE: DYNAMIC TABS ---
# #     st.title("🔍 Multi-Subject Tutoring Agent")

# #     if not st.session_state.initialized:
# #         st.info("Please click 'Boot RAG Engine' in the sidebar to start.")
# #         return

# #     # Create one tab for each subject in session state
# #     tabs = st.tabs(st.session_state.subjects)

# #     for i, subject in enumerate(st.session_state.subjects):
# #         with tabs[i]:
# #             st.header(f"{subject} Environment")
            
# #             # Isolation Awareness Logic
# #             question = st.chat_input(f"Ask a question specifically about {subject}...", key=f"chat_{subject}")

# #             if question:
# #                 # 1. SUBJECT AWARENESS CHECK (Frontend Guardrail)
# #                 # We tell the agent which subject context we are in
# #                 with st.spinner(f"SAGE is analyzing {subject} docs..."):
                    
# #                     # Add subject context to the prompt dynamically
# #                     isolated_prompt = f"### CONTEXT: YOU ARE IN THE {subject.upper()} MODULE.\nUser Question: {question}"
                    
# #                     start_time = time.time()
# #                     result = st.session_state.rag_system.run(isolated_prompt)
# #                     elapsed_time = time.time() - start_time

# #                     # 2. ISOLATION VALIDATION
# #                     # Simple check: If the LLM mentions a different subject from the list, warn the user
# #                     other_subjects = [s for s in st.session_state.subjects if s != subject]
# #                     found_other = [s for s in other_subjects if s.lower() in question.lower()]

# #                     if found_other:
# #                         st.warning(f"⚠️ Note: You asked about **{found_other[0]}**, but you are currently in the **{subject}** tab. Results may be filtered or limited.")

# #                     # Display Result
# #                     st.markdown(f"### 💡 {subject} Insights")
# #                     st.write(result['answer'])
                    
# #                     # Store in subject-specific history
# #                     if subject not in st.session_state.history:
# #                         st.session_state.history[subject] = []
# #                     st.session_state.history[subject].append({
# #                         "q": question, "a": result['answer'], "time": elapsed_time
# #                     })

# #             # --- SUBJECT-SPECIFIC HISTORY ---
# #             if subject in st.session_state.history:
# #                 with st.expander(f"📜 {subject} Chat History"):
# #                     for item in reversed(st.session_state.history[subject]):
# #                         st.markdown(f"**Q:** {item['q']}")
# #                         st.caption(f"Response Time: {item['time']:.2f}s")
# #                         st.markdown("---")

# # if __name__ == "__main__":
# #     main()

# """Streamlit UI for Agentic RAG System - Strict Guardrail Version"""

# import streamlit as st
# from pathlib import Path
# import sys
# import time

# # Add src to path
# sys.path.append(str(Path(__file__).parent))

# from src.config.config import Config
# from src.document_ingestion.document_processor import DocumentProcessor
# from src.vectorstore.vectorstore import VectorStore
# from src.graph_builder.graph_builder import GraphBuilder

# # Page configuration
# st.set_page_config(
#     page_title="🤖 SAGE: Learning Assistant",
#     page_icon="🎓",
#     layout="wide"
# )

# def init_session_state():
#     """Initialize session state variables for Dynamic Subjects"""
#     if 'subjects' not in st.session_state:
#         st.session_state.subjects = ["Machine Learning", "Deep Learning"]
#     if 'rag_system' not in st.session_state:
#         st.session_state.rag_system = None
#     if 'initialized' not in st.session_state:
#         st.session_state.initialized = False
#     if 'history' not in st.session_state:
#         st.session_state.history = {} 

# @st.cache_resource
# def initialize_rag():
#     """Initialize the RAG system"""
#     try:
#         llm = Config.get_llm()
#         doc_processor = DocumentProcessor(
#             chunk_size=Config.CHUNK_SIZE,
#             chunk_overlap=Config.CHUNK_OVERLAP
#         )
#         vector_store = VectorStore()
#         documents = doc_processor.process_urls(Config.DEFAULT_URLS)
#         vector_store.create_vectorstore(documents)
        
#         graph_builder = GraphBuilder(
#             retriever=vector_store.get_retriever(),
#             llm=llm
#         )
#         graph_builder.build()
#         return graph_builder, len(documents)
#     except Exception as e:
#         st.error(f"Failed to initialize: {str(e)}")
#         return None, 0

# def is_relevant(question, subject):
#     """
#     Hard Guardrail: Checks if the question belongs to the current subject.
#     In a production app, you could use a small LLM call here to classify.
#     """
#     # Simple keyword-based validation for speed
#     subject_keywords = subject.lower().split()
#     # Check if any main word from the subject title is in the question
#     # Or if the question is generic (like 'what is this')
#     is_subject_mention = any(word in question.lower() for word in subject_keywords if len(word) > 2)
    
#     # Generic questions are allowed to pass to the agent
#     generic_words = ["what", "how", "explain", "formula", "tell me"]
#     is_generic = all(word in question.lower() for word in generic_words[:2])
    
#     return is_subject_mention or is_generic

# def main():
#     init_session_state()

#     # --- SIDEBAR: SUBJECT MANAGEMENT ---
#     with st.sidebar:
#         st.title("🎓 SAGE Modules")
        
#         new_sub = st.text_input("Create New Subject:", placeholder="e.g. Computer Vision")
#         if st.button("➕ Add Module") and new_sub:
#             # Capitalize first letter of each word
#             formatted_sub = new_sub.strip().title()
#             if formatted_sub not in st.session_state.subjects:
#                 st.session_state.subjects.append(formatted_sub)
#                 st.success(f"Created {formatted_sub}")
#                 st.rerun()
        
#         st.divider()
#         if not st.session_state.initialized:
#             if st.button("🚀 Boot RAG Engine"):
#                 with st.spinner("Initializing..."):
#                     rag_system, _ = initialize_rag()
#                     if rag_system:
#                         st.session_state.rag_system = rag_system
#                         st.session_state.initialized = True
#                         st.rerun()
#         else:
#             st.success("RAG Engine Online")

#     # --- MAIN INTERFACE: DYNAMIC TABS ---
#     st.title("🔍 Multi-Subject Tutoring Agent")

#     if not st.session_state.initialized:
#         st.info("Please boot the RAG engine in the sidebar.")
#         return

#     tabs = st.tabs(st.session_state.subjects)

#     for i, subject in enumerate(st.session_state.subjects):
#         with tabs[i]:
#             st.header(f"{subject} Environment")
            
#             question = st.chat_input(f"Ask about {subject}...", key=f"chat_{subject}")

#             if question:
#                 # --- GUARDRAIL CHECK ---
#                 if not is_relevant(question, subject):
#                     st.error(f"🚫 **Topic Mismatch Detected**")
#                     st.warning(f"This question does not seem related to **{subject}**. Please create or switch to a new module for this topic in the sidebar.")
                    
#                     # Search for existing matches to help the user
#                     matches = [s for s in st.session_state.subjects if s.lower() in question.lower()]
#                     if matches:
#                         st.info(f"💡 Try switching to the **{matches[0]}** tab!")
#                 else:
#                     # Proceed with RAG only if relevant
#                     with st.spinner(f"Analyzing..."):
#                         isolated_prompt = f"### SUBJECT: {subject}\nStrictly answer only if related to {subject}.\nQuestion: {question}"
                        
#                         start_time = time.time()
#                         result = st.session_state.rag_system.run(isolated_prompt)
#                         elapsed_time = time.time() - start_time

#                         st.markdown(f"### 💡 Here is the explanation..")
#                         st.write(result['answer'])
                        
#                         # History tracking
#                         if subject not in st.session_state.history:
#                             st.session_state.history[subject] = []
#                         st.session_state.history[subject].append({"q": question, "a": result['answer']})

#             # History view
#             if subject in st.session_state.history:
#                 with st.expander("Recent History"):
#                     for item in reversed(st.session_state.history[subject][-3:]):
#                         st.write(f"**Q:** {item['q']}")
#                         st.write(f"**A:** {item['a'][:100]}...")

# if __name__ == "__main__":
#     main()

import streamlit as st
from pathlib import Path
import sys
import time
import sqlite3
import hashlib

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

def is_relevant(question, subject):
    subject_keywords = subject.lower().split()
    is_subject_mention = any(word in question.lower() for word in subject_keywords if len(word) > 2)
    generic_words = ["what", "how", "explain", "formula", "tell me"]
    is_generic = all(word in question.lower() for word in generic_words[:2])
    return is_subject_mention or is_generic

# --- AUTHENTICATION UI ---
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
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
                    
    with tab2:
        with st.form("signup_form"):
            new_user = st.text_input("Choose Username")
            new_pw = st.text_input("Choose Password", type="password")
            confirm_pw = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Create Account"):
                if new_pw != confirm_pw:
                    st.error("Passwords do not match")
                elif len(new_pw) < 4:
                    st.error("Password too short")
                else:
                    if db.create_user(new_user, new_pw):
                        st.success("Account created! Please log in.")
                    else:
                        st.error("Username already exists")

# --- MAIN APP LOGIC ---
def main_app():
    # --- SIDEBAR ---
    with st.sidebar:
        st.title(f"👋 Welcome, {st.session_state.username}")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
            
        st.divider()
        st.subheader("🎓 SAGE Modules")
        new_sub = st.text_input("New Subject:", placeholder="e.g. Computer Vision")
        if st.button("➕ Add Module") and new_sub:
            formatted_sub = new_sub.strip().title()
            if formatted_sub not in st.session_state.subjects:
                st.session_state.subjects.append(formatted_sub)
                st.rerun()
        
        st.divider()
        if not st.session_state.initialized:
            if st.button("🚀 Boot RAG Engine"):
                with st.spinner("Initializing..."):
                    rag_system, _ = initialize_rag()
                    if rag_system:
                        st.session_state.rag_system = rag_system
                        st.session_state.initialized = True
                        st.rerun()
        else:
            st.success("RAG Engine Online")

    # --- MAIN CONTENT ---
    st.title("🔍 Multi-Subject Tutoring Agent")

    if not st.session_state.initialized:
        st.info("Please boot the RAG engine in the sidebar to begin.")
        return

    tabs = st.tabs(st.session_state.subjects)

    for i, subject in enumerate(st.session_state.subjects):
        with tabs[i]:
            st.header(f"{subject} Environment")
            question = st.chat_input(f"Ask about {subject}...", key=f"chat_{subject}")

            if question:
                if not is_relevant(question, subject):
                    st.error(f"🚫 **Topic Mismatch Detected**")
                    st.warning(f"This question doesn't seem related to **{subject}**.")
                    matches = [s for s in st.session_state.subjects if s.lower() in question.lower()]
                    if matches:
                        st.info(f"💡 Try switching to the **{matches[0]}** tab!")
                else:
                    with st.spinner(f"Analyzing..."):
                        isolated_prompt = f"### SUBJECT: {subject}\nStrictly answer only if related to {subject}.\nQuestion: {question}"
                        result = st.session_state.rag_system.run(isolated_prompt)

                        st.markdown(f"### 💡 Insights")
                        st.write(result['answer'])
                        
                        if subject not in st.session_state.history:
                            st.session_state.history[subject] = []
                        st.session_state.history[subject].append({"q": question, "a": result['answer']})

            if subject in st.session_state.history:
                with st.expander("Recent History"):
                    for item in reversed(st.session_state.history[subject][-3:]):
                        st.write(f"**Q:** {item['q']}")
                        st.write(f"**A:** {item['a'][:100]}...")

def main():
    init_session_state()
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()