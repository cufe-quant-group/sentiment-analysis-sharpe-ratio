"""
Works for CNBC Oil Markets Sentiment Analysis.

Currently only runs on articles, but can be extended to video captions later on.

"""

from bs4 import BeautifulSoup
import urllib
import re
from textblob import TextBlob
import datetime
from pandas_datareader import data as web
import math
from finviz import Screener

def sentiment(industry):
    if industry not in "internet, oil, social-media, mobile, enterprise, cybersecurity, technology, venture-capital, defense, finance, banks, hedge-funds, deals-and-ipos, wall-street, real-estate, commercial-real-estate, construction, housing, mortgages, reits, biotech-and-pharmaceuticals, life-and-health-insurance, media, advertising, broadcasting, cable-tv, publishing, radio, transportation, airlines, transportation-infrastructure, road-and-rail, autos, outer-space, industrials, aerospace-defense, machinery, manufacturing, materials, retail, apparel, discounters, department-stores, e-commerce, food-and-beverage, restaurants, household-products, luxury":
        print("The industry you have chosen is not on CNBC")
        return

    print("Generating industry rating for " + industry + " markets based on CNBC sentiment analysis...")
    
    industry_rating = 0;
    
    pages = []
    html_page = urllib.request.urlopen("https://www.cnbc.com/" + industry + "/")
    soup = BeautifulSoup(html_page, 'html.parser')
    for link in soup.find_all('a', attrs={'href': re.compile("https://www.cnbc.com/2020/")}):
        url = link.get('href')
        if url not in pages:
            pages.append(url)
    
    print("Performing analysis on the following articles: (" + str(len(pages)) + " total)")
    print(pages)
    
    
    paragraph_count = 0 #Counts total number of paragraphs for normalization
    
    for page in pages:
        visit_page = urllib.request.urlopen(page)
        new_soup = BeautifulSoup(visit_page, 'html.parser')
        paras = new_soup.select("div[id=root] > div[class=App-containerClick] > div[id=BrandPageWrapper] > div[id=MainContent] > div> div.Regular.Article.PageBuilder-page > div.PageBuilder-pageWrapper > div.PageBuilder-pageRow.PageBuilder-containerFluidWidths > div.PageBuilder-col-9.PageBuilder-col.PageBuilder-article > div.ArticleBody-articleBody > div.group > p")
        for paragraph in paras:
            paragraph_count += 1
            
            paragraph_string = str(paragraph.text)
            
            blob = TextBlob(paragraph_string)
            paraScore = blob.sentiment.polarity*blob.sentiment.subjectivity
            """
            if paraScore < 0:
                industry_rating += 5*paraScore
            else:
                industry_rating += paraScore
            """
            industry_rating += paraScore
    industry_rating = industry_rating / paragraph_count

    print("Final rating for the " + industry + " industry: " + str(industry_rating))

    return industry_rating

def sharpe(name,starttime,endtime):
    if(starttime == None):
        start = datetime.datetime(2019,1,1)
    if(endtime == None):
        end = datetime.datetime(2020,2,1)
    start = datetime.datetime(starttime[0],starttime[1],starttime[2])
    end = datetime.datetime(endtime[0],endtime[1],endtime[2])
    df = web.DataReader(name,'yahoo',start,end)
    df_T = web.DataReader('^TNX','yahoo',start,end)

    price_list = df['Open'] #Use the Open Price of each Stock
    price_list_T = df_T['Open']

    mean_price = int(df['Open'].mean())
    sum = 0
    for price in price_list:
        sum = (price-mean_price)**2+sum
    var = sum/len(price_list)
    std = math.sqrt(var)

    ret = ((price_list[len(price_list)-1]- price_list[0])/price_list[0])/((end-start).days)*365 #Normalize to annual return
    ret_T = (price_list_T[len(price_list_T)-1]- price_list_T[0])/price_list_T[0]/((end-start).days)*365
    #print('the price of the T-Bill changes from ' + str(price_list_T[0]) + ' to ' + str(price_list_T[len(price_list_T)-1]))
    #print('the price of the stock changes from ' + str(price_list[0]) + ' to ' + str(price_list[len(price_list)-1]))
    #print ('return of the stock is: ' + str(ret))
    #print ('return of T-Bond is: ' + str(ret_T))

    sharpe = round((ret-ret_T)/std*100,2) #Calculate the Sharpe Ratio and make it a percentage
    print('Sharpe Ratio of ' + name + ' in the current month:' + str(sharpe) + '%')
    return sharpe


#Possible areas of interest: internet, oil, social-media, mobile, enterprise, cybersecurity, technology, venture-capital, defense, finance, banks, hedge-funds, deals-and-ipos, wall-street, real-estate, commercial-real-estate, construction, housing, mortgages, reits, biotech-and-pharmaceuticals, life-and-health-insurance, media, advertising, broadcasting, cable-tv, publishing, radio, transportation, airlines, transportation-infrastructure, road-and-rail, autos, outer-space, industrials, aerospace-defense, machinery, manufacturing, materials, retail, apparel, discounters, department-stores, e-commerce, food-and-beverage, restaurants, household-products, luxury
print("Available options are: internet, oil, social-media, "
      "mobile, enterprise, cybersecurity, technology, venture-capital, "
      "defense, finance, banks, hedge-funds, deals-and-ipos, wall-street, "
      "real-estate, commercial-real-estate, construction, housing, "
      "mortgages, reits, biotech-and-pharmaceuticals, life-and-health-insurance, "
      "media, advertising, broadcasting, cable-tv, publishing, radio, transportation, "
      "airlines, transportation-infrastructure, road-and-rail, autos, outer-space, "
      "industrials, aerospace-defense, machinery, manufacturing, materials, retail, "
      "apparel, discounters, department-stores, e-commerce, food-and-beverage, restaurants, "
      "household-products, luxury")
chosen_industry = input("Enter an industry of interest: ")
sentiment(chosen_industry.lower())

my_filter = ['fa_div_high']
stock_list = Screener(filters=my_filter,order='Industry',custom=['1','3','4'])


sharpe_dic = {}
x = ""
i = 0
while i < stock_list.__len__():
    s1 = stock_list.get(i)["Sector"]
    s2 = stock_list.get(i)["Industry"]
    if chosen_industry in s1 or chosen_industry in s2:
        x = stock_list.get(i)["Ticker"]
        x_sh = sharpe(x, (2020,1,1), (2020, 2,1))
        sharpe_dic[x] = x_sh
    i = i + 1

sort_sharpe_dic = sorted(sharpe_dic.items(), key=lambda x: x[1], reverse=True)
print(sort_sharpe_dic)
print( sort_sharpe_dic[0][0] + " has the highest sharpe ratio among all high-dividend stocks in "
       + chosen_industry + ": (" + str(len(sort_sharpe_dic))  + " total)")
