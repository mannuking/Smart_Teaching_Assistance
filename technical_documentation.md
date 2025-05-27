# Smart Teaching Assistant - Technical Documentation

## Architecture Overview

The Smart Teaching Assistant is built with a modular architecture centered around the Streamlit framework and Google's Gemini AI. The application follows a sequential workflow that transforms educational content through several processing stages.

## Key Components

### 1. Core Dependencies

```python
import streamlit as st
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import os
import google.generativeai as genai
from pypdf import PdfReader
import re
import time
from dotenv import load_dotenv
import json
import traceback
```

### 2. Configuration and Constants

The application uses two main configuration dictionaries that define the structure of generated content:

#### Lesson Plan Structure Tags
```python
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
```

#### Lecture Notes Element Tags
```python
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
```

### 3. Environment Setup

```python
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Please set your Google API key in the .env file.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
```

### 4. Caching Mechanism

```python
generation_cache = {}  # Simple dictionary for caching
```

## Core Functions

### Syllabus Processing

#### PDF Text Extraction

```python
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
            if i % 20 == 0 and i > 0: st.info(f"📄 Processed {i} PDF pages...")
        if not text.strip():
            st.warning("⚠️ No text could be extracted from the PDF. It might be image-based.")
            return None
        st.success(f"✅ Successfully extracted text from {len(pdf_reader.pages)} pages.")
        return text
    except Exception as e:
        st.error(f"⚠️ Error extracting text from PDF: {e}")
        return None
```

#### Roadmap Generation

```python
def generate_roadmap(subject, syllabus_text, difficulty_level, temperature=0.6):    
    try:
        # Prompt construction for roadmap generation
        prompt = f"""
        You are an expert educator tasked with creating a detailed roadmap for the subject: "{subject}".
        
        **Syllabus:** {syllabus_text}
        Target Audience: {difficulty_level} level students
        
        Your task is to generate a comprehensive roadmap that outlines the entire syllabus, divided into main topics, subtopics, and further sub-divisions if necessary.
        """
        
        # Generate content with Gemini
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
            )
        )
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating roadmap: {e}")
        return None
```

#### Roadmap Parsing

```python
def parse_roadmap(roadmap_text):
    roadmap = {"sequence": "Linear", "topics": []} # Default sequence
    lines = roadmap_text.split("\n")

    # Parse sequence type if available
    if lines and lines[0].startswith("Sequence:"):
        sequence_line = lines[0].split(":", 1)
        if len(sequence_line) > 1:
            roadmap["sequence"] = sequence_line[1].strip()
        lines = lines[1:]  # Remove the sequence line from further processing

    # Regex patterns for identifying topic levels
    main_topic_re = r"^\s*T(\d+):\s*(.+)$"
    subtopic_re = r"^\s*T(\d+)\.(\d+):\s*(.+)$"
    subsubtopic_re = r"^\s*T(\d+)\.(\d+)\.(\d+):\s*(.+)$"
    subsubsubtopic_re = r"^\s*T(\d+)\.(\d+)\.(\d+)\.(\d+):\s*(.+)$"

    # Tracking variables for current topic at each level
    current_topic = None
    current_subtopic = None
    current_subsubtopic = None

    # Process each line and build the hierarchical structure
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Match against different levels of topic patterns
        # Add matched topics to the appropriate level in the hierarchy
    
    return roadmap
```

### Lesson Plan Generation

#### Prompt Construction with Hierarchy

```python
def build_prompt_with_hierarchy(subject, difficulty_level, topic_data, parent_topics_content=None, depth=1):
    topic_details = f"Topic: {topic_data['id']}: {topic_data['description']}"
    prompt = f"""
    You are an expert educator creating a DETAILED LESSON PLAN CHUNK for the subject: "{subject}".
    Target Audience: {difficulty_level} students.
    Current Chunk: {topic_details}
    """
    
    # Add parent topic context if available
    if parent_topics_content:
        prompt += "Context from Parent Topics:\n"
        for p_id, p_desc in parent_topics_content.items():
            prompt += f"  - {p_id}: {p_desc}\n"
    
    # Add depth-specific instructions
    depth_focus = ""
    if depth == 1: 
        depth_focus = "Focus on establishing foundational concepts and framework."
    elif depth == 2: 
        depth_focus = "Provide detailed explanations and examples building on foundations."
    elif depth >= 3: 
        depth_focus = "Dive deep into complex aspects, applications, and connections."

    prompt += f"{depth_focus}\n"
    
    # Structured format requirements
    prompt += """
    Format and Content Requirements:
    Output the content using ONLY the following tags. Content WITHIN each tag should be detailed Markdown.
    """
    
    # Add tag-specific requirements for each section
    # ...
    
    return prompt
```

