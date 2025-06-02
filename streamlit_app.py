import asyncio
import streamlit as st
from urllib.parse import urlparse
from backend import get_company_name, analyse_company

def is_url(input_str):
    return "." in input_str and not " " in input_str

def extract_domain(url):
    parsed_url = urlparse(url if url.startswith("http") else "http://" + url)
    return parsed_url.netloc

def get_logo_url(logo_data):
    if not logo_data:
        return None
    try:
        return logo_data[0]["formats"][0]["src"]
    except (KeyError, IndexError, TypeError):
        return None

async def main():
    st.set_page_config(page_title="Company Insights AI", layout="wide")
    st.title("🔍 Company Insights AI")
    st.write("Enter a company name or URL to get started.")

    company_input = st.text_input("Company Name or URL", placeholder="e.g., openai.com or OpenAI")

    company_name = None
    logo_url = None

    if company_input:
        st.write(f"🔄 Processing... Fetching data for: {company_input}")

        if is_url(company_input):
            domain = extract_domain(company_input)
            st.write(f"🔗 Detected URL. Extracted domain: **{domain}**")
            company_info = await get_company_name(domain)
            if isinstance(company_info, dict):
                company_name = company_info.get("name", domain)
                logo_url = get_logo_url(company_info.get("logos", []))
            else:
                company_name = company_info  # fallback if only name returned
        else:
            company_name = company_input

    if company_name:
        st.subheader("🏢 Company Profile")
        st.markdown(f"Name - {company_name}")
        col1, _ = st.columns([1, 4])
        with col1:
            if logo_url:
                st.image(logo_url, use_container_width=True)
            else:
                st.write("📄 No logo available")

        # Analyse
        st.subheader("📊 Analysing Company...")
        result = await analyse_company(company_name, display_fn=st.write)

        if result:
            st.success("✅ Analysis complete.")
        else:
            st.error("⚠️ Failed to analyse company.")

if __name__ == "__main__":
    asyncio.run(main())
