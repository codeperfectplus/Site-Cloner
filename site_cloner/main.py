""""
    Program name : Website cloner
    author : https://github.com/codeperfectplus
    How to use : Check README.md
 """

import os
import re
import logging
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
logging.basicConfig(filename='image_scraper.log', 
                    level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class SiteCloner(object):
    def __init__(self, website_name):
        self.website_name = website_name
        self.site_without_protocol = self.website_name.split('//')[1]
        self.folder_name = self.website_name.split('//')[1].split('/')[0].split('.')[0]
        self.image_out_dir = os.path.join(self.folder_name, 'images')
        os.makedirs(self.folder_name, exist_ok=True)
        os.makedirs(self.image_out_dir, exist_ok=True)

    def crawl_website(self, url, parse=True):
        """ This function will crawl website and return content"""
        data = ""
        response = requests.get(url)
        if response.status_code == 200:
            if parse:
                data = BeautifulSoup(response.text, 'html.parser')
            else:
                data = response
        return data

    def save_website(self, filename, content):
        """ This function will save website to respective folder """
        with open(os.path.join(self.folder_name, filename), "w", encoding="ascii", errors="ignore") as fp:
            fp.write(content.text)

    def scrap_page_links(self, data):
        """ get the links of all the pages """
        page_links = set()
        other_links = set()
        links_tags = data.find_all('a')
        for idx, link_elem in enumerate(links_tags):
            link = link_elem.get('href')
            if link is not None:
                if link.startswith('/'):
                    link = self.website_name + link
                    page_links.add(link)
                
                elif re.search(self.site_without_protocol, link):
                    page_links.add(link)
                else:
                    other_links.add(link)
        return page_links, other_links

    def get_image_links(self, data):
        ''' gets the links of the images '''
        images_links = set()
        images_tags = data.find_all('img')
        for idx, image_ele in enumerate(images_tags):
            img_link = image_ele.get('src')
            if img_link is not None:
                images_links.add(img_link)
        return images_links
        
    def scrap_webpage(self, page_links):
        """ This function will scrap the webpage """
        index_page = self.crawl_website(self.website_name, parse=False)
        self.save_website("index.html", index_page)
        
        for page_link in page_links:
            logging.debug(f"Scraping {page_link}")
            page_name = page_link.split('/')[-1] + '.html'
            page_data = self.crawl_website(page_link, parse=False)
            if page_data:
                self.save_website(page_name, page_data)
    
    def scrap_images(self, image_links):
        ''' downloads the images in the website folder'''
        for idx, image_link in enumerate(tqdm(image_links)):
            response = requests.get(image_link)
            if response.status_code == 200:
                image_name = image_link.split('/')[-1] + ".jpg"
                with open(os.path.join(self.image_out_dir, str(image_name)), 'wb') as fp:
                    fp.write(response.content)
            else:
                print(f"Error downloading {image_link}")
    
    def clone_website(self):
        """ This function will clone the website """
        index_page = self.crawl_website(self.website_name)
        page_links, other_links = self.scrap_page_links(index_page)
        image_links = self.get_image_links(index_page)
        self.scrap_webpage(page_links)
        self.scrap_images(image_links)
        print("Website cloned successfully")

    
