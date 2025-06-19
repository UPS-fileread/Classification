import streamlit as st
import os
from classify_context import classify_context
from convert_pdf import pdf_to_text

def main():
    st.title('Fileread Document Classification')
    
    # Section for user to enter OpenAI API key
    # api_key = st.text_input('Enter your OpenAI API key', type='password')
    # if api_key:
    #     os.environ['OPENAI_API_KEY'] = api_key
    # else:
    #     st.warning('Please enter your OpenAI API key to use the classifier.')
    #     return
    
    st.write('Upload one or more .txt or .pdf files to classify their legal context and subcategory.')
    
    uploaded_files = st.file_uploader(
        "Choose text or PDF files", 
        type=["txt", "pdf"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.subheader(f"📄 {uploaded_file.name}")
            filetype = uploaded_file.name.lower().split('.')[-1]
            if filetype == "pdf":
                # Convert PDF to text
                try:
                    with st.spinner('Converting PDF to text...'):
                        pdf_bytes = uploaded_file.read()
                        text_content = pdf_to_text(pdf_bytes, num_pages=5)
                except Exception as e:
                    st.error(f"Error converting PDF: {e}")
                    continue
            else:
                # Read & decode text file
                raw_bytes = uploaded_file.read()
                text_content = raw_bytes.decode('utf-8', errors='replace')

            st.text_area("Preview", text_content[:200], height=100, disabled=True)

            try:
                with st.spinner('Analyzing document...'):
                    result = classify_context(text_content)
                col1, col2 = st.columns(2)
                col1.metric(label="Category", value=result.category)
                col2.metric(label="Subcategory", value=result.subcategory)
                with st.expander("View Full Document"):
                    st.text_area("Document Text", text_content, height=300, disabled=True)
            except Exception as e:
                st.error(f"Error analyzing {uploaded_file.name}: {e}")
    else:
        st.info('👆 Please upload at least one .txt or .pdf file to analyze.')

if __name__ == "__main__":
    main()
