from crewai import Agent
from textwrap import dedent
import google.generativeai as genai
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

class BlogAgents:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv('GOOGLE_API_KEY'),
            temperature=0.7
        )

    def create_research_agent(self):
        return Agent(
            role='Research Specialist',
            goal='Gather comprehensive information about the given topic',
            backstory=dedent("""
                You are an expert researcher with years of experience in gathering
                and analyzing information from various sources. Your expertise lies
                in finding accurate and relevant information quickly.
            """),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def create_nlp_agent(self):
        return Agent(
            role='NLP Specialist',
            goal='Process and analyze the gathered information using NLP techniques',
            backstory=dedent("""
                You are an NLP expert who specializes in text processing and analysis.
                You can identify key themes, extract important information, and structure
                content effectively.
            """),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def create_writer_agent(self):
        return Agent(
            role='Content Writer',
            goal='Create engaging and well-structured blog content',
            backstory=dedent("""
                You are a professional content writer with expertise in creating
                engaging and informative blog posts. You know how to structure
                content effectively and maintain reader interest.
            """),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def create_plagiarism_checker_agent(self):
        return Agent(
            role='Plagiarism Checker',
            goal='Analyze content originality and provide a plagiarism score based on specific criteria',
            backstory=dedent("""
                You are an expert in content verification and plagiarism detection.
                You analyze content based on the following specific criteria, each worth 20 points:

                1. Writing Style Originality (20 points):
                   - Unique sentence structures
                   - Personal voice and tone
                   - Creative expression
                   - Avoidance of clichés

                2. Content Structure (20 points):
                   - Original organization
                   - Unique flow and transitions
                   - Creative section arrangement
                   - Innovative presentation

                3. Language and Vocabulary (20 points):
                   - Unique word choices
                   - Varied vocabulary
                   - Creative metaphors
                   - Original expressions

                4. Idea Development (20 points):
                   - Original perspectives
                   - Unique insights
                   - Creative connections
                   - Innovative approaches

                5. Technical Elements (20 points):
                   - Original examples
                   - Unique data presentation
                   - Creative formatting
                   - Innovative use of technical terms

                Reference Content for SEO-related checks:
                Post-AI SEO Optimization Strategies (For Gemini & AI-Powered Search)
                
                Strategy Areas and Best Practices:
                1. Focus on User Intent & Context
                   - Create content that answers questions fully
                   - Cover related topics
                   - Use natural language and conversational tone
                
                2. E-E-A-T & Experience Emphasis
                   - Showcase real user experience
                   - Include credentials and authoritative signals
                   - Add case studies, testimonials, and expert quotes
                
                3. Multimodal Content
                   - Incorporate images, videos, infographics
                   - Use AR/VR elements if applicable
                   - Implement structured data (schema)
                
                4. Content Depth & Freshness
                   - Regular content updates
                   - Comprehensive topic coverage
                   - Authority hub development
                
                5. Technical SEO & UX
                   - Fast loading optimization
                   - Mobile responsiveness
                   - Accessibility compliance
                   - Core Web Vitals optimization
                
                6. Semantic & Topical SEO
                   - Use related keywords and LSI terms
                   - Structure for AI comprehension
                   - Implement clear headings and FAQs
                
                7. AI-Generated Snippets
                   - Clear, concise answers
                   - Well-structured definitions
                   - Data presentation in lists
                
                8. Link Quality
                   - Focus on trusted sources
                   - Build relevant backlinks
                   - Prioritize authority over quantity
                
                9. Privacy-Conscious SEO
                   - Minimize tracking
                   - Respect user consent
                   - Optimize for privacy-first signals
                
                10. Interactive Content
                    - Include quizzes and polls
                    - Implement chatbots
                    - Add interactive tools

                For each criterion, provide:
                - Score (0-20)
                - Specific examples from the text
                - Areas for improvement
                - Recommendations

                Calculate the final score (0-100) by summing all criteria scores.
                A score of:
                - 90-100: Highly original
                - 70-89: Mostly original
                - 50-69: Moderately original
                - 30-49: Needs improvement
                - 0-29: Significant concerns

                When checking SEO-related content, pay special attention to:
                1. Whether the content is directly copying from the reference SEO strategies
                2. If the content is merely rephrasing the reference material
                3. How the content builds upon or adds value to these basic strategies
                4. The originality of the implementation examples and case studies
            """),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )