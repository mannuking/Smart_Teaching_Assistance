import streamlit as st
from docx import Document
from docx.shared import Pt
import os
import google.generativeai as genai
import io
from pypdf import PdfReader
import re
import yaml
from yaml.loader import SafeLoader
import time
from dotenv import load_dotenv
import json
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.shared import Inches
import base64

# --- Set page configuration with title and favicon ---
st.set_page_config(
    page_title="Smart Teaching Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom function to display logo and title
def display_app_header():
    # CSS for the header
    st.markdown("""
    <style>
    .app-header {
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        animation: fadeIn 0.5s ease-in-out;
    }
    .app-logo {
        font-size: 2.5rem;
        margin-right: 1rem;
        animation: pulse 2s infinite ease-in-out;
    }
    .app-title {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
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
        margin-top: 2rem;
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
        counter-reset: item;
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

    code {
        font-family: 'Roboto Mono', monospace;
        background-color: #F1F5F9;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.9em;
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
        font-family: 'Times New Roman', Times, serif;
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
            <p class="app-subtitle">Powered by Gemini 2.5 Flash</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Load Environment Variables ---
load_dotenv()

# --- Setup ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Please set your Google API key in the .env file.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

# --- Caching ---
generation_cache = {}  # Simple dictionary for caching

# --- Helper Functions ---
# --- Helper Functions ---

def generate_roadmap(subject, syllabus_text, difficulty_level, temperature=0.7):
    """Generates a detailed roadmap from the syllabus."""
    # Validate inputs
    if not subject or subject.strip() == "":
        st.error("⚠️ Please enter a subject name before generating the roadmap.")
        return ""
    
    if not syllabus_text or syllabus_text.strip() == "":
        st.error("⚠️ No syllabus text found. Please check the uploaded file.")
        return ""
    
    # Trim syllabus text if it's excessively long
    if len(syllabus_text) > 20000:
        st.warning("📝 Syllabus text is very long. Trimming to the first 20,000 characters...")
        syllabus_text = syllabus_text[:20000]
    
    prompt = f"""
    You are an expert educator tasked with creating a detailed roadmap for the subject: "{subject}".

    **Syllabus:** {syllabus_text}
    Target Audience: {difficulty_level} level students

    **Your Task:**
    Generate a comprehensive roadmap that outlines the entire syllabus, divided into main topics, subtopics, and further sub-divisions if necessary. The output MUST STRICTLY ADHERE to the following hierarchical format and output nothing else:

    T<number>: Main Topic Description (e.g., `T1: Introduction to Programming`)
        T<number>.<number>: Subtopic Description (e.g., `T1.1: Basic Data Types`)
            T<number>.<number>.<number>: Sub-subtopic Description (e.g., `T1.1.1: Integers and Floats`)
                T<number>.<number>.<number>.<number>: Further sub-division Description (if needed)

    **Rules:**

    1.  **Hierarchical Format:** Use the exact hierarchical format specified above with "T" followed by numbers and dots.
    2.  **Topic and Subtopic Descriptions:** Each topic and subtopic MUST be followed by a colon (`:`) and a concise, one-sentence description on the SAME LINE.
    3.  **NO Extra Text:** Do not include any introductory text, explanations, or additional formatting beyond what is shown in the example structure. The output should contain ONLY the roadmap structure and the sequence line.
    4.  **NO Asterisks:** Do not use any asterisks (`*`) in the output, except for the examples shown in the format structure.
    5.  **STRICT ADHERENCE:** The output must strictly follow these rules. Any deviations from this format will make the roadmap unusable.
    6.  **Sequence Line:** The very first line of the output MUST be the suggested logical sequence for the topics (Linear, Spiral, or Modular) in the format: `Sequence: <Sequence Type>` (e.g., `Sequence: Linear`).

    Consider the principles of chunking and scaffolding when organizing the outline.
    """
    try:
        if prompt in generation_cache:
            st.success("Roadmap found in cache!")
            return generation_cache[prompt]
        
        # Debug info
        st.info(f"📊 Generating roadmap for subject: '{subject}', level: {difficulty_level}, with {len(syllabus_text)} characters of text.")
        
        with st.spinner("🔄 Analyzing syllabus and generating roadmap..."):
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=4000,  # Increased for longer syllabi
                )
            )
            
            roadmap_text = response.text.strip()
            
            # Verify the output format
            if not roadmap_text or "T1:" not in roadmap_text:
                st.error("⚠️ The generated roadmap doesn't contain expected formatting. Trying again...")
                # Try once more with even more explicit instructions
                response = model.generate_content(
                    prompt + "\n\nNOTE: Your output MUST contain topic identifiers like 'T1:' and should follow exactly the hierarchical format specified above.",
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature - 0.1,  # Lower temperature for more precise output
                        max_output_tokens=4000,
                    )
                )
                roadmap_text = response.text.strip()
            
        if roadmap_text and "T1:" in roadmap_text:
            st.success("✅ Roadmap generated successfully!")
            generation_cache[prompt] = roadmap_text
            return roadmap_text
        else:
            st.error("❌ Failed to generate a properly formatted roadmap.")
            return ""
    except Exception as e:
        st.error(f"⚠️ Error generating roadmap: {e}")
        print(f"Error details: {e}")  # Debugging: Print error to console
        return ""

def parse_roadmap(roadmap_text):
    """
    Parses a roadmap string into a structured dictionary using regular expressions.
    """
    roadmap = {"topics": []}
    lines = roadmap_text.split("\n")

    main_topic_re = r"^T(\d+):\s*(.+)$"
    subtopic_re = r"^T(\d+)\.(\d+):\s*(.+)$"
    subsubtopic_re = r"^T(\d+)\.(\d+)\.(\d+):\s*(.+)$"
    subsubsubtopic_re = r"^T(\d+)\.(\d+)\.(\d+)\.(\d+):\s*(.+)$"

    current_topic = None
    current_subtopic = None
    current_subsubtopic = None
    current_subsubsubtopic = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        main_match = re.match(main_topic_re, line)
        sub_match = re.match(subtopic_re, line)
        subsub_match = re.match(subsubtopic_re, line)
        subsubsub_match = re.match(subsubsubtopic_re, line)

        if main_match:
            topic_num = int(main_match.group(1))
            topic_desc = main_match.group(2)
            current_topic = {
                "id": f"T{topic_num}",
                "description": topic_desc,
                "subtopics": [],
            }
            roadmap["topics"].append(current_topic)
            current_subtopic = None
            current_subsubtopic = None
            current_subsubsubtopic = None
        elif sub_match:
            topic_num = int(sub_match.group(1))
            subtopic_num = int(sub_match.group(2))
            subtopic_desc = sub_match.group(3)
            current_subtopic = {
                "id": f"T{topic_num}.{subtopic_num}",
                "description": subtopic_desc,
                "subsubtopics": [],
            }
            if current_topic:
                current_topic["subtopics"].append(current_subtopic)
            current_subsubtopic = None
            current_subsubsubtopic = None
        elif subsub_match:
            topic_num = int(subsub_match.group(1))
            subtopic_num = int(subsub_match.group(2))
            subsubtopic_num = int(subsub_match.group(3))
            subsubtopic_desc = subsub_match.group(4)
            current_subsubtopic = {
                "id": f"T{topic_num}.{subtopic_num}.{subsubtopic_num}",
                "description": subsubtopic_desc,
                "subsubsubtopics": [],
            }
            if current_subtopic:
                current_subtopic["subsubtopics"].append(current_subsubtopic)
            current_subsubsubtopic = None
        elif subsubsub_match:
            topic_num = int(subsubsub_match.group(1))
            subtopic_num = int(subsubsub_match.group(2))
            subsubtopic_num = int(subsubsub_match.group(3))
            subsubsubtopic_num = int(subsubsub_match.group(4))
            subsubsubtopic_desc = subsubsub_match.group(5)
            current_subsubsubtopic = {
                "id": f"T{topic_num}.{subtopic_num}.{subsubtopic_num}.{subsubsubtopic_num}",
                "description": subsubsubtopic_desc,
                "details": [],
            }
            if current_subsubtopic:
                current_subsubtopic["subsubsubtopics"].append(current_subsubsubtopic)
        else:
            print(f"Warning: Could not parse line: {line}")

    return roadmap

def build_prompt_with_hierarchy(subject, difficulty_level, topic_data, parent_topics_content=None, depth=1):
    """
    Builds a highly optimized prompt for generating lesson plan content, including hierarchical context, specific instructions to prevent repetition, and incorporating advanced learning strategies.
    """
    topic_details = f"**Topic:** {topic_data['id']}: {topic_data['description']}\n"

    prompt = f"""
You are an expert educator creating a detailed lesson plan for the subject: "{subject}".

**Target Audience:** {difficulty_level} level students
**Overall Objective:** To provide a comprehensive and engaging learning experience that builds a strong foundation in {subject}, ensuring students grasp both the theoretical underpinnings and practical applications of each concept.


"""

    if parent_topics_content:
        prompt += "**Context from Parent Topics:**\n"
        for parent_id, parent_desc in parent_topics_content.items():
            prompt += f"  - **{parent_id}:** {parent_desc}\n"

    prompt += f"""
**Current Chunk:** {topic_details}

**Your Task:**
Generate detailed content for this specific chunk of the lesson plan. This is a part of a larger, cohesive plan, so maintain consistency in style, tone, and depth. Ensure that the content is engaging, informative, and suitable for in-depth learning.

"""

    # Depth-based instructions (refined)
    if depth == 1:
        prompt += "**Focus:** Provide a comprehensive overview, establishing the foundational concepts and clearly outlining the subtopics. Lay the groundwork for deeper exploration in subsequent chunks.\n"
    elif depth == 2:
        prompt += "**Focus:** Elaborate on the key concepts introduced earlier. Provide detailed explanations, incorporating examples and analogies to enhance understanding. Ensure a smooth transition from foundational concepts to more complex ideas.\n"
    elif depth >= 3:
        prompt += "**Focus:** Dive deep into the intricacies of each subtopic. Provide in-depth explanations, real-world applications, and challenging scenarios. Encourage critical thinking and problem-solving skills.\n"

    prompt += f"""
**Format and Content Requirements (Strictly Adhere to):**

{topic_details}


1. **Micro-Level Learning Objectives (3-5):** VERY IMPORTANT
    -   Define SMART (Specific, Measurable, Achievable, Relevant, Time-bound) objectives for this chunk.
    -   Begin each objective with an action verb (e.g., Define, Explain, Analyze, Design, Implement).
    -   Ensure alignment with the overall objective of the lesson plan.  
    -   Explain the "why" behind these concepts – their importance and relevance.
    -   Use analogies, metaphors, or real-world examples to enhance understanding are highly encouraged.
    -   **Crucially:** Address potential misconceptions proactively. Anticipate common misunderstandings and clarify them before they take root.
2.
    -   Identify potential challenges or misconceptions that students might encounter.
    -   **ELI5:** If a concept is particularly complex, suggest creating a simplified "Explain Like I'm 5" section in the lecture notes.

**Guiding Principles:**
-   **Clarity and Precision:** Use clear, concise language. Avoid jargon or overly complex sentences.
-   **Engagement:** Maintain an enthusiastic and encouraging tone.
-   **Continuity:** Ensure a smooth flow from previous chunks.
-   **No Repetition:** Refer back to concepts briefly if needed, but do not repeat detailed explanations.
-   **Markdown Formatting:** Use markdown for formatting (headings, lists, bold, italics). No unnecessary asterisks.

"""

    return prompt

def generate_lesson_plan_chunk(subject, difficulty_level, topic_data, parent_topics_content=None, depth=1, temperature=0.7):
    """
    Generates detailed content for a specific chunk of the lesson plan, using hierarchical context.
    """
    prompt = build_prompt_with_hierarchy(subject, difficulty_level, topic_data, parent_topics_content, depth)

    try:
        if prompt in generation_cache:
            st.success(f"Content for {topic_data['id']} found in cache!")
            return generation_cache[prompt]
        with st.spinner(f"Generating content for {topic_data['id']} (Depth: {depth})..."):
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=1500,  # Increased from 500 to 1500 for more detailed content
                )
            )
        # Convert to Markdown-like format
        markdown_content = response.text.strip()
        markdown_content = markdown_content.replace("*   ", "- ")  # Basic list conversion

        generation_cache[prompt] = markdown_content
        return markdown_content
    except Exception as e:
        st.error(f"Error generating lesson plan chunk: {e}")
        print(f"Error generating lesson plan chunk: {e}")  # Debugging
        return ""

def generate_lesson_plan_recursive(subject, roadmap, difficulty_level, temperature=0.7, parent_topics_content=None, depth=1):
    """
    Generates a comprehensive lesson plan recursively and returns a JSON structure, incorporating depth.
    """
    roadmap_dict = parse_roadmap(roadmap)
    lesson_plan_json = {
        "subject": subject,
        "difficulty": difficulty_level,
        "topics": []
    }

    for topic in roadmap_dict["topics"]:
        topic_json = generate_lesson_plan_chunk_json(
            subject, difficulty_level, topic, temperature, parent_topics_content, depth
        )
        lesson_plan_json["topics"].append(topic_json)

    return lesson_plan_json

def generate_lesson_plan_chunk_json(subject, difficulty_level, topic_data, temperature, parent_topics_content=None, depth=1):
    """
    Recursively generates content for a topic/subtopic and returns it as a JSON object, handling depth.
    Correctly handles arbitrary levels of nesting.
    """

    # Build parent_topics_content for subtopics
    current_level_context = {
        topic_data["id"]: topic_data["description"]
    }
    if parent_topics_content:
        current_level_context.update(parent_topics_content)

    content_string = generate_lesson_plan_chunk(
        subject, difficulty_level, topic_data, current_level_context, depth, temperature
    )

    topic_json = {
        "id": topic_data["id"],
        "title": topic_data["description"],
        "content": content_string,
    }

    # Check for and handle subtopics
    if "subtopics" in topic_data and topic_data["subtopics"]:
        topic_json["subtopics"] = []
        for subtopic in topic_data["subtopics"]:
            subtopic_json = generate_lesson_plan_chunk_json(
                subject, difficulty_level, subtopic, temperature, current_level_context, depth + 1
            )
            topic_json["subtopics"].append(subtopic_json)

    # Check for and handle subsubtopics
    if "subsubtopics" in topic_data and topic_data["subsubtopics"]:
        topic_json["subsubtopics"] = []
        for subsubtopic in topic_data["subsubtopics"]:
            subsubtopic_json = generate_lesson_plan_chunk_json(
                subject, difficulty_level, subsubtopic, temperature, current_level_context, depth + 2
            )
            topic_json["subsubtopics"].append(subsubtopic_json)

    # Check for and handle subsubsubtopics
    if "subsubsubtopics" in topic_data and topic_data["subsubsubtopics"]:
        topic_json["subsubsubtopics"] = []
        for subsubsubtopic in topic_data["subsubsubtopics"]:
            subsubsubtopic_json = generate_lesson_plan_chunk_json(
                subject, difficulty_level, subsubsubtopic, temperature, current_level_context, depth + 3
            )
            topic_json["subsubsubtopics"].append(subsubsubtopic_json)

    return topic_json

def save_lesson_plan_json(lesson_plan_json, filename="lesson_plan.json"):
    """Saves the lesson plan JSON to a file."""
    try:
        with open(filename, "w") as f:
            json.dump(lesson_plan_json, f, indent=4)
        st.success(f"Lesson plan saved as {filename}")
    except Exception as e:
        st.error(f"Error saving lesson plan: {e}")
        print(f"Error saving lesson plan: {e}")  # Debugging

def display_lesson_plan_for_editing(lesson_plan_json):
    """
    Displays the lesson plan from the JSON for editing in Streamlit.
    """
    for topic in lesson_plan_json["topics"]:
        display_topic(topic, level=1)

def display_topic(topic, level):
    """
    Displays a single topic or subtopic using markdown headings and text areas with enhanced styling.
    """
    # Create a container for this topic
    topic_container = st.container()
    with topic_container:
        # Title with ID and emoji
        emoji_map = {1: "📘", 2: "📖", 3: "📝", 4: "✏️"}
        emoji = emoji_map.get(level, "📎")
        
        st.markdown(f"""
        <div class="content-topic-header">
            <span class="content-topic-id">{topic['id']}</span>
            <span>{topic['title']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Show existing content (if any) in a formatted way before editing
        if topic["content"] and topic["content"].strip():
            with st.expander("📄 View Current Content", expanded=False):
                st.markdown(f'<div class="content-container">{topic["content"]}</div>', unsafe_allow_html=True)
        
        # Text area with improved styling
        st.markdown(f"""
        <div class="edit-header">
            <span class="edit-icon">✏️</span>
            <h4 class="edit-title">Edit Content</h4>
        </div>
        """, unsafe_allow_html=True)
        
        content = st.text_area(
            "",  # No label, we use the markdown above
            value=topic["content"],
            height=300,
            key=f"{topic['id']}_content",
            help="Edit the content for this topic. Use markdown formatting for headings, lists, and emphasis."
        )
        topic["content"] = content
        
        # Display a preview of formatted content
        if content and content.strip():
            with st.expander("👁️ Preview Formatted Content", expanded=False):
                formatted_content = format_lecture_notes_content(content, topic["id"])
                st.markdown(formatted_content, unsafe_allow_html=True)
        
        # Add some space between topics
        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Process subtopics with indentation
    if topic.get("subtopics") or topic.get("subsubtopics") or topic.get("subsubsubtopics"):
        st.markdown("<div style='margin-left: 2rem;'>", unsafe_allow_html=True)
        
    for subtopic in topic.get("subtopics", []):
        display_topic(subtopic, level + 1)

    for subsubtopic in topic.get("subsubtopics", []):
        display_topic(subsubtopic, level + 2)

    for subsubsubtopic in topic.get("subsubsubtopics", []):
        display_topic(subsubsubtopic, level + 3)
        
    if topic.get("subtopics") or topic.get("subsubtopics") or topic.get("subsubsubtopics"):
        st.markdown("</div>", unsafe_allow_html=True)

def create_docx_from_markdown(text, filename):
    """
    Creates a DOCX file from the given text, interpreting it as Markdown and applying appropriate formatting.
    """
    try:
        document = Document()
        style = document.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(12)

        # Enhanced Markdown parsing
        paragraphs = text.split('\n')
        in_list = False
        list_level = 0
        in_code_block = False

        for para in paragraphs:
            para = para.strip()

            # Code blocks
            if para.startswith("```"):
                in_code_block = not in_code_block
                if in_code_block:
                    # Add a paragraph for the code block
                    code_para = document.add_paragraph()
                    code_para.style = document.styles.add_style(f'CodeBlock{len(document.styles)}', 1)
                    code_para.style.font.name = 'Courier New'
                    code_para.style.font.size = Pt(10)
                continue

            if in_code_block:
                code_para.add_run(para + '\n')
                continue

            # Headings
            if para.startswith('#'):
                level = para.count('#')
                heading_text = para.lstrip('# ').strip()
                document.add_heading(heading_text, level=level)
                continue

            # Lists
            if para.startswith('- ') or para.startswith('* '):
                if not in_list:
                    in_list = True
                    list_level = 1
                else:
                    # Check for nested list
                    spaces = len(para) - len(para.lstrip())
                    new_level = spaces // 2 + 1
                    if new_level > list_level:
                        list_level = new_level
                    elif new_level < list_level:
                        list_level = new_level

                list_item = para.lstrip('-* ').strip()
                p = document.add_paragraph(list_item, style='List Bullet' if list_level == 1 else f'List Bullet {list_level}')
                if list_level > 1:
                    p.paragraph_format.left_indent = Inches(0.5 * list_level)
                continue
            elif in_list:
                in_list = False
                list_level = 0

            # Bold and italics
            while '**' in para:
                start = para.find('**')
                end = para.find('**', start + 2)
                if end == -1:
                    break
                bold_text = para[start+2:end]
                para = para[:start] + '<<BOLD>>' + bold_text + '<<BOLD>>' + para[end+2:]

            while '*' in para:
                start = para.find('*')
                end = para.find('*', start + 1)
                if end == -1:
                    break
                italic_text = para[start+1:end]
                para = para[:start] + '<<ITALIC>>' + italic_text + '<<ITALIC>>' + para[end+1:]

            if para:
                p = document.add_paragraph()
                segments = para.split('<<')
                for segment in segments:
                    if segment.startswith('BOLD>>'):
                        run = p.add_run(segment[6:-6])
                        run.bold = True
                    elif segment.startswith('ITALIC>>'):
                        run = p.add_run(segment[8:-8])
                        run.italic = True
                    else:
                        p.add_run(segment)

        document.save(filename)
        return filename
    except Exception as e:
        st.error(f"Error creating DOCX from Markdown: {e}")
        print(f"Error creating DOCX from Markdown: {e}")
        return None

def create_docx_from_lesson_plan(lesson_plan_json, filename):
    """Creates a DOCX file from the lesson plan JSON."""
    try:
        document = Document()
        style = document.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(12)

        def add_content(data, level):
            if isinstance(data, list):
                for item in data:
                    add_content(item, level)
            elif isinstance(data, dict):
                if "id" in data and "title" in data:
                    document.add_heading(f"{data['id']}: {data['title']}", level=level)
                if "content" in data:
                    #document.add_paragraph(data["content"])
                    paragraphs = data["content"].split('\n')
                    for para in paragraphs:
                        para = para.strip()
                        if para.startswith('# '):
                            document.add_heading(para[2:], level=1)
                        elif para.startswith('## '):
                            document.add_heading(para[3:], level=2)
                        elif para.startswith('### '):
                            document.add_heading(para[4:], level=3)
                        elif para.startswith('#### '):
                            document.add_heading(para[5:], level=4)
                        elif para.startswith('- '):
                            document.add_paragraph(para[2:], style='List Bullet')
                        elif para:
                            document.add_paragraph(para)
                add_content(data.get("subtopics", []), level + 1)
                add_content(data.get("subsubtopics", []), level + 2)
                add_content(data.get("subsubsubtopics", []), level + 3)

        add_content(lesson_plan_json["topics"], level=2)  # Start with level 2 headings

        document.save(filename)
        return filename
    except Exception as e:
        st.error(f"Error creating lesson plan DOCX: {e}")
        print(f"Error creating lesson plan DOCX: {e}")
        return None

def extract_lesson_plan_entry(lesson_plan_json, current_id):
    """
    Extracts the relevant section from the lesson plan JSON based on ID.
    """
    def find_entry_recursive(data, target_id):
        if isinstance(data, list):
            for item in data:
                result = find_entry_recursive(item, target_id)
                if result:
                    return result
        elif isinstance(data, dict):
            if "id" in data and data["id"] == target_id:
                return data["content"]
            for key, value in data.items():
                result = find_entry_recursive(value, target_id)
                if result:
                    return result
        return None

    return find_entry_recursive(lesson_plan_json["topics"], current_id)

def has_sub_chunks(lesson_plan_json, current_id):
    """
    Checks if a given ID in the lesson plan JSON has sub-chunks
    (subtopics, subsubtopics, etc.) at any level.
    """
    def find_entry_recursive(data, target_id):
        if isinstance(data, list):
            for item in data:
                result = find_entry_recursive(item, target_id)
                if result:
                    return result
        elif isinstance(data, dict):
            if "id" in data and data["id"] == target_id:
                return data
            for key, value in data.items():
                result = find_entry_recursive(value, target_id)
                if result:
                    return result
        return None

    def has_sub_keys_recursive(data):
        if isinstance(data, list):
            for item in data:
                if has_sub_keys_recursive(item):
                    return True
        elif isinstance(data, dict):
            if "subtopics" in data and data["subtopics"]:
                return True
            if "subsubtopics" in data and data["subsubtopics"]:
                return True
            if "subsubsubtopics" in data and data["subsubsubtopics"]:
                return True
            for key, value in data.items():
                if has_sub_keys_recursive(value):
                    return True
        return False

    entry = find_entry_recursive(lesson_plan_json["topics"], current_id)
    if entry:
        return has_sub_keys_recursive(entry)
    return False

def get_sub_chunks(lesson_plan_json, current_id):
    """
    Gets the sub-chunk IDs for a given ID.
    """
    def find_subtopic_ids_recursive(data, target_id, found=False):
        sub_chunks = []

        if isinstance(data, list):
            for item in data:
                sub_chunks.extend(find_subtopic_ids_recursive(item, target_id, found))
        elif isinstance(data, dict):
            if "id" in data and data["id"] == target_id:
                found = True

            if found:
                if "subtopics" in data:
                    for subtopic in data["subtopics"]:
                        sub_chunks.append(subtopic["id"])
                if "subsubtopics" in data:
                    for subsubtopic in data["subsubtopics"]:
                        sub_chunks.append(subsubtopic["id"])
                if "subsubsubtopics" in data:
                    for subsubsubtopic in data["subsubsubtopics"]:
                        sub_chunks.append(subsubsubtopic["id"])

            if not found or "subtopics" in data or "subsubtopics" in data or "subsubsubtopics" in data:
                for value in data.values():
                    sub_chunks.extend(find_subtopic_ids_recursive(value, target_id, found))

        return sub_chunks

    return find_subtopic_ids_recursive(lesson_plan_json["topics"], current_id)

def create_lecture_notes_prompt(lesson_plan_entry, current_id, difficulty_level, highlighted_topics, parent_topics_content=None):
    """
    Creates a highly optimized prompt for generating detailed lecture notes, incorporating parent topic context, specific instructions, advanced learning strategies, and addressing potential issues.
    """
    prompt = f"""
You are a distinguished professor and scholar creating comprehensive, publication-quality lecture notes for the following topic:

**Topic ID:** {current_id}
**Subject:** {st.session_state.subject}
**Target Audience:** {difficulty_level} level students
**Overall Objective:** To deliver sophisticated, publication-quality educational content that equips students with a thorough understanding of {st.session_state.subject}, emphasizing both theoretical foundations and practical applications through scholarly discourse.

**Academic Context:**
- These notes should reflect scholarly rigor and depth expected in high-level academic publications
- Ensure thorough coverage with proper citations, explanations, and critical analysis
- Structure content with clear scholarly organization (introduction, development of key concepts, critical analysis, conclusion)
- Use precise academic terminology appropriate for the {difficulty_level} level

"""

    if parent_topics_content:
        prompt += "**Context from Related Topics:**\n"
        for parent_id, parent_content in parent_topics_content.items():
            prompt += f"  - **{parent_id}:** {parent_content}\n"

    prompt += f"""
**Lesson Plan Context (Reference):**
{lesson_plan_entry}

**Highlighted Topics (requiring detailed examples/applications):**
{highlighted_topics}

**Your Task:**
Generate detailed, scholarly lecture notes for this topic based on the provided context. The notes should demonstrate academic rigor, exhibit sophisticated analysis, and provide comprehensive coverage suitable for advanced scholarly discourse.

**Incorporate these scholarly elements:**

1. **Theoretical Foundation:**
   - Begin with a theoretical framework that situates this topic within the broader scholarly discourse
   - Provide precise definitions and explanations of key concepts with proper academic citations where appropriate
   - Include references to seminal works and influential scholars in this area

2. **Critical Analysis:**
   - Examine competing theories or interpretations where applicable
   - Present nuanced arguments with supporting evidence
   - Discuss limitations, implications, and scholarly debates

3. **Didactic Elements:**
   - **Advanced Examples:** Provide sophisticated examples that demonstrate complex applications
   - **Case Studies:** Where appropriate, include detailed case studies that illustrate theoretical principles
   - **Scholarly Analogies:** Use advanced analogies to explain complex concepts
   - **Visual Representations:** Suggest diagrams, charts, or models that could enhance understanding

4. **Pedagogical Structure:**
   - Structure content with clear introduction, development, and conclusion
   - Include discussion questions that promote critical thinking
   - Provide suggestions for further reading or exploration

5. **Formatting Requirements:**
   - Use proper HTML formatting for headers, subheaders, lists, etc.
   - Structure content with a clear hierarchy of concepts
   - Use bold and italics for emphasis of key points
   - Create well-structured numbered and bulleted lists for clarity
   - Format mathematical expressions and equations properly if applicable
   - Ensure proper citation formatting in scholarly style

The final output should be of publication quality that would be suitable for a university-level textbook or scholarly publication. Maintain academic rigor while ensuring accessibility for the target {difficulty_level} audience.
"""

    return prompt

def generate_text_from_prompt(prompt, temperature=0.7):
    """Generates text from a prompt using the LLM."""
    try:
        if prompt in generation_cache:
            st.success("Text found in cache!")
            return generation_cache[prompt]
        with st.spinner("Generating scholarly content..."):
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=4000,  # Increased for more detailed content
                )
            )
        st.success("Scholarly content generated!")
        generation_cache[prompt] = response.text.strip()
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating text: {e}")
        print(f"Error generating text: {e}")
        return ""

def format_lecture_notes_content(content, current_id):
    """Formats the generated lecture notes content with enhanced HTML styling."""
    # Process the content to ensure proper HTML formatting
    if not content:
        return ""
    
    # Convert markdown to enhanced HTML with better styling
    formatted_content = content
    
    # Enhance headings
    formatted_content = re.sub(r'# (.*?)$', r'<h1 class="content-heading">\1</h1>', formatted_content, flags=re.MULTILINE)
    formatted_content = re.sub(r'## (.*?)$', r'<h2 class="content-subheading">\1</h2>', formatted_content, flags=re.MULTILINE)
    formatted_content = re.sub(r'### (.*?)$', r'<h3 class="content-subheading-2">\1</h3>', formatted_content, flags=re.MULTILINE)
    
    # Enhance lists
    formatted_content = re.sub(r'(?m)^- (.*?)$', r'<li class="content-list-item">\1</li>', formatted_content)
    formatted_content = re.sub(r'(?m)^(\d+)\. (.*?)$', r'<li class="content-list-numbered">\1. \2</li>', formatted_content)
    
    # Wrap lists in proper HTML
    formatted_content = re.sub(r'(<li class="content-list-item">.*?</li>\n)+', r'<ul class="content-list">\n\g<0></ul>', formatted_content, flags=re.DOTALL)
    formatted_content = re.sub(r'(<li class="content-list-numbered">.*?</li>\n)+', r'<ol class="content-list-numbered">\n\g<0></ol>', formatted_content, flags=re.DOTALL)
    
    # Enhance emphasis
    formatted_content = re.sub(r'\*\*(.*?)\*\*', r'<strong class="content-emphasis">\1</strong>', formatted_content)
    formatted_content = re.sub(r'\*(.*?)\*', r'<em class="content-italic">\1</em>', formatted_content)
    
    # Add section for the topic ID
    header = f'<div class="content-topic-header"><span class="content-topic-id">{current_id}</span></div>'
    
    # Wrap everything in a div with proper styling
    formatted_content = f'{header}<div class="content-container">{formatted_content}</div>'
    
    return formatted_content

def generate_lecture_notes_chunk(lesson_plan_json, current_id, difficulty_level, highlighted_topics, parent_topics_content=None, temperature=0.8):
    """Generates lecture notes for a specific chunk, without recursively processing sub-chunks."""
    lesson_plan_entry = extract_lesson_plan_entry(lesson_plan_json, current_id)

    # Build parent_topics_context for subtopics
    current_level_context = {}
    if parent_topics_content:
        current_level_context.update(parent_topics_content)

    # Generate content for the current topic only
    prompt = create_lecture_notes_prompt(lesson_plan_entry, current_id, difficulty_level, highlighted_topics, current_level_context)
    generated_content = generate_text_from_prompt(prompt, temperature)
    formatted_content = format_lecture_notes_content(generated_content, current_id)

    return formatted_content  # Return only the content for the current topic

def create_detailed_notes_recursive(lesson_plan_json, difficulty_level, highlighted_topics, temperature=0.8):
    """
    Generates detailed lecture notes recursively, ensuring all topics and subtopics are covered.
    """
    document_text = ""
    processed_ids = set()  # Keep track of processed IDs to prevent duplication

    def count_items_recursive(data):
        count = 0
        if isinstance(data, list):
            for item in data:
                count += count_items_recursive(item)
        elif isinstance(data, dict):
            if "id" in data:
                count += 1
            for key, value in data.items():
                if key in ["subtopics", "subsubtopics", "subsubsubtopics"]:
                    count += count_items_recursive(value)
        return count

    total_items = count_items_recursive(lesson_plan_json["topics"])
    item_count = 0
    progress_bar = st.progress(0)

    def generate_notes_recursive(data, parent_topics_context=None):
        nonlocal document_text, item_count

        if isinstance(data, list):
            for item in data:
                generate_notes_recursive(item, parent_topics_context)
        elif isinstance(data, dict):
            if "id" in data:
                topic_id = data["id"]

                if topic_id in processed_ids:
                    return  # Skip if already processed

                processed_ids.add(topic_id)  # Mark this topic as processed

                # Build parent_topics_context for subtopics
                current_level_context = {}
                if parent_topics_context:
                    current_level_context.update(parent_topics_context)
                current_level_context[topic_id] = data["title"]

                # Always call generate_lecture_notes_chunk for each topic
                topic_content = generate_lecture_notes_chunk(
                    lesson_plan_json, topic_id, difficulty_level, highlighted_topics, current_level_context, temperature
                )
                document_text += topic_content + "\n\n"

                item_count += 1
                progress_bar.progress(item_count / total_items if total_items > 0 else 1.0)

                # Process subtopics immediately after each topic
                for key in ["subtopics", "subsubtopics", "subsubsubtopics"]:
                    if key in data:
                        generate_notes_recursive(data[key], current_level_context)

    generate_notes_recursive(lesson_plan_json["topics"], None)
    filename = "detailed_notes.docx"
    if create_docx_from_markdown(document_text, filename):
        st.success(f"Detailed notes saved as {filename}")
        return filename
    else:
        return None

# App title and welcome message
if 'name' not in st.session_state:
    st.session_state.name = "User"

# Call the header function to display logo and title
display_app_header()

# Sidebar with app info
st.sidebar.markdown(f"""
# 📚 Smart Teaching Assistant

**Welcome, *{st.session_state.name}*!**

This app helps you transform a syllabus into detailed teaching notes using AI.

### How it works:
1. 📋 Upload your syllabus (TXT/PDF)
2. 🗺️ Generate a structured roadmap
3. 📝 Create a detailed lesson plan
4. 📚 Generate comprehensive notes

---

### 🧠 Powered by
Gemini 2.5 Flash Preview
*Advanced AI for education*

---

### 🔄 Version 2.0
*Enhanced UI & Content Generation*
""")

# Step 1 with emoji and better formatting
st.markdown("""
## 📋 Step 1: Syllabus and Difficulty
**Upload your syllabus and set the difficulty level**
""")

# Modified file upload section with clearer labels and direct text input
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### 📄 Upload Syllabus")
    upload_method = st.radio("Choose input method:", ["Upload File", "Enter Text"], horizontal=True)
    
    if upload_method == "Upload File":
        uploaded_syllabus = st.file_uploader("Choose a TXT or PDF file", type=["txt", "pdf"])
    else:
        syllabus_text_input = st.text_area(
            "Enter syllabus text directly:",
            height=250,
            help="Paste your syllabus text here if you don't have a file to upload."
        )
        if syllabus_text_input:
            # Create a virtual "uploaded_syllabus" from the text input
            st.session_state.manual_syllabus_text = syllabus_text_input
    
with col2:
    st.markdown("### 📚 Upload Reference Book (Optional)")
    uploaded_pdf = st.file_uploader("Choose a PDF textbook", type=["pdf"])

difficulty_level = st.selectbox("🎯 Select Difficulty Level", ["Btech", "Mtech", "PHD"])
subject = st.text_input("📝 Enter the subject name:")
st.session_state.subject = subject

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    try:
        # Reset the file pointer to the beginning
        pdf_file.seek(0)
        
        # Create a PDF reader object
        pdf_reader = PdfReader(pdf_file)
        
        # Check if the PDF has pages
        if len(pdf_reader.pages) == 0:
            st.warning("⚠️ The PDF file appears to be empty (no pages found).")
            return None
            
        # Extract text from each page
        text = ""
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            # Progress indicator for larger PDFs
            if i % 10 == 0 and i > 0:
                st.info(f"📄 Processed {i} pages...")
        
        # Check if we got any text
        if not text.strip():
            st.warning("⚠️ No text could be extracted from the PDF. It may be scanned or image-based.")
            return None
            
        st.success(f"✅ Successfully extracted text from {len(pdf_reader.pages)} pages.")
        return text
    except Exception as e:
        st.error(f"⚠️ Error extracting text from PDF: {str(e)}")
        print(f"PDF extraction error details: {e}")
        return None

# Step 2 with emoji and better formatting
st.markdown("""
## 🗺️ Step 2: Generate and Edit Roadmap
**Create a structured roadmap from your syllabus**
""")

syllabus_text = ""
syllabus_source = ""

# Determine the source of syllabus text
if upload_method == "Upload File" and uploaded_syllabus:
    syllabus_source = f"File: {uploaded_syllabus.name}"
    file_type = uploaded_syllabus.type
    
    # Display file info for debugging
    st.info(f"📁 File detected: {uploaded_syllabus.name} ({file_type})")
    
    if file_type == "text/plain":
        try:
            syllabus_text = uploaded_syllabus.read().decode("utf-8")
            st.success(f"✅ Text file loaded: {len(syllabus_text)} characters")
        except Exception as e:
            st.error(f"⚠️ Error reading text file: {e}")
    elif "pdf" in file_type.lower():
        with st.spinner("📄 Extracting text from PDF syllabus..."):
            syllabus_text = extract_text_from_pdf(uploaded_syllabus)
            if not syllabus_text:
                st.error("⚠️ Failed to extract text from PDF. Please try another file.")
    else:
        st.error(f"⚠️ Unsupported file type: {file_type}")
        
elif upload_method == "Enter Text" and "manual_syllabus_text" in st.session_state:
    syllabus_text = st.session_state.manual_syllabus_text
    syllabus_source = "Directly entered text"
    st.success(f"✅ Using manually entered text: {len(syllabus_text)} characters")

# Show a preview of the extracted text
if syllabus_text:
    with st.expander("📝 Preview syllabus text"):
        st.markdown(f"**Source:** {syllabus_source}")
        preview_text = syllabus_text[:1000] + "..." if len(syllabus_text) > 1000 else syllabus_text
        st.markdown(f'<div class="content-container" style="max-height: 300px; overflow-y: auto;">{preview_text}</div>', unsafe_allow_html=True)

    # Process reference book if uploaded
    reference_text = ""
    if uploaded_pdf:
        with st.spinner("📚 Extracting text from reference book..."):
            reference_text = extract_text_from_pdf(uploaded_pdf)
            if reference_text:
                st.success(f"✅ Reference book text extracted: {len(reference_text)} characters")
                with st.expander("📚 Preview reference book text"):
                    preview_text = reference_text[:1000] + "..." if len(reference_text) > 1000 else reference_text
                    st.markdown(f'<div class="content-container" style="max-height: 300px; overflow-y: auto;">{preview_text}</div>', unsafe_allow_html=True)
    
    # Check if subject is provided
    if not subject or subject.strip() == "":
        st.warning("⚠️ Please enter a subject name before generating the roadmap")
    
    roadmap_button = st.button("🚀 Generate Roadmap", key="generate_roadmap_button")
    if roadmap_button:
        if not syllabus_text:
            st.error("⚠️ No syllabus text found. Please check the uploaded file or enter text directly.")
        elif not subject or subject.strip() == "":
            st.error("⚠️ Please enter a subject name before generating the roadmap.")
        else:
            with st.spinner("🔄 Generating scholarly roadmap... This may take a minute."):
                # Clear the cache to ensure fresh content
                if "subject" in st.session_state and st.session_state.subject != subject:
                    generation_cache.clear()
                    
                roadmap = generate_roadmap(subject, syllabus_text, difficulty_level)
                if roadmap:
                    st.session_state.roadmap = roadmap
                    st.session_state.syllabus_text = syllabus_text  # Save for later use
                    st.success("✅ Roadmap generated successfully!")
                    # Force a rerun to show the roadmap immediately
                    st.experimental_rerun()

if "roadmap" in st.session_state:
    st.markdown("""
    <div class="edit-container">
        <div class="edit-header">
            <span class="edit-icon">📝</span>
            <h3 class="edit-title">Review and Edit Your Roadmap</h3>
        </div>
        <p>Fine-tune the structure before proceeding to generate the lesson plan.</p>
    </div>
    """, unsafe_allow_html=True)
    
    edited_roadmap_text = st.text_area("Edit Roadmap", value=st.session_state.roadmap, height=400)
    if st.button("💾 Save Edited Roadmap"):
        st.session_state.roadmap = edited_roadmap_text
        st.success("✅ Roadmap updated!")

# Step 3 with emoji and better formatting
st.markdown("""
## 📝 Step 3: Generate and Edit Lesson Plan
**Create a detailed lesson plan based on the roadmap**
""")

llm_temperature_plan = st.slider("🌡️ AI Creativity Level (Temperature)", 0.0, 1.0, 0.7, step=0.1,
                                help="Controls randomness of lesson plan generation. Higher values = more creative output.")

col1, col2 = st.columns(2)
with col1:
    depth = st.select_slider(
        "🔍 Detail Level",
        options=[1, 2, 3],
        format_func=lambda x: {1: "Basic", 2: "Intermediate", 3: "Advanced"}[x],
        help="Controls the level of detail in the generated lesson plan."
    )

if "roadmap" in st.session_state:
    if st.button("🚀 Generate Lesson Plan"):
        with st.spinner("🔄 Generating comprehensive lesson plan..."):
            try:
                # Clear the cache if we're regenerating
                generation_cache.clear()
                
                lesson_plan_json = generate_lesson_plan_recursive(
                    subject, st.session_state.roadmap, difficulty_level, llm_temperature_plan, None, depth
                )
                st.session_state.lesson_plan = lesson_plan_json
                save_lesson_plan_json(lesson_plan_json)
                st.success("✅ Lesson plan generated and saved as JSON!")
                
                # Force refresh the content
                st.experimental_rerun()
            except Exception as e:
                st.error(f"⚠️ Error generating lesson plan: {e}")
                print(f"Error details: {e}")

if "lesson_plan" in st.session_state:
    st.markdown("""
    ### ✏️ Edit Lesson Plan
    **Review and refine the generated lesson plan**
    """)
    display_lesson_plan_for_editing(st.session_state.lesson_plan)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Edited Lesson Plan"):
            save_lesson_plan_json(st.session_state.lesson_plan)
            st.success("✅ Edited lesson plan saved!")
    with col2:
        if st.button("📥 Download as DOCX"):
            with st.spinner("📄 Creating DOCX file..."):
                create_docx_from_lesson_plan(st.session_state.lesson_plan, "edited_lesson_plan.docx")
            st.success("✅ DOCX file created!")

# Step 4 with emoji and better formatting
st.markdown("""
## 📚 Step 4: Generate Detailed Notes
**Create comprehensive lecture notes from the lesson plan**
""")

st.markdown("**🔢 Highlight topics that need numerical examples (comma-separated):**")
highlighted_topics_input = st.text_area("Example: T1.1, T2.3, T3.1.2", value="", height=100)

llm_temperature_notes = st.slider("🌡️ AI Creativity Level for Notes", 0.0, 1.0, 0.8, step=0.1,
                               help="Controls randomness of notes generation. Higher values = more creative output.")

if "lesson_plan" in st.session_state:
    if st.button("🚀 Generate Detailed Notes"):
        highlighted_topics = [t.strip() for t in highlighted_topics_input.split(",") if t.strip()]
        with st.spinner("🔄 Generating detailed lecture notes... This may take a few minutes."):
            notes_filename = create_detailed_notes_recursive(
                st.session_state.lesson_plan, difficulty_level, highlighted_topics, llm_temperature_notes
            )
            if notes_filename:  # Check if notes were generated
                st.session_state.notes_filename = notes_filename
                st.success("✅ Detailed notes generated successfully!")

    # Download button only if notes have been generated
    if "notes_filename" in st.session_state:
        st.markdown("### 📥 Download Your Notes")
        with open(st.session_state.notes_filename, "rb") as f:
            st.download_button(
                label="📄 Download Detailed Notes (DOCX)",
                data=f,
                file_name=st.session_state.notes_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        st.success("✅ Your detailed notes are ready for download!")
    elif 'lesson_plan' in st.session_state:
        st.info("ℹ️ Please generate detailed notes first.")
else:
    st.warning("⚠️ Please generate and save the lesson plan first.")

# Footer
st.markdown("""
---
### 🎓 Smart Teaching Assistant
*Powered by Gemini 2.5 Flash*
""")
