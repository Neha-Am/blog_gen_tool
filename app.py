import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import PyPDF2


load_dotenv()


genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def read_instructions():
    with open('instructions.txt', 'r') as file:
        return file.read()

def read_pdf_template():
    with open('ieee-conference-template.pdf', 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def generate_paper_content(title, research_field, methodology, expected_results):
    
    instructions = read_instructions()
    
    
    prompt = f"""
    Generate an IEEE conference paper content based on the following details:
    
    Title: {title}
    Research Field: {research_field}
    Methodology: {methodology}
    Expected Results: {expected_results}
    
    Follow these IEEE formatting instructions:
    {instructions}
    
    Generate the content in the following sections:
    1. Abstract (150-250 words)
    2. Introduction
    3. Methodology
    4. Expected Results and Discussion
    5. Conclusion
    6. Keywords (3-5 keywords)
    
    Make sure the content is academic, well-structured, and follows IEEE guidelines.
    """
    
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text

def main():
    st.set_page_config(page_title="IEEE Conference Paper Generator", layout="wide")
    
    st.title("IEEE Conference Paper Content Generator")
    st.markdown("Generate professional IEEE conference paper content based on your inputs.")
    
    # Input fields
    title = st.text_input("Paper Title", placeholder="Enter the title of your research paper")
    
    col1, col2 = st.columns(2)
    with col1:
        research_field = st.text_area("Research Field", 
                                    placeholder="Describe your research field and context")
        methodology = st.text_area("Methodology", 
                                 placeholder="Describe your research methodology")
    
    with col2:
        expected_results = st.text_area("Expected Results", 
                                      placeholder="Describe your expected results or findings")
    
    if st.button("Generate Paper Content"):
        if title and research_field and methodology and expected_results:
            with st.spinner("Generating paper content..."):
                try:
                    generated_content = generate_paper_content(
                        title, research_field, methodology, expected_results
                    )
                    
                    
                    st.success("Content generated successfully!")
                    st.markdown("## Generated Paper Content")
                    st.markdown(generated_content)
                    
                    # Add download button
                    st.download_button(
                        label="Download Content",
                        data=generated_content,
                        file_name="generated_paper.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please fill in all the fields to generate the paper content.")

if __name__ == "__main__":
    main() 