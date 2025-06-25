import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import PyPDF2
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame, PageTemplate, NextPageTemplate
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import FrameBreak, KeepTogether
from io import BytesIO
import tempfile


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

def create_ieee_pdf(content_dict, filename):
    buffer = BytesIO()
    
    # Initialize document with IEEE specs
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Calculate column widths
    page_width = A4[0]
    page_height = A4[1]
    margin_left = 0.75 * inch
    margin_right = 0.75 * inch
    margin_top = 0.75 * inch
    margin_bottom = 0.75 * inch
    column_gap = 0.25 * inch
    column_width = (page_width - margin_left - margin_right - column_gap) / 2
    
    # Create frames for two-column layout
    frame1 = Frame(
        margin_left, 
        margin_bottom,
        column_width,
        page_height - margin_top - margin_bottom,
        id='col1'
    )
    frame2 = Frame(
        margin_left + column_width + column_gap,
        margin_bottom,
        column_width,
        page_height - margin_top - margin_bottom,
        id='col2'
    )
    
    # Create page template
    template = PageTemplate(
        id='TwoCol',
        frames=[frame1, frame2]
    )
    doc.addPageTemplates([template])
    
    # Define styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'IEEETitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName='Times-Bold'
    )
    
    author_style = ParagraphStyle(
        'IEEEAuthor',
        parent=styles['Normal'],
        fontSize=12,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Times-Roman'
    )
    
    heading_style = ParagraphStyle(
        'IEEEHeading',
        parent=styles['Heading2'],
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6,
        fontName='Times-Bold',
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'IEEEBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        alignment=TA_JUSTIFY,
        fontName='Times-Roman',
        firstLineIndent=18
    )
    
    abstract_style = ParagraphStyle(
        'IEEEAbstract',
        parent=body_style,
        fontSize=9,
        leading=11,
        alignment=TA_JUSTIFY,
        firstLineIndent=0
    )
    
    keywords_style = ParagraphStyle(
        'IEEEKeywords',
        parent=abstract_style,
        firstLineIndent=0,
        alignment=TA_LEFT,
        spaceBefore=6
    )
    
    # Build document content
    story = []
    
    # Title (spans both columns)
    story.append(NextPageTemplate('TwoCol'))
    story.append(Paragraph(content_dict['title'].upper(), title_style))
    
    # Author placeholder
    story.append(Paragraph("Author Name(s)<br/>Institution(s)<br/>Email Address(es)", author_style))
    
    # Abstract
    abstract_heading = Paragraph('<b>Abstract</b>&mdash;' + content_dict['abstract'], abstract_style)
    story.append(KeepTogether([abstract_heading]))
    
    # Keywords
    keywords_text = '<i>Keywords</i>&mdash;' + content_dict['keywords']
    story.append(Paragraph(keywords_text, keywords_style))
    story.append(Spacer(1, 12))
    
    # Main sections
    sections = [
        ('I. INTRODUCTION', content_dict['introduction']),
        ('II. METHODOLOGY', content_dict['methodology']),
        ('III. EXPECTED RESULTS AND DISCUSSION', content_dict['results']),
        ('IV. CONCLUSION', content_dict['conclusion'])
    ]
    
    for heading, content in sections:
        story.append(Paragraph(heading, heading_style))
        paragraphs = content.split('\n\n')
        for p in paragraphs:
            if p.strip():
                story.append(Paragraph(p.strip(), body_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def parse_generated_content(content):
    sections = {
        'title': '',
        'abstract': '',
        'keywords': '',
        'introduction': '',
        'methodology': '',
        'results': '',
        'conclusion': ''
    }
    
    current_section = None
    current_content = []
    
    for line in content.split('\n'):
        line = line.strip()
        lower_line = line.lower()
        
        if 'abstract' in lower_line and len(line) < 20:
            current_section = 'abstract'
            current_content = []
        elif 'keywords' in lower_line and len(line) < 20:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'keywords'
            current_content = []
        elif 'introduction' in lower_line and len(line) < 20:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'introduction'
            current_content = []
        elif 'methodology' in lower_line and len(line) < 20:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'methodology'
            current_content = []
        elif 'results' in lower_line and 'discussion' in lower_line and len(line) < 35:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'results'
            current_content = []
        elif 'conclusion' in lower_line and len(line) < 20:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'conclusion'
            current_content = []
        elif current_section and line:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections

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
                    
                    # Parse the generated content into sections
                    content_dict = parse_generated_content(generated_content)
                    content_dict['title'] = title  # Use the original title
                    
                    # Generate PDF
                    pdf_buffer = create_ieee_pdf(content_dict, "generated_paper.pdf")
                    
                    # Add download buttons for both formats
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="Download as Text",
                            data=generated_content,
                            file_name="generated_paper.txt",
                            mime="text/plain"
                        )
                    with col2:
                        st.download_button(
                            label="Download as PDF",
                            data=pdf_buffer,
                            file_name="generated_paper.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please fill in all the fields to generate the paper content.")

if __name__ == "__main__":
    main() 
