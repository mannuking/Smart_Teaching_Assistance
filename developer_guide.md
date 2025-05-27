# Smart Teaching Assistant - Developer Guide

## Architecture Overview

Smart Teaching Assistant follows a modular architecture that combines Streamlit for the UI layer with Google's Gemini API for content generation. The application is designed around a sequential workflow pattern where each step builds upon the previous one.

```
┌─────────────────────┐
│  User Interface     │
│  (Streamlit)        │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Application Logic  │
│  (Processing)       │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  AI Content         │
│  Generation (Gemini)│
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Document Creation  │
│  (python-docx)      │
└─────────────────────┘
```

## Code Structure

### Main Components

- **UI Layer**: Streamlit components for user interaction
- **Processing Layer**: Functions that process user input and prepare AI prompts
- **AI Integration**: Gemini API integration for content generation
- **Document Creation**: DOCX creation and formatting utilities

### Key Files

- `app3.py`: Main application file containing all components
- `requirements.txt`: Package dependencies
- `.env`: Environment variables (API keys)

## Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Smart_Teaching_Assistance.git
   cd Smart_Teaching_Assistance
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install development tools**
   ```bash
   pip install black flake8 pytest
   ```

5. **Configure Google API key**
   - Create a `.env` file with your API key
   - Format: `GOOGLE_API_KEY=your_api_key_here`

## Development Workflow

### Running the Application Locally

```bash
streamlit run app3.py
```

### Code Formatting

```bash
black app3.py
```

### Code Linting

```bash
flake8 app3.py
```

## Core Function Documentation

### Syllabus Processing

#### `extract_text_from_pdf(pdf_file)`
Extracts text content from a PDF file.

**Parameters:**
- `pdf_file`: File object from Streamlit's file_uploader

**Returns:**
- `str`: Extracted text content or None if extraction fails

**Example:**
```python
uploaded_file = st.file_uploader("Upload PDF", type="pdf")
if uploaded_file:
    text_content = extract_text_from_pdf(uploaded_file)
```

#### `generate_roadmap(subject, syllabus_text, difficulty_level, temperature=0.6)`
Generates a structured roadmap from syllabus text.

**Parameters:**
- `subject`: Subject name (string)
- `syllabus_text`: Text content of the syllabus (string)
- `difficulty_level`: Target difficulty level (string)
- `temperature`: AI creativity parameter (float, 0.1-1.0)

**Returns:**
- `str`: Generated roadmap text or None if generation fails

### Roadmap Parsing

#### `parse_roadmap(roadmap_text)`
Parses roadmap text into a structured dictionary.

**Parameters:**
- `roadmap_text`: Text of the roadmap (string)

**Returns:**
- `dict`: Structured representation of the roadmap

### Lesson Plan Generation

#### `generate_lesson_plan_recursive(subject, roadmap_text, difficulty_level, temperature=0.7, depth_setting=1)`
Recursively generates a lesson plan from a roadmap.

**Parameters:**
- `subject`: Subject name (string)
- `roadmap_text`: Roadmap text (string)
- `difficulty_level`: Target difficulty level (string)
- `temperature`: AI creativity parameter (float, 0.1-1.0)
- `depth_setting`: Detail level (int, 1-3)

**Returns:**
- `dict`: JSON-structured lesson plan

### Notes Generation

#### `create_detailed_notes_recursive(lesson_plan_json_root, subject_name, difficulty_level, highlighted_topics, temperature=0.7)`
Recursively generates detailed notes from a lesson plan.

**Parameters:**
- `lesson_plan_json_root`: Lesson plan JSON structure (dict)
- `subject_name`: Subject name (string)
- `difficulty_level`: Target difficulty level (string)
- `highlighted_topics`: List of topic IDs to emphasize (list)
- `temperature`: AI creativity parameter (float, 0.1-1.0)

**Returns:**
- `str`: Filename of the generated DOCX or None if generation fails

## Extending the Application

### Adding a New AI Model

To integrate a different AI model:

1. Add the necessary package to `requirements.txt`
2. Create a new function for the API integration
3. Update the relevant generation functions

Example:
```python
from alternative_ai_provider import AltAI

def generate_with_alt_ai(prompt, temperature=0.7):
    client = AltAI(api_key=os.getenv("ALT_AI_API_KEY"))
    response = client.generate_text(
        prompt=prompt,
        temperature=temperature
    )
    return response.text
```