#### Lesson Plan Generation

```python
def generate_lesson_plan_chunk(subject, difficulty_level, topic_data, parent_topics_content=None, depth=1, temperature=0.7):
    prompt = build_prompt_with_hierarchy(subject, difficulty_level, topic_data, parent_topics_content, depth)
    cache_key = f"lp_chunk_{topic_data['id']}_{depth}_{str(parent_topics_content)[:100]}"
    
    # Check cache first
    if cache_key in generation_cache:
        return generation_cache[cache_key]
    
    try:
        with st.spinner(f"🔄 Generating lesson plan content for {topic_data['id']}..."):
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                )
            )
            
        raw_llm_text = response.text.strip()
        generation_cache[cache_key] = raw_llm_text
        return raw_llm_text
    except Exception as e:
        st.error(f"⚠️ Error generating lesson plan chunk for {topic_data['id']}: {e}")
        return f"Error for {topic_data['id']}. Details: {e}"
```

#### Recursive Lesson Plan Generation

```python
def generate_lesson_plan_recursive(subject, roadmap_text, difficulty_level, temperature=0.7, depth_setting=1):
    roadmap_dict = parse_roadmap(roadmap_text)

    lesson_plan_json = {"subject": subject, "difficulty": difficulty_level, "topics": []}
    if not roadmap_dict["topics"]:
        st.error("Roadmap has no topics to process for lesson plan.")
        return lesson_plan_json

    # Set up progress tracking
    total_items = sum(1 + len(t.get("subtopics", [])) + sum(len(st.get("subsubtopics",[])) for st in t.get("subtopics",[])) for t in roadmap_dict["topics"])
    progress_bar = st.progress(0)
    processed_items = 0

    # Process each topic and its subtopics
    for topic in roadmap_dict["topics"]:
        topic_json = generate_lesson_plan_chunk_json(subject, difficulty_level, topic, temperature, None, depth_setting)
        lesson_plan_json["topics"].append(topic_json)
        processed_items += 1
        progress_bar.progress(min(1.0, processed_items / total_items if total_items > 0 else 1.0))

    return lesson_plan_json
```

### Lecture Notes Generation

#### Notes Prompt Creation

```python
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
    
    # Add specific formatting instructions for structured notes output
    # ...
    
    return prompt
```

#### Notes Generation and Parsing

```python
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
```

#### Recursive Notes Generation

```python
def create_detailed_notes_recursive(lesson_plan_json_root, subject_name, difficulty_level, highlighted_topics, temperature=0.7):
    all_topic_structured_notes = []
    processed_ids = set()

    # Setup progress tracking
    total_items = count_recursive(lesson_plan_json_root.get("topics", []))
    item_count = 0
    progress_bar = st.progress(0)
    
    # Recursive function to generate notes for all topics and subtopics
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

            # Process subtopics with updated context
            current_item_context = {topic_id: item_dict.get("title", "")}
            if parent_context_for_prompt: current_item_context.update(parent_context_for_prompt)
            
            # Process different levels of subtopics
            for sub_key in ["subtopics", "subsubtopics", "subsubsubtopics"]:
                if sub_key in item_dict and item_dict[sub_key]:
                    generate_notes_for_list(item_dict[sub_key], current_item_context)
    
    # Start the recursive generation
    generate_notes_for_list(lesson_plan_json_root.get("topics", []))
    
    # Create DOCX from the structured notes
    if all_topic_structured_notes:
        filename = "detailed_notes_structured.docx"
        if create_docx_from_parsed_elements(all_topic_structured_notes, filename, subject_name, difficulty_level):
            return filename
    
    st.error("No content generated for detailed notes.")
    return None
```

### Document Creation

#### Creating DOCX from Parsed Elements

