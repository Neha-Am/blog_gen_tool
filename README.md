# IEEE Conference Paper Content Generator

A Streamlit application that helps researchers generate IEEE-formatted conference paper content based on their inputs. The application uses Google's Generative AI to create well-structured academic content following IEEE guidelines.

## Features

- Interactive web interface built with Streamlit
- Generates paper content based on user inputs:
  - Paper Title
  - Research Field
  - Methodology
  - Expected Results
- Follows IEEE conference paper formatting guidelines
- Downloads generated content as a text file
- Uses Google's Generative AI for content generation

## Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Running the Application

To run the application, execute:
```bash
streamlit run app.py
```

The application will open in your default web browser.

## Usage

1. Fill in the required fields:
   - Enter your paper title
   - Describe your research field
   - Explain your methodology
   - Outline your expected results

2. Click "Generate Paper Content" to create the IEEE-formatted content

3. Review the generated content and use the download button to save it as a text file

## Requirements

- Python 3.7+
- Streamlit
- Google Generative AI
- python-dotenv
- PyPDF2

## Note

Make sure you have a valid Google API key with access to the Generative AI services. The application requires the IEEE conference template PDF and instructions file to be present in the root directory. 