### Adding a New Output Format

To add a new output format (e.g., HTML):

1. Create a conversion function:
```python
def create_html_from_parsed_elements(all_topics_data, filename, subject_name, difficulty_level):
    html_content = f"<html><head><title>{subject_name} - Notes</title></head><body>"
    html_content += f"<h1>{subject_name} - Detailed Notes</h1>"
    html_content += f"<p>Difficulty Level: {difficulty_level}</p>"
    
    for topic_data in all_topics_data:
        # Process elements and build HTML
        
    html_content += "</body></html>"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return filename
```

2. Add a UI option for the new format:
```python
output_format = st.selectbox("Output Format:", ["DOCX", "HTML", "PDF"])
```

3. Update the generation function to use the appropriate converter:
```python
if output_format == "DOCX":
    filename = create_docx_from_parsed_elements(...)
elif output_format == "HTML":
    filename = create_html_from_parsed_elements(...)
```

### Adding a New Feature

To add a new feature (e.g., assessment question generation):

1. Create the prompt generation function:
```python
def create_assessment_prompt(topic_data, difficulty_level, question_count=5):
    prompt = f"""
    Generate {question_count} assessment questions for:
    Topic: {topic_data['id']}: {topic_data['title']}
    Difficulty: {difficulty_level}
    
    Include a mix of multiple choice, short answer, and essay questions.
    For each question, provide the correct answer or evaluation criteria.
    """
    return prompt
```

2. Create the generation function:
```python
def generate_assessment_questions(lesson_plan_json, topic_id, difficulty_level, question_count=5, temperature=0.7):
    topic_data = extract_lesson_plan_entry(lesson_plan_json, topic_id)
    if not topic_data:
        return []
    
    prompt = create_assessment_prompt(topic_data, difficulty_level, question_count)
    response = generate_text_from_prompt(prompt, temperature, purpose="assessment")
    
    # Parse response into questions and answers
    parsed_questions = parse_assessment_response(response)
    
    return parsed_questions
```

3. Add UI elements:
```python
st.markdown("## 📝 Step 5: Generate Assessment Questions")
if "lesson_plan" in st.session_state and subject:
    topic_for_assessment = st.selectbox("Select Topic for Assessment:", 
                                        [f"{t['id']}: {t['title']}" for t in st.session_state.lesson_plan.get("topics", [])])
    
    question_count = st.slider("Number of Questions:", 5, 20, 10)
    
    if st.button("Generate Assessment"):
        topic_id = topic_for_assessment.split(":")[0].strip()
        questions = generate_assessment_questions(st.session_state.lesson_plan, topic_id, 
                                                difficulty_level, question_count)
        # Display questions
```

## Performance Optimization

### Caching Strategies

The application uses a dictionary-based caching system to avoid redundant API calls:

```python
generation_cache = {}  # Simple dictionary for caching

# Before generating content, check cache
cache_key = f"content_type_{parameters_hash}"
if cache_key in generation_cache:
    return generation_cache[cache_key]

# After generating content, store in cache
generation_cache[cache_key] = generated_content
```

For a more robust caching solution, consider implementing:

1. **Persistent caching** using SQLite or Redis:
```python
import sqlite3

def get_from_cache(cache_key):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    cursor.execute('SELECT content FROM cache WHERE key = ?', (cache_key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def store_in_cache(cache_key, content):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO cache (key, content) VALUES (?, ?)', 
                  (cache_key, content))
    conn.commit()
    conn.close()
```

2. **Time-based cache expiration**:
```python
import time

cache_with_timestamp = {}

def get_cached_content(key, max_age_seconds=3600):
    if key in cache_with_timestamp:
        timestamp, content = cache_with_timestamp[key]
        if time.time() - timestamp < max_age_seconds:
            return content
    return None

def cache_content(key, content):
    cache_with_timestamp[key] = (time.time(), content)
```

### Memory Management

For large documents and complex generations:

1. **Chunking large documents**:
```python
def process_large_document(document_text, chunk_size=5000):
    chunks = [document_text[i:i+chunk_size] for i in range(0, len(document_text), chunk_size)]
    results = []
    
    for chunk in chunks:
        # Process each chunk separately
        result = process_chunk(chunk)
        results.append(result)
    
    # Combine results
    return combine_results(results)
```

