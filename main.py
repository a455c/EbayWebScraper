import logging as log
import urllib.request
from bs4 import BeautifulSoup
from kivy.app import App

from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

LISTING_PRICE = 100

# gets wanted url to scrape
url = "https://www.ebay.com/sch/i.html?_nkw=xbox+one&LH_Complete=1"

def scrape_page(url, maxPrice):
    log.info('scraping ebay page')
    try:
        page = urllib.request.urlopen(url)
    except:
        log.error('url is invalid')
        return 0, None
    
    print(page)

    s = BeautifulSoup(page, "html.parser")#turns the string from page into readable html

    #print(s.encode('utf-8'))

    listingsHead = s.find("ul", attrs={"class":"srp-results srp-list clearfix"})#finding the head list of listings in html

    #print(listingsHead.encode('utf-8'))

    listings = listingsHead.find_all("li", attrs={"class":"s-item s-item__pl-on-bottom"})#find all the individual listings in the listing head

    goodListings = [] # making a list for the listings we want to look out for 

    print(listings[0].encode('utf-8'))

    for l in listings: # scraping through each listing 
        try:
            id = l['id'] # getting id of the listing
        except:
            continue
        price = l.find("span", attrs={"class":"s-item__price"}).text #finding price through <span> type of html
        name = l.find("div", attrs={"class":"s-item__title"}).text #finding name through <span> type of html

        item_link = l.find("a", attrs={"class":"s-item__link"})
        item_url = item_link["href"]

        type = l.find("span", attrs={"class":"s-item__bids s-item__bidCount"})
        if not type :
            type = l.find("span", attrs={"class":"s-item__purchase-options s-item__purchaseOptions"}).text
        else:
            type = type.text

                
        formattedPrice = ""
        for c in price:
            if c == "£" or c == "$" or c == "€":
                continue
            formattedPrice = formattedPrice + c
        if float(formattedPrice) >= maxPrice: # finding the most wanted listings
            continue                                    

        # getting only the most wanted listings in a dictionary
        listing = {"id":id,
                    "name":name,
                    "price":price,
                    "type":type,
                    "url":item_url}
        goodListings.append(listing) # adding wanted listings to the main list


    log.info('scraped ebay page successfully')
    return 1, goodListings

class ScrapeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def scrape_page_btn(self):
        print('scrape page button pressed')
        self.ids.text = 'https://www.ebay.co.uk/sch/i.html?_from=R40&_trksid=p4432023.m570.l1313&_nkw=xbox+one&_sacat=0'
        url = self.ids.scrape_url.text
        maxPrice = self.ids.max_listing_price.text
        
        scrapeResult, listings = scrape_page(url, float(maxPrice))

        if scrapeResult == 1:
            resultScrn = self.manager.get_screen('resultScrn')
            resultScrn.get_listings(listings)
            self.manager.current = 'resultScrn'
        else: 
            log.info('scrape result returned 0')

class ResultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_listings(self, listings):
        log.info('getting listings')
        self.listings = listings
        self.show_listings()

    def show_listings(self):
        log.info('showing listings')
        self.lsgrid.clear_widgets()
        for i in range(0, len(self.listings)): 
            btn = Button(
                text=self.listings[i]['id'], 
                size_hint_x=None, 
                width=130,
                )
            btn.bind(on_release = self.get_individual_listing)
            btn.my_id = self.listings[i]['id']

            self.grid.add_widget(btn)

    def get_individual_listing(self, instance):
        log.info('getting individual listings')
        id = instance.my_id
        l = None
        for i in range(0, len(self.listings)):
            if not self.listings[i]['id'] == id:
                continue
            l = self.listings[i]
        self.show_individual_listing(l)

    def show_individual_listing(self, listing):
        log.info('showing individual listings')
        self.grid.clear_widgets()

        l = listing
        lt = []
        print(l)
        
        nameLbl = Label(text=l['name'], font_size='18sp', pos_hint = {'x':.5, 'y':.1})
        priceLbl = Label(text=str(l['price']))
        typeLbl = Label(text =l['type'])
        urlLbl = TextInput(text=l['url'], readonly=True, size_hint=(.3, 1))
        
        backBtn = Button(text='BACK', pos_hint={'x':None, 'y':None}, pos = (500, 100))
        backBtn.bind(on_press=self.backBtn_callback)
        
        self.lsgrid.add_widget(nameLbl)
        self.lsgrid.add_widget(priceLbl)
        self.lsgrid.add_widget(typeLbl)
        self.lsgrid.add_widget(urlLbl)
        self.lsgrid.add_widget(backBtn)

    def backBtn_callback(self, instance):
        self.show_listings()

class ScraperApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ScrapeScreen(name='scrapeScrn'))
        sm.add_widget(ResultScreen(name='resultScrn'))
        return sm
    
if __name__ == "__main__":
    ScraperApp().run()