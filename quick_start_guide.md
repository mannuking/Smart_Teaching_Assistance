# Smart Teaching Assistant - Quick Start Guide

## Overview

Smart Teaching Assistant is an AI-powered application that helps educators quickly create detailed teaching materials from a simple syllabus. This quick start guide will help you set up and begin using the application within minutes.

## Installation in 5 Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Smart_Teaching_Assistance.git
   cd Smart_Teaching_Assistance
   ```

2. **Create a virtual environment and activate it**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your Google API key**
   - Create a `.env` file in the project directory
   - Add your API key: `GOOGLE_API_KEY=your_key_here`

5. **Launch the application**
   ```bash
   streamlit run app3.py
   ```

## Creating Teaching Materials in 4 Steps

### Step 1: Input Your Syllabus
- Choose "Upload File" (TXT/PDF) or "Enter Text" directly
- Enter the subject name (e.g., "Introduction to Programming")
- Select the target difficulty level (Btech, Mtech, PHD)

### Step 2: Generate a Roadmap
- Click "Generate Roadmap"
- Review the hierarchical topic structure
- Edit if needed and save your changes

### Step 3: Create a Lesson Plan
- Adjust the AI creativity slider (0.1-1.0)
- Select detail level (Overview, Standard, In-Depth)
- Click "Generate Lesson Plan"
- Edit any section of the lesson plan as desired
- Save your changes and/or download as a DOCX file

### Step 4: Generate Lecture Notes
- Optionally enter topic IDs to emphasize (e.g., "T1.1, T2.3")
- Adjust AI creativity for notes generation
- Click "Generate Detailed Notes"
- Download the resulting DOCX file

## Tips for Best Results

- **Provide specific details** in your syllabus for better output
- **Use lower creativity settings** (0.3-0.6) for technical/factual subjects
- **Use higher creativity settings** (0.7-0.9) for subjects requiring varied examples
- **Save your work** after each major step
- **Edit the generated content** to add your personal teaching style and expertise

## Keyboard Shortcuts

- `Ctrl+Enter` in text areas to submit
- `Escape` to clear selection
- Use the Tab key to navigate between UI elements

## Additional Resources

- For detailed information, consult the comprehensive [User Manual](user_manual.md)
- For UI details, see the [UI Documentation](UI.md)
- For technical details, refer to the [Technical Documentation](technical_documentation.md)

## Need Help?

Contact: jk422331@gmail.com