2. **Limiting concurrent operations**:
```python
def process_with_rate_limit(items, process_func, max_concurrent=3, delay_seconds=1):
    results = []
    for i, item in enumerate(items):
        results.append(process_func(item))
        
        # Apply rate limiting
        if i % max_concurrent == max_concurrent - 1 and i < len(items) - 1:
            time.sleep(delay_seconds)
    
    return results
```

## Testing

### Unit Tests

Create test functions for core functionality:

```python
import pytest

def test_parse_roadmap():
    sample_roadmap = """
    Sequence: Linear
    
    T1: Sample Topic
        T1.1: Sample Subtopic
    """
    result = parse_roadmap(sample_roadmap)
    
    assert result["sequence"] == "Linear"
    assert len(result["topics"]) == 1
    assert result["topics"][0]["id"] == "T1"
    assert result["topics"][0]["description"] == "Sample Topic"
    assert len(result["topics"][0]["subtopics"]) == 1
```

### Mock Testing for AI Integration

Use mocks to test AI-dependent functions:

```python
from unittest.mock import patch

@patch('app3.model.generate_content')
def test_generate_roadmap(mock_generate):
    # Configure the mock
    mock_generate.return_value.text = "Sequence: Linear\n\nT1: Test Topic"
    
    result = generate_roadmap("Test Subject", "Test syllabus", "Btech")
    
    assert "T1: Test Topic" in result
    mock_generate.assert_called_once()
```

### End-to-End Testing

Test the full workflow with sample inputs:

```python
def test_full_workflow():
    # Sample inputs
    subject = "Test Subject"
    syllabus = "Sample syllabus content"
    difficulty = "Btech"
    
    # Generate roadmap
    roadmap = generate_roadmap(subject, syllabus, difficulty)
    assert roadmap is not None
    
    # Parse roadmap
    roadmap_dict = parse_roadmap(roadmap)
    assert len(roadmap_dict["topics"]) > 0
    
    # Generate lesson plan
    lesson_plan = generate_lesson_plan_recursive(subject, roadmap, difficulty)
    assert lesson_plan is not None
    assert "topics" in lesson_plan
    
    # Generate notes
    notes_file = create_detailed_notes_recursive(lesson_plan, subject, difficulty, [])
    assert notes_file is not None
    assert os.path.exists(notes_file)
```

## Deployment

### Local Deployment

For personal or team use:

```bash
streamlit run app3.py --server.port 8501
```

### Server Deployment

For shared server deployment:

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Create a service**:
```
[Unit]
Description=Smart Teaching Assistant Streamlit App
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/Smart_Teaching_Assistance
ExecStart=/path/to/venv/bin/streamlit run app3.py --server.port 8501 --server.address 0.0.0.0
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

3. **Set up a reverse proxy** with Nginx:
```
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### Docker Deployment

Create a Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app3.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t smart-teaching-assistant .
docker run -p 8501:8501 -v ~/.streamlit:/root/.streamlit smart-teaching-assistant
```

## Contributing Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use descriptive variable and function names
- Add docstrings to all functions
- Use type hints where appropriate

### Commit Standards

Format: `[type]: [description]`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, etc
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding tests
- `chore`: Maintenance tasks

Example: `feat: Add assessment question generation`

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: Add your feature"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a pull request

### Review Process

All contributions will be reviewed for:
- Code quality and adherence to style guidelines
- Proper test coverage
- Documentation completeness
- Performance impact

## API Reference

### Gemini API

This application uses Google's Gemini API for content generation. Key classes and methods:

```python
from google import generativeai as genai

# Configure API
genai.configure(api_key=your_api_key)

# Create a model instance
model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

# Generate content
response = model.generate_content(
    prompt,
    generation_config=genai.types.GenerationConfig(
        temperature=temperature,
        # Additional options:
        # max_output_tokens=1024,
        # top_p=0.9,
        # top_k=40,
    )
)

# Access the response
generated_text = response.text
```

For more details, refer to the [Google AI Gemini API documentation](https://ai.google.dev/).

## Licensing and Credits

This project is licensed under the MIT License.

Acknowledgments:
- [Streamlit](https://streamlit.io/) for the UI framework
- [Google Generative AI](https://ai.google.dev/) for content generation
- [python-docx](https://python-docx.readthedocs.io/) for document creation
- [PyPDF](https://pypdf.readthedocs.io/) for PDF processing

## Contact

For questions, contributions, or support:
- Email: jk422331@gmail.com
- GitHub: [Your GitHub Profile](https://github.com/yourusername)
