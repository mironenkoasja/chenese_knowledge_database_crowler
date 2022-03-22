# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 12:43:33 2018

@author: Asja
"""

import os
from __future__ import unicode_literals
import socks
import socket
import requests
import re
from lxml import etree
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException   
os.environ[str("webdriver.gecko.driver")] = str(
        'D:\\Programs\\geckodriver-v0.24.0-win64\\geckodriver.exe'
        )
from selenium.webdriver.common.proxy import *
from lxml import html
import cStringIO

path = 'path_to_directory'
os.getcwd()
os.chdir(path)

# I created FirefoxProfile for setting  proxy on configured 
profile = webdriver.FirefoxProfile("C:\\Users\\Asja\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\pdsh00m5.Default User")

# Start Firefox
driver = webdriver.Firefox(
        executable_path=r'D:\\Programs\\geckodriver-v0.24.0-win64\\geckodriver.exe',
        firefox_profile=profile
        )
driver.get("http://2ip.ru")
time.sleep(5)
# access to proxy  
alert = driver.switch_to.alert
alert.accept()

#Loading of China Knowledge Resource Integrated Database search-page
driver.get("http://oversea.cnki.net/kns55/brief/result.aspx?dbPrefix=CJFD")
time.sleep(5)

# Filling search form
driver.find_element_by_link_text('Source Search').click()
time.sleep(4)
source_search = driver.find_element_by_id('magazine_value1')
source_search.clear()
source_search.send_keys("1671-8461")
source_search.send_keys(Keys.RETURN)
time.sleep(5)
driver.switch_to_frame(driver.find_element_by_id("iframeResult"))
time.sleep(7)
driver.find_elements_by_xpath("//div[contains(@id, 'id_grid_display_num')]/a")[-1].click()


# Function scrapes links on all articles on the page and collect data about each link
first_list = []
def scrap_list_link(driver, first_list):
    for i in range(2, 52):
        #Create empty dictionary
        artic_inf = dict.fromkeys([
                'link',
                'author',
                'year_issue',
                'cites',
                'downloads'])
        # Link to the article
        l_el = driver.find_elements_by_xpath(
            "//table[contains(@class,'GridTableContent')]/tbody/tr["+str(i)+"]/td[2]/a[1]"
            )
        artic_inf['link'] = l_el[0].get_attribute('href')
        # Author
        a_el = driver.find_elements_by_xpath(
            "//table[contains(@class,'GridTableContent')]/tbody/tr["+str(i)+"]/td[3]/a"
            )
        if a_el:
            artic_inf['author'] = a_el[0].get_attribute('text')
        else:
            artic_inf['author'] =None
            
        # Journal issue
        yi_el = driver.find_elements_by_xpath(
            "//table[contains(@class,'GridTableContent')]/tbody/tr["+str(i)+"]/td[5]/a"
            )
        artic_inf['year_issue'] = yi_el[0].get_attribute('text')
        
        # Cites
        c_el = driver.find_elements_by_xpath(
            "//table[contains(@class,'GridTableContent')]/tbody/tr["+str(i)+"]/td[6]/a"
            )
        if c_el:
            
            artic_inf['cites'] = c_el[0].get_attribute('text')#Может не быть ссылок
        else:
            artic_inf['cites'] = 0
        # downloads  
        d_el = driver.find_elements_by_xpath(
            "//table[contains(@class,'GridTableContent')]/tbody/tr["+str(i)+"]/td[7]"
            )
        if d_el:
            
            artic_inf['downloads'] = d_el[0].get_attribute('text')
        else:
            artic_inf['downloads'] = 0
         
        first_list.append(artic_inf)
    
print final_list[0]


# Loop scrape all links of articles from all pages of search result
for i in range(1, 19):    
    pages = driver.find_elements_by_xpath("//td[contains(@class,'pagerCell')]/a")
    next_page = pages[-1].get_attribute('href')
    driver.get(next_page)
    time.sleep(10)        
    scrap_list_link(driver)
    
# Function writes in csv first result    
def write_in_csv(outfile, final_list):
    writer = csv.writer(outfile)
    first_row = [
            'link',
            'author',
            'year_issue',
            'cites',
            'downloads'
                ]
    writer.writerow(first_row)
    
    for item in final_list:
        row = []
        row.append(item['link'].encode('utf-8'))
        if item['author'] != None:
            row.append(item['author'].encode('utf-8'))
        else:
            row.append(item['author'])
        row.append(item['year_issue'].encode('utf-8'))
        row.append(item['cites'])
        row.append(item['downloads'])
        print row
        writer.writerow(row)
    
    return outfile
    


# Write first data 
outfile = open('first_list_articl.csv', 'w')
write_in_csv(outfile, final_list)
outfile.close()

# Function check existence of html-element
def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True  
    

# Funcrion scrape information from article page
def scrape_article_link(dict_link, dict_id):
    driver.get(dict_link)
    time.sleep(6)
    article_data = dict.fromkeys([
            'id',
            'title_ch',
            'title_en',
            'authors_ch',
            'authors_eng',
            'organizations',
            'abstract_ch',
            'abstract_en',
            'keywords_ch',
            'downloads'
            ])
    article_data['id'] = dict_id
        
    #Title on chinese
    el_title_ch = driver.find_element_by_xpath(
            "//span[contains(@id, 'chTitle')]"
            )
    article_data['title_ch'] = el_title_ch.get_attribute('text')
    
    # Title English
    if check_exists_by_xpath("//span[contains(@id, 'enTitle')]"): 
        el_title_en = driver.find_element_by_xpath(
                "//span[contains(@id, 'enTitle')]"
                )
        article_data['title_en'] = el_title_en.get_attribute('text')
    else:
        article_data['title_en'] = None
    
    # Authors chinese
    ###To Do сделать не списки, а строчки с разделителем  ;
    el_authors_ch = driver.find_elements_by_xpath(
            "//div[contains(@class, 'author')]/p[1]/a"
            ) 
    i = ''       
    for item in el_authors_ch:
        i = i + item.get_attribute('text') + ';' 
    article_data['authors_ch'] = i
    
    # Authors english
    if check_exists_by_xpath("//div[contains(@class, 'author')]/p[2]"):
        el_authors_en = driver.find_element_by_xpath(
                "//div[contains(@class, 'author')]/p[2]"
                )
        if el_authors_en.get_attribute('text') != None:
            article_data['authors_en'] = el_authors_en.get_attribute('text').split('\n')[-1]
        else:
            article_data['authors_en'] = el_authors_en.get_attribute('innerHTML').split('\n')[-1]
    else:
        article_data['authors_en'] = None
        
        
    # Organisation chinese
    if check_exists_by_xpath("//div[contains(@class, 'author')]/p[3]/a"):
        el_organizations = driver.find_elements_by_xpath(
                "//div[contains(@class, 'author')]/p[3]/a"
                )
        i = ''
        for item in el_organizations:
            i = i + item.get_attribute('text') + ';' 
        article_data['organizations'] = i
    else:
       article_data['organizations'] = None        
    
    # Abstract chinese english
    if check_exists_by_xpath("//span[contains(@id, 'ChDivSummary')]"):     
        el_abstract_ch = driver.find_elements_by_xpath(
                "//span[contains(@id, 'ChDivSummary')]"
                )
        if len(el_abstract_ch) == 2:
            article_data['abstract_ch'] = el_abstract_ch[0].get_attribute('text')
            article_data['abstract_en'] = el_abstract_ch[1].get_attribute('text')
        else:
            article_data['abstract_ch'] = el_abstract_ch[0].get_attribute('text')
            article_data['abstract_en'] = None
    else:
        article_data['abstract_ch'] = None
        article_data['abstract_en'] = None
         
    # key-words 
    if check_exists_by_xpath("//span[contains(@id, 'ChDivKeyWord')]/a"):
        el_keywords = driver.find_elements_by_xpath(
                "//span[contains(@id, 'ChDivKeyWord')]/a"
                )
        i = ''
        for item in el_keywords:
            i = i + item.get_attribute('text') + ';'
        article_data['keywords_ch'] = i
    else:
        article_data['keywords_ch'] = None
   
    # downloads
    if check_exists_by_xpath("//ul[contains(@class, 'break')]/li"):
        el_downloads = driver.find_elements_by_xpath(
                "//ul[contains(@class, 'break')]/li"
                )    
        article_data['downloads'] = int(el_downloads[-1].get_attribute('text').split('】')[-1])
    else:
        article_data['downloads'] = None
        
    return article_data
    
            
# Read first list from csv-file
ff_path = 'first_list_articl.csv'
f_dict = []  
with open(ff_path) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        f_dict.append(row)   


# Scrape information about all articles from article-page
for i in range(0, len(f_dict)):
    print f_dict[i]['id']
    test_list.append(scrape_article_link(f_dict[i]['link'], f_dict[i]['id']))
    
# Write in csv final information    
def write_in_csv_f_dict(outfile, final_list):
    writer = csv.writer(outfile)
    first_row = [
            'id',
            'title_ch',
            'title_en',
            'authors_ch',
            'authors_en',
            'organizations',
            'abstract_ch',
            'abstract_en',
            'keywords_ch',
            'downloads'
                ]
    writer.writerow(first_row)
    
    for item in final_list:
        print item['id']
        row = []
        row.append(item['id'].encode('utf-8'))
        if item['title_ch'] != None:
            row.append(item['title_ch'].encode('utf-8'))
        else:
            row.append(item['title_ch'])
        if item['title_en'] != None:
            row.append(item['title_en'].encode('utf-8'))
        else:
            row.append(item['title_en'])
        if item['authors_ch'] != None:
            row.append(item['authors_ch'].encode('utf-8'))
        else:
            row.append(item['authors_ch'])    
            
        if item['authors_en'] != None:
            row.append(item['authors_en'].encode('utf-8'))
        else:
            row.append(item['authors_en'])
        if item['organizations'] != None:
            row.append(item['organizations'].encode('utf-8'))
        else:
            row.append(item['organizations'])
        if item['abstract_ch'] != None:
            row.append(item['abstract_ch'].encode('utf-8'))
        else:
            row.append(item['abstract_ch'])
        if item['abstract_en'] != None:
            row.append(item['abstract_en'].encode('utf-8'))
        else:
            row.append(item['abstract_en'])
        if item['keywords_ch'] != None:
            row.append(item['keywords_ch'].encode('utf-8'))
        else:
            row.append(item['keywords_ch'])
        if item['downloads'] != None:
            row.append(int(item['downloads']))
        else:
            row.append(item['downloads'])    
        #print row
        writer.writerow(row)
    
    return outfile
    

    
outfile = open('ishodnik.csv', 'w')
write_in_csv_f_dict(outfile, final_list)
outfile.close()    


# Functions for automated translation abstracts and title into english
def google_translator(ch_str):
    driver.get('https://translate.google.com/#zh-CN/en')
    time.sleep(2)               
    source_text = driver.find_element_by_xpath(
            '//textarea[contains(@id, "source")]'
            )
    source_text.clear()
    source_text.send_keys(ch_str)
    source_text.send_keys(Keys.RETURN)
    time.sleep(6) 
    result = driver.find_element_by_xpath(
            '//span[contains(@id, "result_box")]/span'
            ).get_attribute('innerHTML')         
    return result
    

def add_google_translation(item):  
    if (item['title_ch'] != None) and (item['title_en'] == None):
        item['title_gtrans'] = google_translator(item['title_ch'])
    else:
        item['title_gtrans'] = None
        
    if (item['authors_ch'] != None) and (item['authors_en'] == None):
        item['authors_gtrans'] = google_translator(item['authors_ch'])
    else:
        item['authors_gtrans'] = None
    if item['organizations'] != None:        
        item['orgs_gtrans'] = google_translator(item['organizations'])
    else:    
        item['orgs_gtrans'] = None
    if (item['abstract_ch'] != None) and (item['abstract_en'] == None):
        item['abstract_gtrans'] = google_translator(item['abstract_ch'])
    else:
        item['abstract_gtrans'] = None
    if item['keywords_ch'] != None:    
        item['keywords_gtrans'] = google_translator(item['keywords_ch'])
    else:
        item['keywords_gtrans'] = None
    print item['id']
    return item



