import streamlit as st
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT # WD_TAB_ALIGNMENT, WD_TAB_LEADER (not used)
# from docx.enum.style import WD_STYLE_TYPE # For list styles, if needed more granularly

import os
import google.generativeai as genai
# import io # Not directly used anymore
from pypdf import PdfReader
import re
# import yaml # Not used
# from yaml.loader import SafeLoader # Not used
import time
from dotenv import load_dotenv
import json
# import base64 # Not used

# --- Page Configuration ---
st.set_page_config(
    page_title="Smart Teaching Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Constants for Structured Output ---
LESSON_PLAN_STRUCTURE_TAGS = {
    "learning_objectives": "LEARNING_OBJECTIVES",
    "key_concepts": "KEY_CONCEPTS_DEFINITIONS",
    "instructional_content": "INSTRUCTIONAL_CONTENT_OUTLINE",
    "engagement_activities": "ENGAGEMENT_STRATEGIES_ACTIVITIES",
    "assessment_methods": "ASSESSMENT_METHODS_CHECKPOINTS",
    "potential_challenges": "POTENTIAL_CHALLENGES_MISCONCEPTIONS",
    "eli5_suggestion": "ELI5_COMPLEX_CONCEPTS",
    "additional_notes": "EDUCATOR_NOTES"
}

LECTURE_NOTE_ELEMENT_TAGS = {
    "heading_1": "H1",
    "heading_2": "H2",
    "heading_3": "H3",
    "paragraph": "P",
    "list_item": "LI",
    "code_block": "CODE",
    "quote_block": "QUOTE",
    "example_block": "EXAMPLE",
    "definition_block": "DEF",
    "equation_block": "EQ",
    "image_placeholder": "IMG",
    "table_placeholder": "TABLE",
}

# --- Custom CSS and Header ---
def display_app_header():
    st.markdown("""
    <style>
    /* Retained most of your CSS for UI consistency */
    /* ... (Your existing comprehensive CSS, ensure it's complete here) ... */
    /* Main styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px; /* Wider container for more space */
    }

    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
        height: 10px;
        border-radius: 5px;
        transition: width 0.3s ease;
    }

    /* Header and title styling */
    h1, h2, h3 {
        color: #1E3A8A;
        font-weight: 600;
    }

    h1 {
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
        color: #1E3A8A;
        text-align: center;
    }

    h2 {
        font-size: 1.8rem;
        margin-top: 2rem;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 0.5rem;
        transition: color 0.3s ease;
    }

    h2:hover {
        color: #3B82F6;
    }

    h3 {
        font-size: 1.4rem;
        margin-top: 1.5rem;
    }

    /* Success message styling */
    .element-container .stAlert {
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        animation: slideIn 0.3s ease-in-out;
    }

    /* Success message styling */
    .element-container .stAlert[data-baseweb="notification"] {
        background-color: #E8F5E9;
        border-left-color: #4CAF50;
    }

    /* Warning message styling */
    div[data-testid="stImage"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }

    div[data-testid="stImage"]:hover {
        transform: scale(1.02);
    }

    /* Card-like containers */
    .stTextArea, 
    div[data-testid="stFileUploader"],
    .stSlider,
    .stSelectbox {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        transition: box-shadow 0.3s ease, transform 0.3s ease;
    }

    .stTextArea:hover, 
    div[data-testid="stFileUploader"]:hover,
    .stSlider:hover,
    .stSelectbox:hover {
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }

    /* Text input styling - make it look like modern search box */
    .stTextInput>div>div>input {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }

    .stTextInput>div>div>input:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
    }

    /* Button styling - make them more 3D */
    .stButton>button {
        background: linear-gradient(to bottom, #2563EB, #1E40AF);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9rem;
    }

    .stButton>button:hover {
        background: linear-gradient(to bottom, #1E40AF, #1E3A8A);
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(37, 99, 235, 0.4);
    }

    .stButton>button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.4);
    }

    /* Radio button styling */
    .stRadio > div {
        display: flex;
        gap: 10px;
    }

    .stRadio label {
        cursor: pointer;
        background-color: #F8FAFC;
        padding: 8px 16px;
        border-radius: 6px;
        border: 1px solid #E2E8F0;
        transition: all 0.2s;
    }

    .stRadio label:hover {
        background-color: #EFF6FF;
        border-color: #BFDBFE;
    }

    /* Select box styling */
    .stSelectbox>div>div>div {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        transition: all 0.3s ease;
    }

    .stSelectbox>div>div>div:hover {
        border-color: #3B82F6;
    }

    /* Text area styling */
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        font-family: 'Roboto Mono', monospace;
        line-height: 1.5;
        transition: all 0.3s ease;
    }

    .stTextArea>div>div>textarea:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1E3A8A;
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }

    .streamlit-expanderHeader:hover {
        background-color: #EFF6FF;
        color: #3B82F6;
    }

    .streamlit-expanderContent {
        border: 1px solid #E2E8F0;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
        animation: fadeIn 0.3s ease-in-out;
    }

    /* Sidebar styling */

    /* Add modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Roboto+Mono&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Improve sidebar appearance */
    section[data-testid="stSidebar"] {
        background-color: #1E3A8A;
        color: white;
        padding-top: 2rem;
        box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: white;
    }

    section[data-testid="stSidebar"] .stMarkdown p {
        color: rgba(255, 255, 255, 0.8);
    }

    /* Custom styling for content display */
    .content-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        line-height: 1.7;
        transition: all 0.3s ease;
    }

    .content-container:hover {
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    .content-topic-header {
        background-color: #1E3A8A;
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 8px 8px 0 0;
        margin-top: 0rem; /* Reduced margin-top */
        font-weight: 600;
    }

    .content-topic-id {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background-color: rgba(255,255,255,0.2);
        border-radius: 4px;
        margin-right: 0.5rem;
    }

    .content-heading {
        color: #1E3A8A;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E2E8F0;
    }

    .content-subheading {
        color: #2563EB;
        font-size: 1.4rem;
        font-weight: 600;
        margin: 1.25rem 0 0.75rem 0;
    }

    .content-subheading-2 {
        color: #3B82F6;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1rem 0 0.5rem 0;
    }

    .content-list {
        padding-left: 1.5rem;
        margin: 1rem 0;
    }

    .content-list-item {
        margin-bottom: 0.5rem;
        position: relative;
    }

    .content-list-numbered {
        padding-left: 1.5rem;
        margin: 1rem 0;
        /* counter-reset: item; */ /* Removed as HTML OL handles numbering */
    }

    .content-emphasis {
        font-weight: 600;
        color: #1E3A8A;
    }

    .content-italic {
        font-style: italic;
        color: #4B5563;
    }

    /* Styling for the edit view */
    .edit-container {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        padding: 1.5rem;
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }

    .edit-container:hover {
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    .edit-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #E2E8F0;
    }

    .edit-icon {
        margin-right: 0.5rem;
        color: #3B82F6;
    }

    .edit-title {
        font-weight: 600;
        color: #1E3A8A;
        margin: 0;
    }

    /* Code block styling */
    pre {
        background-color: #F1F5F9;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Roboto Mono', monospace;
        overflow-x: auto;
        border-left: 4px solid #3B82F6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }

    pre:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    code { /* For inline code */
        font-family: 'Roboto Mono', monospace;
        background-color: #F1F5F9;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.9em;
    }
    pre code { /* For code within pre blocks, reset some inline code styling */
        background-color: transparent;
        padding: 0;
        font-size: 1em; /* Inherit from pre */
    }


    /* Styling for tables */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1.5rem 0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }

    table:hover {
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.1);
    }

    th {
        background-color: #E2E8F0;
        padding: 0.75rem 1rem;
        text-align: left;
        font-weight: 600;
        color: #1E3A8A;
    }

    td {
        padding: 0.75rem 1rem;
        border-top: 1px solid #E2E8F0;
        transition: background-color 0.2s ease;
    }

    tr:hover td {
        background-color: #F1F5F9;
    }

    tr:nth-child(even) {
        background-color: #F8FAFC;
    }

    /* Styling for equations */
    .equation {
        padding: 1rem;
        background-color: #F8FAFC;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
        font-family: 'Times New Roman', Times, serif; /* Changed to be more math-like */
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }

    .equation:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    /* Styling for blockquotes */
    blockquote {
        border-left: 4px solid #3B82F6;
        padding-left: 1rem;
        margin-left: 0;
        color: #4B5563;
        font-style: italic;
        background-color: #F8FAFC;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1rem 1rem 1.5rem;
        transition: all 0.3s ease;
    }

    blockquote:hover {
        background-color: #EFF6FF;
        border-left-color: #2563EB;
    }

    /* Styling for definition terms */
    dt {
        font-weight: 600;
        color: #1E3A8A;
        margin-top: 1rem;
    }

    dd {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Animation keyframes */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideIn {
        from { transform: translateY(-10px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    /* File uploader specific styling */
    div[data-testid="stFileUploader"] div[data-testid="stFileUploaderDropzone"] {
        border: 2px dashed #BFDBFE !important;
        background-color: #EFF6FF;
        border-radius: 8px !important;
        transition: all 0.3s ease;
    }

    div[data-testid="stFileUploader"] div[data-testid="stFileUploaderDropzone"]:hover {
        border-color: #3B82F6 !important;
        background-color: #DBEAFE;
    }
    .app-header {
        display: flex;
        align-items: center;
        justify-content: center; /* Center alignment */
        background: linear-gradient(90deg, #1E3A8A, #3B82F6); /* Example gradient */
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        animation: fadeIn 0.5s ease-in-out;
    }
    .app-logo {
        font-size: 2.5rem; /* Adjust as needed */
        margin-right: 1rem;
        animation: pulse 2s infinite ease-in-out; /* Example animation */
    }
    .app-title {
        color: white;
        font-size: 2rem; /* Adjust as needed */
        font-weight: 700;
        margin: 0;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
     .app-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        margin: 0;
        font-style: italic;
    }
    .title-container {
        display: flex;
        flex-direction: column;
    }

    /* Print styling for generated documents */
    @media print {
        body {
            font-size: 12pt;
            color: black;
            background-color: white;
        }
        
        .app-header, 
        section[data-testid="stSidebar"],
        button, 
        .stButton, 
        .stSlider,
        footer {
            display: none !important;
        }
        
        .content-container {
            box-shadow: none;
            border: 1px solid #E2E8F0;
            break-inside: avoid;
            page-break-inside: avoid;
        }
        
        h1, h2, h3, h4, h5, h6 {
            break-after: avoid;
            page-break-after: avoid;
        }
    }
    </style>
    
    <div class="app-header">
        <div class="app-logo">🎓</div>
        <div class="title-container">
            <h1 class="app-title">Smart Teaching Assistant</h1>
            <p class="app-subtitle">Powered by Gemini</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Load Environment Variables & Setup Gemini ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("🚨 Please set your Google API key in the .env file.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')


# --- Caching ---
generation_cache = {} # Simple dictionary for caching

# --- Helper Functions ---

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    try:
        pdf_file.seek(0)
        pdf_reader = PdfReader(pdf_file)
        if not pdf_reader.pages:
            st.warning("⚠️ The PDF file appears to be empty.")
            return None
        text = ""
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            if i % 20 == 0 and i > 0: st.info(f"📄 Processed {i} PDF pages...") # More frequent updates
        if not text.strip():
            st.warning("⚠️ No text could be extracted from the PDF. It might be image-based.")
            return None
        st.success(f"✅ Successfully extracted text from {len(pdf_reader.pages)} pages.")
        return text
    except Exception as e:
        st.error(f"⚠️ Error extracting text from PDF: {e}")
        return None

def generate_roadmap(subject, syllabus_text, difficulty_level, temperature=0.6): # Slightly lower temp for structure
    if not subject or not subject.strip():
        st.error("⚠️ Please enter a subject name for roadmap generation.")
        return ""
    if not syllabus_text or not syllabus_text.strip():
        st.error("⚠️ Syllabus text is empty. Cannot generate roadmap.")
        return ""
    
    syllabus_text = syllabus_text[:25000] # Increased limit slightly

    prompt = f"""
    You are an expert curriculum designer creating a detailed, hierarchical roadmap for the subject: "{subject}".
    Syllabus Text:
    ---
    {syllabus_text}
    ---
    Target Audience: {difficulty_level} level students

    Task: Generate a comprehensive roadmap. The output MUST STRICTLY ADHERE to this format:
    Sequence: <Linear, Spiral, or Modular> (Suggest a logical teaching sequence on the first line)
    T<number>: Main Topic Description (e.g., T1: Introduction to Core Concepts)
        T<number>.<number>: Subtopic Description (e.g., T1.1: Defining X and Y)
            T<number>.<number>.<number>: Detailed Point or Sub-subtopic (e.g., T1.1.1: Historical Context of X)
                T<number>.<number>.<number>.<number>: Further Elaboration (if necessary)

    Rules:
    1.  Start with the "Sequence:" line.
    2.  Use the EXACT "T<num>..." hierarchical format.
    3.  Each topic/subtopic MUST have a concise, one-sentence description AFTER the colon on the SAME LINE.
    4.  NO extra text, explanations, or formatting beyond this structure. Only the roadmap.
    5.  NO asterisks or other bullet symbols.
    6.  Aim for logical flow and comprehensive coverage based on the syllabus.
    """
    cache_key = f"roadmap_{subject}_{difficulty_level}_{syllabus_text[:500]}" # More robust cache key
    if cache_key in generation_cache:
        st.info("ℹ️ Roadmap found in cache.")
        return generation_cache[cache_key]

    try:
        with st.spinner("🔄 Analyzing syllabus and crafting roadmap..."):
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=4096 # Max for flash
                )
            )
            roadmap_text = response.text.strip()
        
        if roadmap_text and "T1:" in roadmap_text and roadmap_text.startswith("Sequence:"):
            st.success("✅ Roadmap generated successfully!")
            generation_cache[cache_key] = roadmap_text
            return roadmap_text
        else:
            st.error(f"❌ Failed to generate a valid roadmap. LLM Output: {roadmap_text[:300]}...")
            # Optionally, try one more time with a more direct prompt or slightly different temp
            return ""
    except Exception as e:
        st.error(f"⚠️ Error generating roadmap: {e}")
        return ""

def parse_roadmap(roadmap_text):
    roadmap = {"sequence": "Linear", "topics": []} # Default sequence
    lines = roadmap_text.split("\n")

    if lines and lines[0].startswith("Sequence:"):
        roadmap["sequence"] = lines[0].replace("Sequence:", "").strip()
        lines = lines[1:] # Process rest of the lines

    main_topic_re = r"^\s*T(\d+):\s*(.+)$"
    subtopic_re = r"^\s*T(\d+)\.(\d+):\s*(.+)$"
    subsubtopic_re = r"^\s*T(\d+)\.(\d+)\.(\d+):\s*(.+)$"
    subsubsubtopic_re = r"^\s*T(\d+)\.(\d+)\.(\d+)\.(\d+):\s*(.+)$"

    current_topic = None
    current_subtopic = None
    current_subsubtopic = None

    for line in lines:
        line = line.strip()
        if not line: continue

        m_main = re.match(main_topic_re, line)
        m_sub = re.match(subtopic_re, line)
        m_subsub = re.match(subsubtopic_re, line)
        m_subsubsub = re.match(subsubsubtopic_re, line)

        if m_main:
            current_topic = {"id": f"T{m_main.group(1)}", "description": m_main.group(2).strip(), "subtopics": []}
            roadmap["topics"].append(current_topic)
            current_subtopic, current_subsubtopic = None, None
        elif m_sub and current_topic:
            current_subtopic = {"id": f"T{m_sub.group(1)}.{m_sub.group(2)}", "description": m_sub.group(3).strip(), "subsubtopics": []}
            current_topic["subtopics"].append(current_subtopic)
            current_subsubtopic = None
        elif m_subsub and current_subtopic:
            current_subsubtopic = {"id": f"T{m_subsub.group(1)}.{m_subsub.group(2)}.{m_subsub.group(3)}", "description": m_subsub.group(4).strip(), "subsubsubtopics": []}
            current_subtopic["subsubtopics"].append(current_subsubtopic)
        elif m_subsubsub and current_subsubtopic:
            # Note: "details" key was in your original, "subsubsubtopics" list makes sense if it can have children too.
            # For simplicity, let's assume 4th level is leaf.
            sub_item = {"id": f"T{m_subsubsub.group(1)}.{m_subsubsub.group(2)}.{m_subsubsub.group(3)}.{m_subsubsub.group(4)}", "description": m_subsubsub.group(5).strip()}
            current_subsubtopic["subsubsubtopics"].append(sub_item)
        # else: st.warning(f"Roadmap line not parsed: {line}") # Debugging
    return roadmap

def build_prompt_with_hierarchy(subject, difficulty_level, topic_data, parent_topics_content=None, depth=1):
    topic_details = f"Topic: {topic_data['id']}: {topic_data['description']}"
    prompt = f"""
You are an expert educator creating a DETAILED LESSON PLAN CHUNK for the subject: "{subject}".
Target Audience: {difficulty_level} students.
Current Chunk: {topic_details}
"""
    if parent_topics_content:
        prompt += "Context from Parent/Related Topics (for coherence, do not repeat this content directly):\n"
        for p_id, p_desc in parent_topics_content.items():
            prompt += f"  - {p_id}: {p_desc}\n"
    
    depth_focus = ""
    if depth == 1: depth_focus = "Focus: Broad overview, foundational concepts, outline sub-areas for this main topic."
    elif depth == 2: depth_focus = "Focus: Elaborate on key concepts, provide examples, bridge to deeper details for this sub-topic."
    elif depth >= 3: depth_focus = "Focus: In-depth explanation, applications, potential complexities for this specific point."

    prompt += f"{depth_focus}\n"
    prompt += f"""
Format and Content Requirements for '{topic_data['id']}':
Output the content using ONLY the following tags. Content WITHIN each tag should be detailed Markdown.
Ensure each section is well-developed and directly addresses the topic.

[{LESSON_PLAN_STRUCTURE_TAGS['learning_objectives']}_START]
- Specific, measurable, achievable, relevant, time-bound objective 1 (Action verb)...
- Objective 2...
- Explain the "why" behind these objectives – their importance and relevance.
[{LESSON_PLAN_STRUCTURE_TAGS['learning_objectives']}_END]

[{LESSON_PLAN_STRUCTURE_TAGS['key_concepts']}_START]
**Concept A:** Detailed definition and explanation.
**Concept B:** Detailed definition and explanation.
Use analogies or real-world examples here.
[{LESSON_PLAN_STRUCTURE_TAGS['key_concepts']}_END]

[{LESSON_PLAN_STRUCTURE_TAGS['instructional_content']}_START]
- Main teaching point 1 (elaborated).
- Main teaching point 2 (elaborated, possibly with sub-points).
   - Sub-point 2.1
[{LESSON_PLAN_STRUCTURE_TAGS['instructional_content']}_END]

[{LESSON_PLAN_STRUCTURE_TAGS['engagement_activities']}_START]
- Activity 1: Description of an engaging activity.
- Question: A thought-provoking question for discussion.
[{LESSON_PLAN_STRUCTURE_TAGS['engagement_activities']}_END]

[{LESSON_PLAN_STRUCTURE_TAGS['assessment_methods']}_START]
- Method 1: How to assess understanding (e.g., quick quiz, concept map).
- Checkpoint: Specific point to check for comprehension.
[{LESSON_PLAN_STRUCTURE_TAGS['assessment_methods']}_END]

[{LESSON_PLAN_STRUCTURE_TAGS['potential_challenges']}_START]
- Misconception 1: Common misunderstanding. Clarification: ...
- Potential Difficulty: Area where students might struggle. Tip: ...
[{LESSON_PLAN_STRUCTURE_TAGS['potential_challenges']}_END]

[{LESSON_PLAN_STRUCTURE_TAGS['eli5_suggestion']}_START]
Concept to simplify: [Specify complex concept if applicable]. ELI5 Explanation: ...
(Only if a concept within this chunk is particularly complex)
[{LESSON_PLAN_STRUCTURE_TAGS['eli5_suggestion']}_END]

[{LESSON_PLAN_STRUCTURE_TAGS['additional_notes']}_START]
Any other relevant notes, resources, or pedagogical considerations for the educator.
[{LESSON_PLAN_STRUCTURE_TAGS['additional_notes']}_END]

Guiding Principles:
- Clarity, Precision, Engagement, Continuity.
- NO REPETITION of detailed explanations already covered in other main sections.
- Markdown Formatting: Use markdown (headings, lists, bold, italics) WITHIN the tags.
- Output ONLY the tagged sections. No other introductory/concluding text.
"""
    return prompt

def parse_structured_content(text_content, tags_dict):
    parsed_data = {}
    found_any_tag = False
    for field_name, tag_name in tags_dict.items():
        match = re.search(rf"\[{tag_name}_START\](.*?)\s*\[{tag_name}_END\]", text_content, re.DOTALL)
        if match:
            parsed_data[field_name] = match.group(1).strip()
            found_any_tag = True
        else:
            parsed_data[field_name] = ""
    if not found_any_tag and text_content.strip():
        # st.warning(f"Could not find structured tags in content. Displaying as raw.")
        parsed_data['raw_fallback'] = text_content.strip()
    return parsed_data

def reconstruct_markdown_from_structured(structured_data, tags_dict):
    if not structured_data or 'raw_fallback' in structured_data:
        return structured_data.get('raw_fallback', '')
    ordered_sections = [
        ("Learning Objectives", "learning_objectives"), ("Key Concepts & Definitions", "key_concepts"),
        ("Instructional Content Outline", "instructional_content"), ("Engagement Strategies & Activities", "engagement_activities"),
        ("Assessment Methods & Checkpoints", "assessment_methods"), ("Potential Challenges & Misconceptions", "potential_challenges"),
        ("ELI5 for Complex Concepts", "eli5_suggestion"), ("Educator Notes", "additional_notes"),
    ]
    markdown_parts = []
    for title, field_name in ordered_sections:
        content = structured_data.get(field_name, "").strip()
        if content or field_name in ["eli5_suggestion", "additional_notes"]: # Show even if optional ones are empty for editing
             markdown_parts.append(f"### {title}\n{content if content else '(Not specified)'}\n")
    return "\n".join(markdown_parts).strip()

def generate_lesson_plan_chunk(subject, difficulty_level, topic_data, parent_topics_content=None, depth=1, temperature=0.7):
    prompt = build_prompt_with_hierarchy(subject, difficulty_level, topic_data, parent_topics_content, depth)
    cache_key = f"lp_chunk_{topic_data['id']}_{depth}_{str(parent_topics_content)[:100]}"
    if cache_key in generation_cache:
        # st.info(f"ℹ️ Raw content for {topic_data['id']} (lesson plan) found in cache.")
        return generation_cache[cache_key]
    try:
        with st.spinner(f"🔄 Generating lesson plan content for {topic_data['id']}..."):
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=temperature, max_output_tokens=3000) # Increased
            )
        raw_llm_text = response.text.strip()
        generation_cache[cache_key] = raw_llm_text
        return raw_llm_text
    except Exception as e:
        st.error(f"⚠️ Error generating lesson plan chunk for {topic_data['id']}: {e}")
        return f"Error for {topic_data['id']}. Details: {e}"

def generate_lesson_plan_chunk_json(subject, difficulty_level, topic_data, temperature, parent_topics_content=None, depth=1):
    current_level_context = {topic_data["id"]: topic_data["description"]}
    if parent_topics_content: current_level_context.update(parent_topics_content)

    raw_content_string = generate_lesson_plan_chunk(subject, difficulty_level, topic_data, current_level_context, depth, temperature)
    structured_content_data = parse_structured_content(raw_content_string, LESSON_PLAN_STRUCTURE_TAGS)
    reconstructed_markdown = reconstruct_markdown_from_structured(structured_content_data, LESSON_PLAN_STRUCTURE_TAGS)
    
    topic_json = {
        "id": topic_data["id"], "title": topic_data["description"],
        "structured_content": structured_content_data,
        "content": reconstructed_markdown if 'raw_fallback' not in structured_content_data else structured_content_data['raw_fallback']
    }

    for sub_key, next_depth_increment in [("subtopics", 1), ("subsubtopics", 2), ("subsubsubtopics", 3)]:
        if sub_key in topic_data and topic_data[sub_key]:
            topic_json[sub_key] = [
                generate_lesson_plan_chunk_json(subject, difficulty_level, sub_item, temperature, current_level_context, depth + next_depth_increment)
                for sub_item in topic_data[sub_key]
            ]
    return topic_json

def generate_lesson_plan_recursive(subject, roadmap_text, difficulty_level, temperature=0.7, depth_setting=1):
    # roadmap_dict = parse_roadmap(st.session_state.roadmap) # Use passed roadmap_text
    roadmap_dict = parse_roadmap(roadmap_text)

    lesson_plan_json = {"subject": subject, "difficulty": difficulty_level, "topics": []}
    if not roadmap_dict["topics"]:
        st.error("Roadmap has no topics to process for lesson plan.")
        return lesson_plan_json

    total_items = sum(1 + len(t.get("subtopics", [])) + sum(len(st.get("subsubtopics",[])) for st in t.get("subtopics",[])) for t in roadmap_dict["topics"]) # Rough count
    progress_bar = st.progress(0)
    processed_items = 0

    for topic in roadmap_dict["topics"]:
        # Depth for top-level topics is the user selected depth_setting
        topic_json = generate_lesson_plan_chunk_json(subject, difficulty_level, topic, temperature, None, depth_setting)
        lesson_plan_json["topics"].append(topic_json)
        processed_items +=1 # count main topic
        # Add counts for sub-items if you want more granular progress for generate_lesson_plan_recursive
        # For now, progress bar in create_detailed_notes_recursive is more granular.
        progress_bar.progress(min(1.0, processed_items / total_items if total_items > 0 else 1.0))

    return lesson_plan_json


def save_lesson_plan_json(lesson_plan_json, filename="lesson_plan.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(lesson_plan_json, f, indent=2) # Indent 2 for smaller file size
        # st.success(f"Lesson plan saved as {filename}") # Moved to UI
    except Exception as e:
        st.error(f"Error saving lesson plan JSON: {e}")

def display_lesson_plan_for_editing(lesson_plan_json_root):
    for topic in lesson_plan_json_root.get("topics", []):
        display_topic_editor(topic, level=1) # Changed function name

def display_topic_editor(topic_data, level): # Renamed from display_topic
    topic_container = st.container()
    with topic_container:
        emoji_map = {1: "📘", 2: "📖", 3: "📝", 4: "✏️"}
        emoji = emoji_map.get(level, "📎")
        st.markdown(f"""
        <div class="content-topic-header" style="margin-top: {0.5 if level > 1 else 1}rem;">
            <span class="content-topic-id">{topic_data['id']}</span>
            <span>{emoji} {topic_data['title']}</span>
        </div>""", unsafe_allow_html=True)

        structured_data = topic_data.get("structured_content", {})
        is_fallback = 'raw_fallback' in structured_data and structured_data['raw_fallback']
        
        edit_area_key_prefix = f"{topic_data['id']}_{level}" # Ensure unique keys

        if structured_data and not is_fallback:
            st.markdown(f"""<div class="edit-header" style="margin-top: 0.5rem;"><span class="edit-icon">✏️</span><h4 class="edit-title">Edit Structured Content Sections</h4></div>""", unsafe_allow_html=True)
            ordered_edit_fields = [
                ("Learning Objectives", "learning_objectives"), ("Key Concepts & Definitions", "key_concepts"),
                ("Instructional Content Outline", "instructional_content"), ("Engagement Strategies & Activities", "engagement_activities"),
                ("Assessment Methods & Checkpoints", "assessment_methods"), ("Potential Challenges & Misconceptions", "potential_challenges"),
                ("ELI5 for Complex Concepts (Optional)", "eli5_suggestion"), ("Educator Notes (Optional)", "additional_notes"),
            ]
            for display_name, field_key in ordered_edit_fields:
                if field_key in LESSON_PLAN_STRUCTURE_TAGS:
                    field_content = structured_data.get(field_key, "")
                    updated_field_content = st.text_area(
                        f"{display_name}", value=field_content, height=150, # Reduced height
                        key=f"{edit_area_key_prefix}_{field_key}",
                        help=f"Edit {display_name.lower()}. Use Markdown."
                    )
                    topic_data["structured_content"][field_key] = updated_field_content
            topic_data["content"] = reconstruct_markdown_from_structured(topic_data["structured_content"], LESSON_PLAN_STRUCTURE_TAGS)
        else:
            st.markdown(f"""<div class="edit-header"><span class="edit-icon">✏️</span><h4 class="edit-title">Edit Raw Content</h4></div>""", unsafe_allow_html=True)
            if is_fallback: st.warning("This section may not have been fully parsed. Editing raw content.")
            raw_content_to_edit = topic_data.get("content", structured_data.get('raw_fallback', ''))
            edited_raw_content = st.text_area("", value=raw_content_to_edit, height=250, key=f"{edit_area_key_prefix}_raw_content", help="Edit raw content. Use Markdown.")
            topic_data["content"] = edited_raw_content
            if is_fallback: topic_data["structured_content"]['raw_fallback'] = edited_raw_content

        if topic_data["content"] and topic_data["content"].strip():
            with st.expander("👁️ Preview Formatted Content (Combined)", expanded=False):
                preview_html = format_lecture_notes_content(topic_data["content"], topic_data["id"]) # Using existing formatter
                st.markdown(preview_html, unsafe_allow_html=True)
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True) # Simpler separator

    for sub_key, next_depth_increment in [("subtopics", 1), ("subsubtopics", 2), ("subsubsubtopics", 3)]:
        if sub_key in topic_data and topic_data[sub_key]:
            st.markdown("<div style='margin-left: 2rem;'>", unsafe_allow_html=True)
            for sub_item in topic_data[sub_key]:
                display_topic_editor(sub_item, level + next_depth_increment)
            st.markdown("</div>", unsafe_allow_html=True)


def create_docx_from_lesson_plan(lesson_plan_json, filename):
    try:
        document = Document()
        style = document.styles['Normal']
        font = style.font; font.name = 'Calibri'; font.size = Pt(11)

        def add_content_recursive(data_list, current_level):
            for item in data_list:
                if "id" in item and "title" in item:
                    # Make heading level sane for deeply nested items
                    effective_level = min(current_level, 4) # Max heading level 4 for sub-sub-sub
                    document.add_heading(f"{item['id']}: {item['title']}", level=effective_level)
                
                if "content" in item and item["content"].strip():
                    # Simplified Markdown to DOCX conversion for lesson plan
                    # The 'content' is already reconstructed Markdown.
                    # This part relies on your original create_docx_from_lesson_plan's logic for splitting blocks.
                    content_text = item["content"]
                    # Split content into paragraphs based on one or more newlines.
                    # More robust: treat double newlines as paragraph breaks, single as line breaks within para.
                    paragraphs = content_text.split('\n') # Simpler split for now.
                    
                    in_list = False
                    for para_text in paragraphs:
                        para_text_stripped = para_text.strip()
                        if not para_text_stripped:
                            # if p: p = None # End current paragraph on blank line
                            in_list = False # End list on blank line
                            continue

                        p = document.add_paragraph()
                        
                        # Basic list handling (could be improved with regex for nested lists)
                        if para_text_stripped.startswith(("- ", "* ")):
                            p.text = para_text_stripped[2:]
                            p.style = 'ListBullet'
                            in_list = True
                        elif re.match(r"^\d+[\.\)] ", para_text_stripped):
                            p.text = re.sub(r"^\d+[\.\)] ", "", para_text_stripped)
                            p.style = 'ListNumber'
                            in_list = True
                        # Basic heading handling from Markdown
                        elif para_text_stripped.startswith("### "):
                            document.add_heading(para_text_stripped[4:], level=min(effective_level + 2, 6))
                        elif para_text_stripped.startswith("## "):
                             document.add_heading(para_text_stripped[3:], level=min(effective_level + 1, 6))
                        else:
                            # Add run with basic bold/italic. Your original was more complex.
                            add_markdown_inline_to_run(p, para_text_stripped)
                            if in_list: # if previous was list item, this is indented under it
                                p.paragraph_format.left_indent = Inches(0.25)


                for sub_key in ["subtopics", "subsubtopics", "subsubsubtopics"]:
                    if sub_key in item and item[sub_key]:
                        add_content_recursive(item[sub_key], current_level + 1)
        
        document.add_heading(f"Lesson Plan: {lesson_plan_json.get('subject', 'N/A')}", level=0)
        document.add_heading(f"Difficulty: {lesson_plan_json.get('difficulty', 'N/A')}", level=1)
        add_content_recursive(lesson_plan_json.get("topics", []), 2) # Start main topics at level 2

        document.save(filename)
        return filename
    except Exception as e:
        st.error(f"Error creating lesson plan DOCX: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_lesson_plan_entry(lesson_plan_json_root, current_id):
    def find_entry_recursive(data_list, target_id):
        for item_dict in data_list:
            if item_dict.get("id") == target_id:
                return {"title": item_dict.get("title",""), "content": item_dict.get("content","")}
            for sub_key in ["subtopics", "subsubtopics", "subsubsubtopics"]:
                if sub_key in item_dict and item_dict[sub_key]:
                    found = find_entry_recursive(item_dict[sub_key], target_id)
                    if found: return found
        return None
    return find_entry_recursive(lesson_plan_json_root.get("topics", []), current_id)

def create_lecture_notes_prompt(lesson_plan_entry_title, lesson_plan_entry_content, current_id, subject_name, difficulty_level, highlighted_topics, parent_topics_content=None):
    prompt = f"""
You are a distinguished professor creating PUBLICATION-QUALITY lecture notes.
Subject: {subject_name}
Target Audience: {difficulty_level}
Topic ID: {current_id}
Topic Title (from lesson plan): {lesson_plan_entry_title}

Context from Lesson Plan (Use this to guide content generation, NOT for output structure):
---
{lesson_plan_entry_content}
---
"""
    if parent_topics_content:
        prompt += "Context from Related Topics (for coherence, do not repeat directly):\n"
        for p_id, p_desc in parent_topics_content.items(): prompt += f"  - {p_id}: {p_desc}\n"
    if highlighted_topics:
        prompt += f"Emphasize with detailed examples/applications these specific areas: {', '.join(highlighted_topics)}\n"

    prompt += f"""
Task: Generate scholarly lecture notes for "{current_id} - {lesson_plan_entry_title}".
Output the ENTIRE content as a sequence of the following STRUCTURAL TAGS.
Content WITHIN each tag MUST be well-formed Markdown.

AVAILABLE TAGS:
- `[{LECTURE_NOTE_ELEMENT_TAGS['heading_1']}]Page/Topic Title[/H1]` (Use for this chunk's main ID/Title)
- `[{LECTURE_NOTE_ELEMENT_TAGS['heading_2']}]Section Title[/H2]`
- `[{LECTURE_NOTE_ELEMENT_TAGS['heading_3']}]Sub-Section Title[/H3]`
- `[{LECTURE_NOTE_ELEMENT_TAGS['paragraph']}]Detailed paragraph text. Markdown for inline emphasis like **bold** or *italics*.[/P]`
- `[{LECTURE_NOTE_ELEMENT_TAGS['list_item']}]A single list item. Markdown prefix like "- " or "1. " inside.[/LI]`
- `[{LECTURE_NOTE_ELEMENT_TAGS['code_block']} language="language_name"]\ncode content\n[/CODE]`
- `[{LECTURE_NOTE_ELEMENT_TAGS['quote_block']}]Quoted text.[/QUOTE]`
- `[{LECTURE_NOTE_ELEMENT_TAGS['example_block']}]Detailed example description or illustrative code.[/EXAMPLE]`
- `[{LECTURE_NOTE_ELEMENT_TAGS['definition_block']}]**Term:** Definition of the term.[/DEF]`
- `[{LECTURE_NOTE_ELEMENT_TAGS['equation_block']}]LaTeX or plain text equation. E.g., E = mc^2[/EQ]`
- `[{LECTURE_NOTE_ELEMENT_TAGS['image_placeholder']} description="Brief image description"][/IMG]`
- `[{LECTURE_NOTE_ELEMENT_TAGS['table_placeholder']} title="Table Title" columns="Col1|Col2" data="R1C1|R1C2;R2C1|R2C2"][/TABLE]`

CRITICAL INSTRUCTIONS:
1.  **Sequence of Tags:** Output a flat sequence of these tags. Do NOT nest block tags like [P] inside another [P].
2.  **Markdown Inside Tags:** Text *inside* tags is Markdown.
3.  **Scholarly & Comprehensive:** Cover all aspects from lesson plan context.
4.  **Structure:** Start with `[H1]` for the topic ID/title. Use `[H2]` for major sections (Intro, Theories, etc.), `[H3]` for sub-sections.
5.  **No Untagged Text:** ALL content MUST be enclosed in one of the specified tags.

Begin generating the tagged sequence for "{current_id}":
"""
    return prompt

def generate_text_from_prompt(prompt, temperature=0.7, purpose="content"): # Added purpose for cache key
    cache_key = f"{purpose}_{prompt[:200]}_{temperature}" # Basic cache key
    if cache_key in generation_cache:
        # st.info(f"ℹ️ Raw text for {purpose} found in cache.")
        return generation_cache[cache_key]
    try:
        with st.spinner(f"🔮 Generating {purpose} with AI..."):
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=4090 # Max for flash
                )
            )
        raw_text = response.text.strip()
        if not raw_text:
            st.warning(f"LLM returned empty output for {purpose}.")
            return ""
        generation_cache[cache_key] = raw_text
        return raw_text
    except Exception as e:
        st.error(f"⚠️ Error during AI generation for {purpose}: {e}")
        return f"Error generating {purpose}. Details: {e}"

def parse_linear_structured_notes(raw_text, tags_config):
    elements = []
    tag_to_type = {v: k for k, v in tags_config.items()}
    tag_names_pattern = "|".join(re.escape(tag) for tag in tag_to_type.keys())
    pattern = re.compile(
        r"\[(" + tag_names_pattern + r")" + r"(?:\s*([^\]]*?))?\]" +
        r"(.*?)" + r"\s*\[/\1\]",
        re.DOTALL | re.IGNORECASE
    )
    for match in pattern.finditer(raw_text):
        tag_name = match.group(1).upper()
        attributes_str = match.group(2)
        content = match.group(3).strip()
        element_type = tag_to_type.get(tag_name)
        if not element_type: continue
        attrs = {}
        if attributes_str:
            for attr_match in re.finditer(r'(\w+)\s*=\s*"(.*?)"', attributes_str):
                attrs[attr_match.group(1)] = attr_match.group(2)
        elements.append({"type": element_type, "content": content, "attributes": attrs})
    if not elements and raw_text.strip():
        # st.warning("Could not parse structured elements from notes. Using as raw.")
        elements.append({"type": "raw_fallback", "content": raw_text.strip(), "attributes": {}})
    return elements

def generate_lecture_notes_chunk(lesson_plan_json_root, current_id, subject_name, difficulty_level, highlighted_topics, parent_topics_content=None, temperature=0.7):
    entry_data = extract_lesson_plan_entry(lesson_plan_json_root, current_id)
    if not entry_data:
        st.error(f"Could not find lesson plan entry for {current_id} to generate notes.")
        return []
    
    prompt = create_lecture_notes_prompt(
        entry_data["title"], entry_data["content"], current_id,
        subject_name, difficulty_level, highlighted_topics, parent_topics_content
    )
    raw_generated_text = generate_text_from_prompt(prompt, temperature, purpose=f"notes_{current_id}")
    if not raw_generated_text.strip(): return []
    
    return parse_linear_structured_notes(raw_generated_text, LECTURE_NOTE_ELEMENT_TAGS)

def create_detailed_notes_recursive(lesson_plan_json_root, subject_name, difficulty_level, highlighted_topics, temperature=0.7):
    all_topic_structured_notes = []
    processed_ids = set()

    # Simplified item counting for progress
    def count_recursive(data_list):
        count = 0
        for item in data_list:
            count += 1
            for sub_key in ["subtopics", "subsubtopics", "subsubsubtopics"]:
                if sub_key in item and item[sub_key]:
                    count += count_recursive(item[sub_key])
        return count
    
    total_items = count_recursive(lesson_plan_json_root.get("topics", []))
    item_count = 0
    progress_bar = st.progress(0)
    
    def generate_notes_for_list(data_list, parent_context_for_prompt=None):
        nonlocal item_count
        for item_dict in data_list:
            topic_id = item_dict["id"]
            if topic_id in processed_ids: continue
            processed_ids.add(topic_id)

            st.info(f"📝 Generating notes for: {topic_id} - {item_dict.get('title', '')}")
            elements_for_chunk = generate_lecture_notes_chunk(
                lesson_plan_json_root, topic_id, subject_name, difficulty_level,
                highlighted_topics, parent_context_for_prompt, temperature
            )
            if elements_for_chunk:
                all_topic_structured_notes.append({
                    "id": topic_id, "title": item_dict.get("title", "Untitled"),
                    "elements": elements_for_chunk
                })
            item_count += 1
            progress_bar.progress(min(1.0, item_count / total_items if total_items > 0 else 1.0))
            time.sleep(0.05) # For UI responsiveness

            current_item_context = {topic_id: item_dict.get("title", "")}
            if parent_context_for_prompt: current_item_context.update(parent_context_for_prompt)
            for sub_key in ["subtopics", "subsubtopics", "subsubsubtopics"]:
                if sub_key in item_dict and item_dict[sub_key]:
                    generate_notes_for_list(item_dict[sub_key], current_item_context)
    
    generate_notes_for_list(lesson_plan_json_root.get("topics", []))
    
    if not all_topic_structured_notes:
        st.error("No content generated for detailed notes.")
        return None

    filename = "detailed_notes_structured.docx"
    if create_docx_from_parsed_elements(all_topic_structured_notes, filename, subject_name, difficulty_level):
        # st.success(f"Detailed notes saved as {filename}") # Moved to UI
        return filename
    else:
        st.error("Failed to create DOCX from structured notes.")
        return None

def add_markdown_inline_to_run(paragraph, text_segment):
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text_segment)
    for part in parts:
        if not part: continue
        if part.startswith('**') and part.endswith('**') and len(part) > 4:
            run = paragraph.add_run(part[2:-2]); run.bold = True
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            run = paragraph.add_run(part[1:-1]); run.italic = True
        elif part.startswith('`') and part.endswith('`') and len(part) > 2:
            run = paragraph.add_run(part[1:-1]); run.font.name = 'Courier New'
        else:
            paragraph.add_run(part)

def create_docx_from_parsed_elements(all_topics_data, filename, subject_name, difficulty_level):
    try:
        document = Document()
        style = document.styles['Normal']; font = style.font; font.name = 'Calibri'; font.size = Pt(11)
        document.add_heading(f"Detailed Lecture Notes: {subject_name}", level=0)
        document.add_paragraph(f"Target Audience: {difficulty_level}\n")

        for topic_data in all_topics_data:
            # Add a separator or clear heading for each main roadmap item's notes
            # document.add_heading(f"Notes for: {topic_data['id']} - {topic_data['title']}", level=1) # Redundant if H1 is first element
            
            for element in topic_data['elements']:
                el_type = element['type']; content = element.get('content', ''); attrs = element.get('attributes', {})
                if el_type == 'raw_fallback':
                    p = document.add_paragraph(); add_markdown_inline_to_run(p, f"[RAW FALLBACK for {topic_data.get('id','N/A')}]: {content}")
                    continue

                if el_type == 'heading_1': document.add_heading(content, level=1)
                elif el_type == 'heading_2': document.add_heading(content, level=2)
                elif el_type == 'heading_3': document.add_heading(content, level=3)
                elif el_type == 'paragraph': p = document.add_paragraph(); add_markdown_inline_to_run(p, content)
                elif el_type == 'list_item':
                    is_ord = content.strip().startswith(tuple(f"{i}." for i in range(1,10)))
                    style = 'ListNumber' if is_ord else 'ListBullet'
                    clean_c = re.sub(r"^\s*[-\*\+]?\s*|\s*\d+[\.\)]\s*", "", content.strip(), 1)
                    p = document.add_paragraph(style=style); add_markdown_inline_to_run(p, clean_c)
                elif el_type == 'code_block':
                    p = document.add_paragraph(); run = p.add_run(f"(Code - {attrs.get('language', 'text')}):"); run.italic = True
                    code_p = document.add_paragraph(); code_run = code_p.add_run(content); code_run.font.name = 'Courier New'; code_run.font.size = Pt(10)
                elif el_type == 'quote_block': p = document.add_paragraph(style='Intense Quote'); add_markdown_inline_to_run(p, content)
                elif el_type == 'example_block': document.add_heading("Example:", level=4); p = document.add_paragraph(); add_markdown_inline_to_run(p, content)
                elif el_type == 'definition_block': p = document.add_paragraph(); add_markdown_inline_to_run(p, content) # Assumes **Term:** Def
                elif el_type == 'equation_block':
                    p = document.add_paragraph(); run = p.add_run("Equation: "); run.italic = True
                    eq_run = p.add_run(content); eq_run.font.name = 'Cambria Math'; p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                elif el_type == 'image_placeholder':
                    p = document.add_paragraph(); run = p.add_run(f"[Image: {attrs.get('description', 'N/A')}]"); run.italic = True; p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                elif el_type == 'table_placeholder':
                    p = document.add_paragraph(); run = p.add_run(f"[Table: {attrs.get('title', 'N/A')}]\n"); run.italic = True
                    if 'columns' in attrs and 'data' in attrs:
                        try:
                            cols = attrs['columns'].split('|'); num_cols = len(cols)
                            table = document.add_table(rows=1, cols=num_cols); table.style = 'Table Grid'
                            for i, h_text in enumerate(cols): table.rows[0].cells[i].text = h_text
                            for row_text in attrs['data'].split(';'):
                                row_vals = row_text.split('|'); row_cells = table.add_row().cells
                                for i in range(min(num_cols, len(row_vals))): row_cells[i].text = row_vals[i]
                        except Exception as e_tbl: p.add_run(f"(Err creating table: {e_tbl})")
                    else: p.add_run(f"Cols: {attrs.get('columns')} Data: {attrs.get('data')}")
        document.save(filename)
        return filename
    except Exception as e:
        st.error(f"Error creating detailed notes DOCX: {e}")
        import traceback; traceback.print_exc(); return None

def format_lecture_notes_content(content, current_id_for_header=""): # Kept for lesson plan preview
    """Formats Markdown content with enhanced HTML styling."""
    if not content: return ""
    formatted_content = content
    formatted_content = re.sub(r'# (.*?)$', r'<h1 class="content-heading">\1</h1>', formatted_content, flags=re.MULTILINE)
    formatted_content = re.sub(r'## (.*?)$', r'<h2 class="content-subheading">\1</h2>', formatted_content, flags=re.MULTILINE)
    formatted_content = re.sub(r'### (.*?)$', r'<h3 class="content-subheading-2">\1</h3>', formatted_content, flags=re.MULTILINE)
    formatted_content = re.sub(r'(?m)^- (.*?)$', r'<li class="content-list-item">\1</li>', formatted_content)
    formatted_content = re.sub(r'(?m)^(\d+)\. (.*?)$', r'<li class="content-list-item">\1. \2</li>', formatted_content) # Use same class for now
    formatted_content = re.sub(r'(<li class="content-list-item">.*?</li>\n*)+', r'<ul class="content-list">\g<0></ul>', formatted_content, flags=re.DOTALL) # Basic wrapping
    formatted_content = formatted_content.replace("</ul>\n<ul", "</ul><ul") # Fix multiple lists
    formatted_content = re.sub(r'\*\*(.*?)\*\*', r'<strong class="content-emphasis">\1</strong>', formatted_content)
    formatted_content = re.sub(r'\*(.*?)\*', r'<em class="content-italic">\1</em>', formatted_content)
    formatted_content = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', formatted_content, flags=re.DOTALL)
    formatted_content = re.sub(r'`(.*?)`', r'<code>\1</code>', formatted_content)
    formatted_content = re.sub(r'(?m)^> (.*?)$', r'<blockquote>\1</blockquote>', formatted_content)
    
    header_html = f'<div class="content-topic-header"><span class="content-topic-id">{current_id_for_header}</span></div>' if current_id_for_header else ""
    return f'{header_html}<div class="content-container">{formatted_content}</div>'

# --- Streamlit App UI ---
display_app_header()

st.sidebar.markdown(f"""# 📚 Smart Teaching Assistant
**Welcome!** This app transforms syllabi into detailed teaching materials using AI.
### How it works:
1. 📤 Upload syllabus (TXT/PDF) & set parameters.
2. 🗺️ Generate a structured roadmap.
3. 📝 Create a detailed lesson plan (editable).
4. 📖 Generate comprehensive lecture notes.
---
🧠 Powered by Gemini
""")

# Step 1: Syllabus and Difficulty
st.markdown("## 📋 Step 1: Syllabus and Parameters")
col1, col2 = st.columns([2,1]) # Adjusted column ratio
with col1:
    upload_method = st.radio("Syllabus input method:", ["Upload File", "Enter Text"], horizontal=True, key="syllabus_input_method")
    if upload_method == "Upload File":
        uploaded_syllabus_file = st.file_uploader("Choose a TXT or PDF syllabus", type=["txt", "pdf"], key="syllabus_file")
    else:
        syllabus_text_manual = st.text_area("Paste syllabus text:", height=200, key="syllabus_manual_text")
        if syllabus_text_manual: st.session_state.manual_syllabus_text_input = syllabus_text_manual

with col2:
    subject = st.text_input("📝 Subject Name:", key="subject_name_input", placeholder="e.g., Introduction to AI")
    difficulty_level = st.selectbox("🎯 Target Difficulty:", ["Btech", "Mtech", "PHD"], key="difficulty_select")

# Process syllabus text
syllabus_text_content = ""
if upload_method == "Upload File" and uploaded_syllabus_file:
    if uploaded_syllabus_file.type == "text/plain":
        try: syllabus_text_content = uploaded_syllabus_file.read().decode("utf-8")
        except Exception as e: st.error(f"Error reading TXT: {e}")
    elif "pdf" in uploaded_syllabus_file.type.lower():
        with st.spinner("📄 Extracting text from PDF syllabus..."):
            syllabus_text_content = extract_text_from_pdf(uploaded_syllabus_file)
    if syllabus_text_content: st.success(f"Syllabus from '{uploaded_syllabus_file.name}' loaded ({len(syllabus_text_content):,} chars).")
elif upload_method == "Enter Text" and "manual_syllabus_text_input" in st.session_state:
    syllabus_text_content = st.session_state.manual_syllabus_text_input
    if syllabus_text_content: st.success(f"Using manually entered syllabus ({len(syllabus_text_content):,} chars).")

if syllabus_text_content:
    with st.expander("📝 View Syllabus Text (first 1000 chars)", expanded=False):
        st.markdown(f'<div class="content-container" style="max-height: 200px; overflow-y: auto;">{syllabus_text_content[:1000]}...</div>', unsafe_allow_html=True)

# Step 2: Generate Roadmap
st.markdown("## 🗺️ Step 2: Generate Roadmap")
if syllabus_text_content and subject:
    if st.button("🚀 Generate Roadmap", key="gen_roadmap_btn"):
        if "roadmap" in st.session_state: del st.session_state["roadmap"] # Clear old
        if "lesson_plan" in st.session_state: del st.session_state["lesson_plan"]
        if "notes_filename" in st.session_state: del st.session_state["notes_filename"]
        generation_cache.clear() # Clear cache for new generation flow

        roadmap_result = generate_roadmap(subject, syllabus_text_content, difficulty_level)
        if roadmap_result:
            st.session_state.roadmap = roadmap_result
            st.rerun() # Show roadmap editor immediately
        else:
            st.error("Roadmap generation failed. Please check errors or try again.")
else:
    st.info("ℹ️ Please provide syllabus text and subject name above to generate a roadmap.")

if "roadmap" in st.session_state:
    st.markdown("""<div class="edit-container" style="margin-top:1em;"><div class="edit-header"><span class="edit-icon">✍️</span><h3 class="edit-title">Review & Edit Roadmap</h3></div></div> """, unsafe_allow_html=True)
    edited_roadmap = st.text_area("Roadmap Structure:", value=st.session_state.roadmap, height=300, key="roadmap_edit_area")
    if st.button("💾 Save Edited Roadmap", key="save_roadmap_btn"):
        st.session_state.roadmap = edited_roadmap
        st.success("✅ Roadmap updated!")
        if "lesson_plan" in st.session_state: del st.session_state["lesson_plan"] # Invalidate lesson plan
        if "notes_filename" in st.session_state: del st.session_state["notes_filename"]


# Step 3: Generate Lesson Plan
st.markdown("## 📝 Step 3: Generate & Edit Lesson Plan")
if "roadmap" in st.session_state and subject and difficulty_level:
    llm_temp_plan = st.slider("🌡️ AI Creativity (Lesson Plan):", 0.1, 1.0, 0.6, step=0.05, key="temp_plan_slider", help="Lower for more factual, higher for more creative lesson plan sections.")
    plan_depth = st.select_slider("🔍 Detail Level (Lesson Plan):", options=[1, 2, 3], value=2, format_func=lambda x: {1:"Overview", 2:"Standard", 3:"In-Depth"}[x], key="plan_depth_slider")

    if st.button("🚀 Generate Lesson Plan", key="gen_plan_btn"):
        if "lesson_plan" in st.session_state: del st.session_state["lesson_plan"]
        if "notes_filename" in st.session_state: del st.session_state["notes_filename"]
        # generation_cache.clear() # Already cleared if roadmap was generated, but good for safety
        
        with st.spinner("🔄 Generating structured lesson plan... This might take a while."):
            lesson_plan_data = generate_lesson_plan_recursive(subject, st.session_state.roadmap, difficulty_level, llm_temp_plan, plan_depth)
        if lesson_plan_data and lesson_plan_data.get("topics"):
            st.session_state.lesson_plan = lesson_plan_data
            save_lesson_plan_json(st.session_state.lesson_plan) # Save silently
            st.success("✅ Lesson plan generated! You can now edit it below.")
            st.rerun()
        else:
            st.error("Lesson plan generation failed or returned no topics.")

    if "lesson_plan" in st.session_state:
        st.markdown("### ✏️ Edit Lesson Plan Sections")
        display_lesson_plan_for_editing(st.session_state.lesson_plan)
        
        col_lp_save, col_lp_dl = st.columns(2)
        with col_lp_save:
            if st.button("💾 Save Edited Lesson Plan", key="save_edited_plan_btn"):
                save_lesson_plan_json(st.session_state.lesson_plan)
                st.success("✅ Edited lesson plan saved to `lesson_plan.json`!")
        with col_lp_dl:
            if st.session_state.lesson_plan:
                plan_docx_buffer = create_docx_from_lesson_plan(st.session_state.lesson_plan, "temp_lesson_plan.docx")
                if plan_docx_buffer:
                    with open("temp_lesson_plan.docx", "rb") as fp_plan:
                        st.download_button(
                            label="📥 Download Lesson Plan (DOCX)",
                            data=fp_plan,
                            file_name=f"{subject.replace(' ','_')}_LessonPlan.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    os.remove("temp_lesson_plan.docx") # Clean up temp file
else:
    st.info("ℹ️ Generate and save a roadmap first to enable lesson plan generation.")


# Step 4: Generate Detailed Notes
st.markdown("## 📖 Step 4: Generate Detailed Lecture Notes")
if "lesson_plan" in st.session_state and subject:
    highlighted_topics_input = st.text_area("✍️ Topics for extra examples (comma-separated IDs like T1.1, T2.3):", key="highlight_topics_input", height=75)
    llm_temp_notes = st.slider("🌡️ AI Creativity (Notes):", 0.1, 1.0, 0.7, step=0.05, key="temp_notes_slider", help="Controls randomness for notes generation.")

    if st.button("🚀 Generate Detailed Notes", key="gen_notes_btn"):
        if "notes_filename" in st.session_state: del st.session_state["notes_filename"]
        
        highlighted = [t.strip() for t in highlighted_topics_input.split(",") if t.strip()]
        with st.spinner("🔄 Generating detailed lecture notes from plan... This can take several minutes."):
            notes_file = create_detailed_notes_recursive(
                st.session_state.lesson_plan, subject, difficulty_level, highlighted, llm_temp_notes
            )
        if notes_file:
            st.session_state.notes_filename = notes_file
            st.success(f"✅ Detailed notes generated as `{notes_file}`!")
            st.rerun() # To show download button
        else:
            st.error("Detailed notes generation failed.")

    if "notes_filename" in st.session_state and os.path.exists(st.session_state.notes_filename):
        st.markdown("### 📥 Download Your Notes")
        with open(st.session_state.notes_filename, "rb") as fp_notes:
            st.download_button(
                label="📄 Download Detailed Notes (DOCX)",
                data=fp_notes,
                file_name=f"{subject.replace(' ','_')}_DetailedNotes.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    elif 'lesson_plan' in st.session_state :
         st.info("ℹ️ Click 'Generate Detailed Notes' to create the DOCX.")
else:
    st.info("⚠️ Please generate and save a lesson plan first to enable detailed notes generation.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:grey;'>Smart Teaching Assistant - Streamlining Curriculum Development</p>", unsafe_allow_html=True)