import json
import datetime

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from dateutil.relativedelta import relativedelta

def clubs_create_json():

    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1400,1500")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")

    data = {}
    hrefs = {}

    url = "https://cyberion.ua/contacts"

    driverCityClub = webdriver.Chrome(options=options)

    driverCityClub.get(url)

    city_list = driverCityClub.find_elements(By.CLASS_NAME, "components_club_city__Gqzr_")

    for city in city_list:
        city_name = city.find_element(By.TAG_NAME, 'h2').text
        data[city_name] = []
        hrefs[city_name] = []
        cards = city.find_elements(By.CLASS_NAME, "components_item__3sGY5")

        for card in cards:
            links = card.find_elements(By.TAG_NAME, 'a')
       
            if len(links) == 2:
                location = card.find_element(By.TAG_NAME, "h4")
            
                link = links[0].get_attribute("href")
                social = links[1].get_attribute("href")

                hrefs[city_name].append(link)

                data[city_name].append({
                    "url_club": link,
                    "title": "",
                    "location": location.text,
                    "social": social
                    })
            
                
            elif len(links) == 0 and len(data[city_name]) == 0:
                data[city_name].append({
                    "url_club": "",
                    "title": "",
                    "image": "https://api.cyberion.com.ua/files/1742210261121.webp",
                    "location": city_name,
                    "social": ""
                    })

    for href in hrefs:
        i=0
        for link in hrefs[href]:
            driverCityClub.get(link)

            try:
                title = driverCityClub.find_element(By.CLASS_NAME, "component_left__8x1nS").find_element(By.TAG_NAME, "h1").text
                data[href][i]["title"] = title
                i += 1
            except:
                print("Заголовок не знайдено.")

    with open("clubs.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    driverCityClub.quit()

def news_create_json():

    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1400,1500")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")

    data = []

    url = "https://cyberion.ua/news"

    driverNews = webdriver.Chrome(options=options)

    driverNews.get(url)

    today = datetime.date.today()
    format_today_months = f"{today.month}.{today.year}"

    past = today - relativedelta(months=1)
    format_past_months = f"{past.month}.{past.year}"


    news_list = driverNews.find_elements(By.CLASS_NAME, "component_main__4z2vV")

    for news in news_list:

        title = news.find_element(By.CLASS_NAME, "body-text").text
        date = news.find_element(By.CLASS_NAME, "component_date__zGdfb").text

        date_obj = datetime.datetime.strptime(date, "%d.%m.%Y")

        fomat_date_news = f"{date_obj.month}.{date_obj.year}"

        if fomat_date_news == format_today_months or fomat_date_news == format_past_months:

            ActionChains(driverNews) \
                .click(news) \
                .perform()
    
            close = driverNews.find_element(By.CLASS_NAME, "component_main__fWdme").find_element(By.CLASS_NAME, "component_modal_btn__7Ifu1")

            data.append({
                "url": driverNews.current_url,
                "title": title,
                "date": date   
            })

            ActionChains(driverNews) \
                .click(close) \
                .perform()

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    driverNews.quit()

def tournaments_create_json():

    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1400,1500")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")

    data = []

    url = "https://cyberion.ua/kololeague"

    driverTournaments = webdriver.Chrome(options=options)

    driverTournaments.get(url)

    components_body = driverTournaments.find_elements(By.CLASS_NAME, "component_body_head_item__jXUM3")

    for item in components_body:

        title = item.find_element(By.TAG_NAME, "h2").text

        ActionChains(driverTournaments) \
                .click(item) \
                .perform()
    
        parameters = driverTournaments.find_element(By.CLASS_NAME, "component_main__XUSK5").find_elements(By.TAG_NAME, "h4")

        if len(parameters) != 0:

            data.append({
                "title": title,
                "parameters": f'🏆 <b>Призовий пул:</b>\n🥇 {parameters[4].text}\n🥈 {parameters[5].text}\n🥉 {parameters[6].text}\n\n🎟️ <b>Вступний внесок:</b> <i>{parameters[7].text}</i>\n\n🎁 <b>Призи від:</b> <u>{parameters[8].text}</u>'
            })

    with open("tournaments.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    driverTournaments.quit()