```python
def create_docx_from_parsed_elements(all_topics_data, filename, subject_name, difficulty_level):
    try:
        document = Document()
        style = document.styles['Normal']
        font = style.font; font.name = 'Calibri'; font.size = Pt(11)
        document.add_heading(f"Detailed Lecture Notes: {subject_name}", level=0)
        document.add_paragraph(f"Target Audience: {difficulty_level}\n")

        for topic_data in all_topics_data:
            for element in topic_data['elements']:
                el_type = element['type']
                content = element.get('content', '')
                attrs = element.get('attributes', {})
                
                # Process different element types (headings, paragraphs, lists, etc.)
                if el_type == 'heading_1': 
                    document.add_heading(content, level=1)
                elif el_type == 'heading_2': 
                    document.add_heading(content, level=2)
                # ... other element types
                
        document.save(filename)
        return filename
    except Exception as e:
        st.error(f"Error creating detailed notes DOCX: {e}")
        traceback.print_exc()
        return None
```

#### Adding Markdown Formatting to Document

```python
def add_markdown_inline_to_run(paragraph, text_segment):
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text_segment)
    for part in parts:
        if not part: continue
        
        # Bold text
        if part.startswith('**') and part.endswith('**') and len(part) > 4:
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        
        # Italic text
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        
        # Code/monospace text
        elif part.startswith('`') and part.endswith('`') and len(part) > 2:
            run = paragraph.add_run(part[1:-1])
            run.font.name = 'Courier New'
        
        # Regular text
        else:
            paragraph.add_run(part)
```

## User Interface Implementation

The main UI is structured in a step-by-step workflow:

### App Header

```python
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
```

### Step 1: Syllabus and Difficulty

```python
st.markdown("## 📋 Step 1: Syllabus and Parameters")
col1, col2 = st.columns([2,1])
with col1:
    upload_method = st.radio("Syllabus input method:", ["Upload File", "Enter Text"], horizontal=True)
    if upload_method == "Upload File":
        uploaded_syllabus_file = st.file_uploader("Choose a TXT or PDF syllabus", type=["txt", "pdf"])
    else:
        syllabus_text_manual = st.text_area("Paste syllabus text:", height=200)

with col2:
    subject = st.text_input("📝 Subject Name:", placeholder="e.g., Introduction to AI")
    difficulty_level = st.selectbox("🎯 Target Difficulty:", ["Btech", "Mtech", "PHD"])
```

### Step 2: Generate Roadmap

```python
st.markdown("## 🗺️ Step 2: Generate Roadmap")
if syllabus_text_content and subject:
    if st.button("🚀 Generate Roadmap"):
        roadmap_result = generate_roadmap(subject, syllabus_text_content, difficulty_level)
        if roadmap_result:
            st.session_state.roadmap = roadmap_result
            st.rerun()
else:
    st.info("ℹ️ Please provide syllabus text and subject name above to generate a roadmap.")

if "roadmap" in st.session_state:
    edited_roadmap = st.text_area("Roadmap Structure:", value=st.session_state.roadmap, height=300)
    if st.button("💾 Save Edited Roadmap"):
        st.session_state.roadmap = edited_roadmap
        st.success("✅ Roadmap updated!")
```

### Step 3: Generate Lesson Plan

```python
st.markdown("## 📝 Step 3: Generate & Edit Lesson Plan")
if "roadmap" in st.session_state and subject and difficulty_level:
    llm_temp_plan = st.slider("🌡️ AI Creativity (Lesson Plan):", 0.1, 1.0, 0.6, step=0.05)
    plan_depth = st.select_slider("🔍 Detail Level (Lesson Plan):", 
                                  options=[1, 2, 3], 
                                  value=2, 
                                  format_func=lambda x: {1:"Overview", 2:"Standard", 3:"In-Depth"}[x])

    if st.button("🚀 Generate Lesson Plan"):
        with st.spinner("🔄 Generating structured lesson plan... This might take a while."):
            lesson_plan_data = generate_lesson_plan_recursive(subject, st.session_state.roadmap, 
                                                             difficulty_level, llm_temp_plan, plan_depth)
        if lesson_plan_data and lesson_plan_data.get("topics"):
            st.session_state.lesson_plan = lesson_plan_data
            save_lesson_plan_json(st.session_state.lesson_plan)
            st.success("✅ Lesson plan generated! You can now edit it below.")
            st.rerun()
```

### Step 4: Generate Detailed Notes

