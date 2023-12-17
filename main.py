import logging as log, urllib.request
from bs4 import BeautifulSoup
from kivy.app import App

from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


def scrape_page(url, maxPrice):
    log.info('scraping ebay page')

    log.info("getting page")
    try:
        page = urllib.request.urlopen(url)
    except:
        log.error('url is invalid')

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
        time = " "
        if not type :
            type = l.find("span", attrs={"class":"s-item__purchase-options s-item__purchaseOptions"}).text
        else:
            type = type.text
            timeHead = l.find("span", attrs={"class":"s-item__time"})
            time = l.find("span", attrs={"class":"s-item__time-left"}).text

                
        formattedPrice = ""
        for c in price:
            if c == "£" or c == "$" or c == "€" or c==" ":
                continue
            formattedPrice = formattedPrice + c
        try:
            if float(formattedPrice) >= maxPrice: # finding the most wanted listings
                continue 
        except:
            continue

        imgHeader = l.find("img")
        img_src = imgHeader['src']              

        # getting only the most wanted listings in a dictionary
        listing = {"id":id,
                    "name":name,
                    "price":price,
                    "type":type,
                    "url":item_url,
                    "img": img_src,
                    "time":time}
        goodListings.append(listing) # adding wanted listings to the main list


    log.info('scraped ebay page successfully')
    return 1, goodListings

class ScrapeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scraped = False
        Clock.schedule_interval(self.update, 120)


    def scrape_page_btn(self):
        print('scrape page button pressed')
        url = self.ids.scrape_url.text
        maxPrice = float(self.ids.max_listing_price.text)

        self.url = url
        self.maxPrice = maxPrice

        scrapeResult, listings = scrape_page(url, maxPrice)

        if scrapeResult == 1:
            resultScrn = self.manager.get_screen('resultScrn')
            resultScrn.get_listings(listings)
            self.manager.current = 'resultScrn'
            self.scraped = True
        else: 
            log.info('scrape result returned 0') 

    def update(self, dt): 
        print("updating")
        if self.scraped == True:
            print("scraping")
            scrapeResult, listings = scrape_page(self.url, self.maxPrice)

            if scrapeResult == 1:
                resultScrn = self.manager.get_screen('resultScrn')
                resultScrn.get_listings(listings)
            else: 
                log.info('scrape result returned 0')

class ResultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_listings(self, listings):
        log.info('getting listings')
        self.listings = None
        self.listings = listings
        self.show_listings()

    def show_listings(self):
        log.info('showing listings')
        self.lsgrid.clear_widgets()
        self.grid.clear_widgets()
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
        print(l)
        
        nameLbl = Label(text=l['name'], font_size='18sp', pos_hint = {'x':.5, 'y':.9},size_hint=(.1, .1))
        typeLbl = Label(text =l['type'] + "   " + str(l['price']) + "   " + l['time'], pos_hint = {'x':.5, 'y':.75},size_hint=(.1, .1))
        urlLbl = TextInput(text=l['url'], readonly=True,pos_hint = {'x':0, 'y':.2}, size_hint=(.4, .5))
        img = AsyncImage(source=l['img'],pos_hint = {'x':.5, 'y':.2},size_hint=(.4, .5))
        
        backBtn = Button(text='BACK', size_hint=(1, .2))
        backBtn.bind(on_press=self.backBtn_callback)


        self.lsgrid.add_widget(nameLbl)
        self.lsgrid.add_widget(img)
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
    
    
    Config.set('graphics', 'width', '1024')
    Config.set('graphics', 'height', '768')
    Config.write()
    
if __name__ == "__main__":
    ScraperApp().run()