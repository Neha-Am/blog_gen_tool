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

def extract_text_from_uploaded_pdf(uploaded_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def create_ieee_pdf(content_dict, filename, author_info=None):
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
    
    # Author information - use provided info or placeholder
    if author_info and (author_info.get('Author Name') or author_info.get('Email ID') or author_info.get('Institution/Organization')):
        author_text = ""
        if author_info.get('Author Name'):
            author_text += author_info['Author Name'] + "<br/>"
        if author_info.get('Institution/Organization'):
            author_text += author_info['Institution/Organization'] + "<br/>"
        if author_info.get('Email ID'):
            author_text += author_info['Email ID']
        
        if not author_text:
            author_text = "Author Name(s)<br/>Institution(s)<br/>Email Address(es)"
    else:
        author_text = "Author Name(s)<br/>Institution(s)<br/>Email Address(es)"
    
    story.append(Paragraph(author_text, author_style))
    
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
        # Handle content with better paragraph splitting
        if content and content.strip():
            # Split by double newlines first, then by single newlines
            paragraphs = content.split('\n\n')
            for p in paragraphs:
                if p.strip():
                    # Further split by single newlines if needed
                    sub_paragraphs = p.split('\n')
                    for sub_p in sub_paragraphs:
                        if sub_p.strip():
                            story.append(Paragraph(sub_p.strip(), body_style))
                    # Add spacing between paragraphs
                    story.append(Spacer(1, 6))
        else:
            # If section is empty, add a placeholder
            story.append(Paragraph(f"[{heading} content will be generated]", body_style))
            story.append(Spacer(1, 12))
    
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
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        lower_line = line.lower()
        
        # Check for section headers with more flexible matching
        if any(keyword in lower_line for keyword in ['abstract']) and len(line) < 30:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'abstract'
            current_content = []
            
        elif any(keyword in lower_line for keyword in ['keywords', 'keyword']) and len(line) < 50:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'keywords'
            current_content = []
            
        elif any(keyword in lower_line for keyword in ['introduction', 'i. introduction', '1. introduction']):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'introduction'
            current_content = []
            
        elif any(keyword in lower_line for keyword in ['methodology', 'methods', 'ii. methodology', '2. methodology']):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'methodology'
            current_content = []
            
        elif any(keyword in lower_line for keyword in ['results', 'discussion', 'expected results', 'iii. expected results', '3. expected results']):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'results'
            current_content = []
            
        elif any(keyword in lower_line for keyword in ['conclusion', 'conclusions', 'iv. conclusion', '4. conclusion']):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'conclusion'
            current_content = []
            
        elif current_section and line:
            # Add content to current section
            current_content.append(line)
    
    # Save the last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    # Clean up sections - remove any empty sections
    for key in sections:
        if not sections[key]:
            sections[key] = f"[{key.title()} content will be generated]"
    
    return sections

def generate_paper_content(title, research_field, methodology, expected_results, additional_context="", custom_parameters=None):
    
    instructions = read_instructions()
    
    # Build context from uploaded PDF if available
    context_info = ""
    if additional_context:
        context_info = f"\nAdditional Context from uploaded material:\n{additional_context}\n"
    
    # Build custom parameters info if provided
    custom_params_info = ""
    if custom_parameters:
        custom_params_info = "\nAdditional Parameters:\n"
        for param_name, param_value in custom_parameters.items():
            if param_value:  # Only include non-empty parameters
                custom_params_info += f"- {param_name}: {param_value}\n"
    
    prompt = f"""
    Generate an IEEE conference paper content based on the following details:
    
    Title: {title}
    Research Field: {research_field}
    Methodology: {methodology}
    Expected Results: {expected_results}{context_info}{custom_params_info}
    
    Follow these IEEE formatting instructions:
    {instructions}
    
    Generate the content in the following sections with clear headers:
    
    Abstract
    [Generate 150-250 word abstract here]
    
    Keywords
    [Generate 3-5 keywords separated by commas]
    
    I. INTRODUCTION
    [Generate introduction content here]
    
    II. METHODOLOGY
    [Generate methodology content here]
    
    III. EXPECTED RESULTS AND DISCUSSION
    [Generate results and discussion content here]
    
    IV. CONCLUSION
    [Generate conclusion content here]
    
    IMPORTANT: 
    1. Generate only the academic paper content. Do NOT include any conversation, explanations, or meta-commentary about the generation process.
    2. Use the exact section headers as shown above (Abstract, Keywords, I. INTRODUCTION, etc.)
    3. The output should be a clean, professional research paper that could be directly submitted to an IEEE conference.
    4. Ensure each section has substantial content (at least 2-3 paragraphs for main sections).
    5. Make sure the content is academic, well-structured, and follows IEEE guidelines.
    """
    
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text

def main():
    st.set_page_config(page_title="IEEE Conference Paper Generator", layout="wide")
    
    st.title("IEEE Conference Paper Content Generator")
    st.markdown("Generate professional IEEE conference paper content based on your inputs.")
    
    # PDF Upload Section
    st.markdown("## 📄 Upload Reference Material (Optional)")
    st.markdown("Upload a PDF to provide additional context for the paper generation.")
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    additional_context = ""
    if uploaded_file is not None:
        additional_context = extract_text_from_uploaded_pdf(uploaded_file)
        if additional_context:
            st.success("PDF uploaded successfully! Content will be used as additional context.")
            with st.expander("Preview uploaded content"):
                st.text(additional_context[:500] + "..." if len(additional_context) > 500 else additional_context)
    
    # Main Input Section
    st.markdown("## 📝 Paper Details")
    
    # Required inputs
    title = st.text_input("Paper Title *", placeholder="Enter the title of your research paper")
    
    col1, col2 = st.columns(2)
    with col1:
        research_field = st.text_area("Research Field *", 
                                    placeholder="Describe your research field and context")
        methodology = st.text_area("Methodology *", 
                                 placeholder="Describe your research methodology")
    
    with col2:
        expected_results = st.text_area("Expected Results *", 
                                      placeholder="Describe your expected results or findings")
    
    # Optional Parameters Section
    st.markdown("## ⚙️ Additional Parameters (Optional)")
    st.markdown("These parameters are optional and will provide additional context for paper generation.")
    
    # Author Information Section
    st.markdown("### 👤 Author Information (Optional)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        author_name = st.text_input("Author Name", placeholder="e.g., John Smith")
    
    with col2:
        email_id = st.text_input("Email ID", placeholder="e.g., john.smith@university.edu")
    
    with col3:
        institution = st.text_input("Institution/Organization", placeholder="e.g., University of Technology")
    
    # Additional Custom Parameters
    st.markdown("### 🔧 Additional Parameters (Optional)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        custom_param1 = st.text_input("Parameter 1", placeholder="e.g., Dataset size, Algorithm type")
        custom_param2 = st.text_input("Parameter 2", placeholder="e.g., Evaluation metrics")
    
    with col2:
        custom_param3 = st.text_input("Parameter 3", placeholder="e.g., Implementation details")
        custom_param4 = st.text_input("Parameter 4", placeholder="e.g., Related work focus")
    
    with col3:
        custom_param5 = st.text_input("Parameter 5", placeholder="e.g., Future work direction")
        custom_param6 = st.text_input("Parameter 6", placeholder="e.g., Technical constraints")
    
    # Collect custom parameters including author information
    custom_parameters = {
        "Author Name": author_name,
        "Email ID": email_id,
        "Institution/Organization": institution,
        "Parameter 1": custom_param1,
        "Parameter 2": custom_param2,
        "Parameter 3": custom_param3,
        "Parameter 4": custom_param4,
        "Parameter 5": custom_param5,
        "Parameter 6": custom_param6
    }
    
    if st.button("Generate Paper Content"):
        if title and research_field and methodology and expected_results:
            with st.spinner("Generating paper content..."):
                try:
                    generated_content = generate_paper_content(
                        title, research_field, methodology, expected_results, 
                        additional_context, custom_parameters
                    )
                    
                    
                    st.success("Content generated successfully!")
                    st.markdown("## Generated Paper Content")
                    st.markdown(generated_content)
                    
                    # Parse the generated content into sections
                    content_dict = parse_generated_content(generated_content)
                    content_dict['title'] = title  # Use the original title
                    
                    # Generate PDF
                    pdf_buffer = create_ieee_pdf(content_dict, "generated_paper.pdf", custom_parameters)
                    
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
            st.warning("Please fill in all the required fields (marked with *) to generate the paper content.")

if __name__ == "__main__":
    main() 
