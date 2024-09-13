import streamlit as st
import pandas as pd
import re
import os
import tempfile
from datetime import datetime

# Set page config
st.set_page_config(page_title="Advanced Log Analyzer", layout="wide")

# Function to highlight keywords
def highlight_keywords(text):
    keywords = ['DEBUG', 'INFO', 'ERROR', 'WARNING', 'Failed', 'TIMEOUT', 'Committing', 'WARN']
    pattern = '|'.join(map(re.escape, keywords))
    return re.sub(f'({pattern})', r'<span style="background-color: yellow;">\1</span>', text, flags=re.IGNORECASE)

# Function to search for error messages
def search_errors(content, search_term):
    lines = content.split('\n')
    results = []
    for i, line in enumerate(lines):
        if search_term.lower() in line.lower():
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            context = '\n'.join(lines[start:end])
            results.append({
                'line_number': i + 1,
                'context': highlight_keywords(context)
            })
    return results

# Function to save search results
def save_search_results(results, search_term):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"search_results_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write(f"Search Term: {search_term}\n\n")
        for result in results:
            f.write(f"Line {result['line_number']}:\n{result['context']}\n\n")
    return filename

# Main application
def main():
    st.title("Advanced Log Analyzer")

    # File uploader
    uploaded_file = st.file_uploader("Choose a log file (up to 50MB)", type=['txt', 'log'])

    if uploaded_file is not None:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
        st.write(file_details)

        # Check file size
        if uploaded_file.size > 50 * 1024 * 1024:  # 50MB in bytes
            st.error("File size exceeds 50MB limit. Please upload a smaller file.")
            return

        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        # Search functionality
        search_term = st.text_input("Enter search term:")
        if st.button("Search"):
            with open(tmp_file_path, 'r') as file:
                content = file.read()
                results = search_errors(content, search_term)

            if results:
                st.subheader(f"Search Results for '{search_term}':")
                for result in results:
                    st.markdown(f"**Line {result['line_number']}:**")
                    st.markdown(result['context'], unsafe_allow_html=True)
                    st.markdown("---")

                # Save results
                saved_file = save_search_results(results, search_term)
                st.success(f"Search results saved to {saved_file}")
            else:
                st.info("No results found.")

        # Option to view entire file content
        if st.checkbox("View entire file content"):
            with open(tmp_file_path, 'r') as file:
                content = file.read()
                highlighted_content = highlight_keywords(content)
                st.markdown(highlighted_content, unsafe_allow_html=True)

        # Clean up temporary file
        os.unlink(tmp_file_path)

    # Back button
    if st.button("Back"):
        st.experimental_rerun()

if __name__ == "__main__":
    main()