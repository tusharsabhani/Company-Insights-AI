financials_prompt = (
    "Search trusted sources such as Yahoo Finance, Crunchbase, or company investor relations pages. "
    "Extract the most recent financial performance of the company, including revenue, profit or loss, "
    "and any available growth metrics (e.g., year-over-year growth, EBITDA, net income, etc.)."
)

desc_prompt = (
    "Search the web and summarize what this company does. "
    "Give a concise description suitable for a user unfamiliar with the brand."
)

funding_prompt = (
    "Search for the company’s funding history. Provide a list of funding rounds including round type, date, amount raised, and key investors."
)

news_prompt = (
    "List notable news articles about the company from the last 30 days. "
    "For each article, give the title, publish date, and URL."
)