```python
st.markdown("## 📖 Step 4: Generate Detailed Lecture Notes")
if "lesson_plan" in st.session_state and subject:
    highlighted_topics_input = st.text_area("✍️ Topics for extra examples (comma-separated IDs):")
    llm_temp_notes = st.slider("🌡️ AI Creativity (Notes):", 0.1, 1.0, 0.7, step=0.05)

    if st.button("🚀 Generate Detailed Notes"):
        highlighted = [t.strip() for t in highlighted_topics_input.split(",") if t.strip()]
        with st.spinner("🔄 Generating detailed lecture notes from plan... This can take several minutes."):
            notes_file = create_detailed_notes_recursive(
                st.session_state.lesson_plan, subject, difficulty_level, highlighted, llm_temp_notes
            )
        if notes_file:
            st.session_state.notes_filename = notes_file
            st.success(f"✅ Detailed notes generated as `{notes_file}`!")
            st.rerun()
```

## Data Flow

1. **Input Processing**:
   - Syllabus text (from file upload or direct input)
   - Subject name and difficulty level parameters

2. **Roadmap Creation**:
   - Prompt construction for roadmap generation
   - AI generates hierarchical roadmap
   - Parsing roadmap text into structured dictionary

3. **Lesson Plan Generation**:
   - Hierarchical prompt construction for each topic
   - AI generates content for each topic/subtopic
   - Parsing structured content into JSON format
   - Saving lesson plan to file

4. **Notes Generation**:
   - Extracting content from lesson plan
   - Creating specialized prompts for lecture notes
   - AI generates structured notes content
   - Parsing notes into structured elements

5. **Document Creation**:
   - Converting structured data into DOCX format
   - Applying formatting and styles
   - Saving documents for download

## Optimization Techniques

### Caching

The application implements a simple dictionary-based caching system to avoid redundant AI calls:

```python
generation_cache = {}  # Simple dictionary for caching

# Example usage
cache_key = f"lp_chunk_{topic_data['id']}_{depth}_{str(parent_topics_content)[:100]}"
if cache_key in generation_cache:
    return generation_cache[cache_key]
# ... Generate content
generation_cache[cache_key] = raw_llm_text
```

### Progress Tracking

Long-running operations include progress tracking:

```python
total_items = count_recursive(lesson_plan_json_root.get("topics", []))
item_count = 0
progress_bar = st.progress(0)

# During processing:
item_count += 1
progress_bar.progress(min(1.0, item_count / total_items if total_items > 0 else 1.0))
```

### Error Handling

Comprehensive error handling with informative messages:

```python
try:
    # Operation that might fail
except Exception as e:
    st.error(f"⚠️ Error description: {e}")
    traceback.print_exc()  # Detailed error info for debugging
    return fallback_value
```

## Extension Points

### Adding New AI Models

The model configuration can be modified to use different Gemini models or parameters:

```python
# Current configuration
model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

# To change model or parameters:
model = genai.GenerativeModel(
    'alternative-model-name',
    safety_settings=[
        {"category": "HARM_CATEGORY", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    ]
)
```

### Custom Content Formats

New content structures can be added by extending the tag dictionaries and adding corresponding parsing functions:

```python
# Add new tag to existing dictionary
LECTURE_NOTE_ELEMENT_TAGS["interactive_element"] = "INTERACTIVE"

# Add handling in parsing function
if el_type == 'interactive_element':
    # Custom handling for interactive elements
```

### Alternative Document Formats

The document creation functions can be extended to support additional output formats:

```python
def create_html_from_parsed_elements(all_topics_data, filename, subject_name, difficulty_level):
    # Similar to create_docx_from_parsed_elements but outputs HTML
```

## Performance Considerations

### Memory Usage

- For very large syllabi, text extraction and processing is done in chunks
- Progress updates for long-running operations help manage user expectations

### API Rate Limiting

- Caching mechanism reduces redundant API calls
- Sequential processing with visible progress indicators

### Session State Management

- Streamlit session state preserves user data between interactions
- Clear state management for multi-step workflow

## Conclusion

The Smart Teaching Assistant application demonstrates effective integration of AI content generation with educational structure and formatting. Its modular architecture allows for easy extension and customization, while the comprehensive error handling ensures a smooth user experience even when dealing with complex content generation tasks.
