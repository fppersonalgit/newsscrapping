import asyncio
from datetime import datetime, timezone
import time
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from tqdm import tqdm
import logging

async def scrap_website(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    with tqdm(desc="BBC News scraping", unit="page") as progress:
        async with aiohttp.ClientSession() as session:
            titles_list = []
            dates_list1 = []
            html = await scrap_website(session, 'https://www.bbc.com/news/science-environment-56837908')
            soup = BeautifulSoup(html, 'html.parser')
            titles = soup.findAll('a', {'class': 'gs-c-promo-heading gs-o-faux-block-link__overlay-link gel-pica-bold nw-o-link-split__anchor'})[0:5]
            dates = soup.findAll('time', {'class': 'gs-o-bullet__text date qa-status-date'})[0:5]
            for date in dates:
                datetime_value = date['datetime']
                date_obj = datetime.fromisoformat(datetime_value.replace('Z', '+00:00'))
                dates_list1.append(date_obj)
            for title in titles:
                titles_list.append(title.text)
            bbc_news = [{'title': title, 'datetime': date_value} for title, date_value in zip(titles_list, dates_list1)]
            print(bbc_news)
            progress.update()
    with tqdm(desc="CNN scraping", unit="page") as progress:
        async with aiohttp.ClientSession() as session:
            titles_list = []
            dates_list = []
            html = await scrap_website(session, 'https://edition.cnn.com/world/cnn-climate')
            soup = BeautifulSoup(html, 'html.parser')
            titles_cnn = soup.findAll('div', {'class': 'container__headline container_list-headlines-with-images__headline'})
            dates_cnn = soup.findAll('div', {'class': 'container__date container_list-headlines-with-images__date inline-placeholder'})
            for date in dates_cnn:
                date_middle = str(date.text.strip())
                dt = datetime.strptime(date_middle, '%b %d, %Y')
                dt_utc = dt.replace(tzinfo=timezone.utc)
                dates_list.append(dt_utc)
            for title in titles_cnn:
                titles_list.append(title.text.strip())
            cnn_news = [{'title': title_cnn, 'datetime': date_cnn} for title_cnn, date_cnn in zip(titles_list, dates_list)]
            print(cnn_news)
            progress.update()
    return html

loop = asyncio.get_event_loop()
loop.run_until_complete(main())