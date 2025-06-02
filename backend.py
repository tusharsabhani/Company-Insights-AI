import os
import time
import requests
from dotenv import load_dotenv
from firecrawl import AsyncFirecrawlApp, ScrapeOptions
from constants import financials_prompt, desc_prompt, funding_prompt, news_prompt

load_dotenv()
BRAND_FETCH_TOKEN = os.getenv("BRAND_FETCH_TOKEN")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
app = AsyncFirecrawlApp(api_key=FIRECRAWL_API_KEY)

async def get_company_name(domain):
    try:
        url = f"https://api.brandfetch.io/v2/brands/{domain}"
        headers = {"Authorization": f"Bearer {BRAND_FETCH_TOKEN}"}
        
        response = requests.get(url, headers=headers) 
        return response.json()
    except Exception as e:
        print(f"Exception in get_company_name - {e}")
        return None
    

async def analyse_company(company_name, display_fn=print):
    try:
        urls = {key: [] for key in ["financials", "description", "funding", "news"]}
        crawled_data = {key: [] for key in ["financials", "description", "funding", "news"]}
        prompts = {
            "financials": financials_prompt,
            "description": desc_prompt,
            "funding": funding_prompt,
            "news": news_prompt
        }

        for category, prompt in prompts.items():
            response = await app.search(query=f"Company: {company_name}\n\n{prompt}", limit=2)
            urls[category] = [item["url"] for item in response["data"]]
            print(f"Fetched {category} URLs")

            display_fn(f"🕷️ Crawling content for {category.capitalize()}...")
            crawled_data_array = []
            for link in urls[category]:
                response = await app.crawl_url(
                    url=link,
                    limit=1,
                    scrape_options=ScrapeOptions(
                        formats=["markdown"],
                        onlyMainContent=True
                    )
                )
                crawled_data_array.append(response)
            crawled_data[f"{category}_data"] = crawled_data_array
            display_fn(f"✅ Finished crawling {category.capitalize()}")
            time.sleep(60)  # Adding a delay to avoid hitting rate limits
        return crawled_data
    except Exception as e:
        display_fn(f"❌ Exception in analyse_company - {e}")
        return None