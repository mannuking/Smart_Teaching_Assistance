def evaluate_notes_with_advanced_ai(notes_content, subject, difficulty_level, evaluation_aspects, evaluation_depth):
    """
    Evaluates the generated notes using the advanced Gemini 2.5 Pro model
    """
    try:
        # Make sure we're using the latest API key configuration
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("🚨 Google API key not found. Please check your .env file.")
            return None
        
        # Initialize the advanced model for evaluation with explicit API key
        genai.configure(api_key=api_key)
        evaluation_model = genai.GenerativeModel('gemini-2.5-pro-preview-05-06')
        
        # Build comprehensive evaluation prompt
        evaluation_prompt = build_evaluation_prompt(
            notes_content, subject, difficulty_level, evaluation_aspects, evaluation_depth
        )
        
        # Generate evaluation using the advanced model
        response = evaluation_model.generate_content(
            evaluation_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,  # Lower temperature for more analytical, consistent evaluation
                max_output_tokens=4096
            )
        )
        
        return response.text.strip()
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower() or "resource exhausted" in error_msg.lower():
            st.error(f"""🚨 API quota exceeded or rate limit reached.

This is likely because the Gemini 2.5 Pro Preview model has usage limitations.

**Troubleshooting steps:**
1. Confirm your API key is correctly set in the .env file
2. Verify that your API key has access to the Gemini 2.5 Pro Preview model
3. Try again later as API quotas are often reset daily

Current API key: {api_key[:5]}...{api_key[-4:]}""")
        else:
            st.error(f"Error during evaluation: {error_msg}")
        return None
