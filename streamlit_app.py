import streamlit as st

def main():
    st.set_page_config(page_title="Company Insights AI", layout="wide")
    st.title("🔍 Company Insights AI")
    st.write("Enter a company name or URL to get started.")

    # Input field for company name or URL
    company_input = st.text_input("Company Name or URL", placeholder="e.g., openai.com or OpenAI")

    if company_input:
        st.info(f"Fetching data for: {company_input}")
        st.write("🔄 Processing...")

if __name__ == "__main__":
    main()
