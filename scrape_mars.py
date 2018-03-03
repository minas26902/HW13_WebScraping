# ## HW#13 Web Scraping and Document Databases
# ## Mission to Mars

#Import dependencies
from bs4 import BeautifulSoup
from splinter import Browser
import pandas as pd
import requests
import time
import re
import pymongo

def init_brower():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'} 
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser = init_brower()
    #create scraped_mars_data dictionary that we can insert into mongo
    scraped_mars_data = {}

    ###NASA MARS NEWS
    mars_news = 'https://mars.nasa.gov/news/'
    browser.visit(mars_news)
    time.sleep(2)
    html=browser.html

    #Create a BeautifulSoup object and parse html
    News_soup = BeautifulSoup(html, 'html.parser')
    #Extract latest news title and paragraph
    news_title= News_soup.find('div', class_='content_title').get_text()
    news_paragraph=News_soup.find('div', class_='rollover_description_inner').get_text()
    time.sleep(2)

    #Add news_title and news_paragraph to dictionary
    scraped_mars_data["news1"] = news_title
    scraped_mars_data["news2"]= news_paragraph

    ### JPL MARS SPACE IMAGE
    JPL_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(JPL_url)

    #Click through the pages to reach the link containing the high res jpg image
    time.sleep(2)
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(2)
    browser.click_link_by_partial_text('more info')
    time.sleep(2)
    browser.click_link_by_partial_text('.jpg')

    #Retrieve image url
    html=browser.html
    JPL_soup=BeautifulSoup(html,'html.parser')
    featured_image_url=JPL_soup.find('img').get('src')
    
    #Add image to the dictionary
    scraped_mars_data["image"] = featured_image_url

    ### MARS WEATHER
    weather_url='https://twitter.com/marswxreport?lang=en'
    html=requests.get(weather_url)
    weather_soup = BeautifulSoup(html.text, 'html.parser')
    mars_weather=weather_soup.find_all(string=re.compile("Sol"), class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")[0].text
    
    #Add weather to the dictionary
    scraped_mars_data["weather"] = mars_weather

    ### MARS PLANET PROFILE TABLE
    facts_url='https://space-facts.com/mars/'
    table=pd.read_html(facts_url)
    table_df=table[0]
    table_df=table_df.rename(columns={0:'Mars Planet Profile', 1: ''})
    table_df.set_index('Mars Planet Profile', inplace=True)
    table_df

    #Convert table to html table 
    table_df.to_html('facts_table.html')

    # #facts_table.html.replace('/n',"")
    # #Strip items from html table
    # soup=BeautifulSoup(open('table_html'), 'html.parser')
    # table_description=[]
    # table_values={}
    # for item in soup.table('tr'):
    #     #print(item.text)
    #     table_description.append(item.text.strip(':'))
    # table_values=dict([(k,v) for k,v in zip (table_description[::2], table_description[1::2])])
    # #print (table_values)

    #  #Add table to dictionary
    # scraped_mars_data["table"] = table_values

    ### MARS HEMISPHERES IMAGES FROM USGS ASTROGEOLOGY SITE
    hemisphere_url='https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemisphere_url)
    html=browser.html
    hemisphere_soup = BeautifulSoup(html, 'html.parser')

    #Create a dictionary containing hemisphere titles and images urls
    hemisphere_image_urls=[]
    hemisphere_dict={'title':[], 'img_url':[]}
    x=hemisphere_soup.find_all('h3')

    for i in x:
        y=i.get_text()
        title=y.strip('Enhanced')
        browser.click_link_by_partial_text(y)
        url=browser.find_link_by_partial_href('download')['href']
        hemisphere_dict={'title':title, 'img_url':url}
        hemisphere_image_urls.append(hemisphere_dict)
        browser.visit(hemisphere_url)
    #print(hemisphere_image_urls)

    #Add hemisphere images to dictionary
    scraped_mars_data["hemispheres"] = hemisphere_image_urls

    return scraped_mars_data

