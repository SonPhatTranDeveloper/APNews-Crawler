import os
import pprint

from dotenv import load_dotenv

from src.crawler import crawl_ap_article
from src.news import get_headlines_by_source
from src.model import CrawledNews
from src.llm import analyze_article_content



def main():
    load_dotenv()
    news_api_key = os.getenv("NEWS_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Get the news
    # news = get_headlines_by_source(news_api_key, "associated-press")

    # Get the first news
    # first_news = crawl_ap_article(news[1])
    first_news = CrawledNews(None, "A new wave of torrential rains and flash flooding struck the South and Midwest of the United States on Saturday, worsening conditions in areas already devastated by days of severe storms and deadly tornadoes. Forecasters warned that rivers would continue to rise for days, with widespread flooding expected in multiple states including Arkansas, Kentucky, Missouri, and Tennessee. At least 16 people have died due to the extreme weather, including 10 in Tennessee alone. Among the victims were a 9-year-old boy in Kentucky, a 74-year-old found in a submerged car, and a 5-year-old in Arkansas. Infrastructure damage is widespread, and shipping disruptions are likely due to the flooding in key logistics hubs like Louisville and Memphis. Louisville officials reported the Ohio River rising five feet in 24 hours, calling it one of the top ten flooding events in the city’s history. States have issued flash flood emergencies and tornado warnings, with some areas seeing over a foot of rainfall. The National Weather Service cited a combination of warm temperatures, wind shear, and Gulf moisture as drivers of the storms. Emergency responders have carried out multiple rescues, including evacuating the entire town of Falmouth, Kentucky, which faces flooding reminiscent of a catastrophic 1997 event. In Arkansas, a washed-out railroad bridge caused a train derailment, though no injuries were reported. In Dyersburg, Tennessee, residents sought shelter from tornado threats, bringing essential items in case their homes were destroyed. Officials continue to warn residents to avoid unnecessary travel as recovery efforts are underway.")

    # Extract the content from the first news
    first_news = analyze_article_content(openai_api_key, first_news)
    pprint.pprint(first_news)
    


if __name__ == "__main__":
    main()
