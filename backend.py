import os
import json
import time
import asyncio
import requests
from dotenv import load_dotenv
from meta_ai_api import MetaAI
from openai import AsyncAzureOpenAI
from firecrawl import AsyncFirecrawlApp, ScrapeOptions
from constants import financials_prompt, desc_prompt, funding_prompt, news_prompt

ai = MetaAI()
load_dotenv()
BRAND_FETCH_TOKEN = os.getenv("BRAND_FETCH_TOKEN")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_VERSION= os.getenv('AZURE_OPENAI_API_VERSION')
AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT')

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
		app = AsyncFirecrawlApp(api_key=FIRECRAWL_API_KEY)
		urls = {key: [] for key in ["financials", "description", "funding", "news"]}
		crawled_data = {key: [] for key in ["financials_data", "description_data", "funding_data", "news_data"]}
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
				time.sleep(60)
			crawled_data[f"{category}_data"] = crawled_data_array
			display_fn(f"✅ Finished crawling {category.capitalize()}")
			time.sleep(60)  # Adding a delay to avoid hitting rate limits

		# crawled_data['financials_data'][0].data[0].markdown
		
		for key in crawled_data.keys():
			pages = []
			if len(crawled_data[key]) > 0:
				for crawled_page in crawled_data[key]:
					pages.append(crawled_page.data[0].markdown)
			crawled_data[key] = pages

		summary_data = await analyse_openai(crawled_data)
		return summary_data
	except Exception as e:
		display_fn(f"❌ Exception in analyse_company - {e}")
		return None
	

async def analyse_openai(crawled_data):
	try:
		client = AsyncAzureOpenAI(
			api_key=AZURE_OPENAI_API_KEY,
			azure_endpoint=AZURE_OPENAI_ENDPOINT,
			api_version=AZURE_OPENAI_API_VERSION,
			azure_deployment=AZURE_OPENAI_DEPLOYMENT,
			max_retries=2,
			timeout=900
		)

		system_message = (
			"You are a structured data summarization assistant. "
			"Generate a concise summary paragraph that highlights key insights or trends "
			"from the provided input. Use clear, natural language suitable for the given category."
		)

		async def call_openai(category, data):
			prompt = f'''Here is the input for analysis:
				{category}: {data}

				Task:
				- Iterate through the list above.
				- Write a concise summary paragraph capturing the key insights or trends.
				- Use clear, natural language appropriate for the "{category}" category.
				- Output only the summary text. No JSON, no headers.'''
			
			response = await client.chat.completions.create(
				model="gpt-4o",
				response_format={"type": "text"},
				seed=33,
				temperature=0.1,
				timeout=900,
				messages=[
					{"role": "system", "content": system_message},
					{"role": "user", "content": prompt}
				]
			)

			return response.choices[0].message.content.strip()

		financials_summary = await call_openai("financials", crawled_data["financials_data"])
		description_summary = await call_openai("description", crawled_data["description_data"])
		funding_summary = await call_openai("funding", crawled_data["funding_data"])
		news_summary = await call_openai("news", crawled_data["news_data"])

		return {
			"financials": financials_summary,
			"description": description_summary,
			"funding": funding_summary,
			"news": news_summary
		}

	except Exception as e:
		print(f"Exception in analyse_openai - {e}")
		return None



if __name__ == "__main__":
	asyncio.run(analyse_company(""))
