# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 08:47:16 2020

@author: Sanjay Sharma
"""


import os
import pyodbc
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
import requests
import json
import datetime as datetime
from utility import *

time_stamp = time.strftime("%d_%m_%Y")   # get today date

### Creating a base url that we user anywhere
BASE_URL = "https://www.careerjet.co.za"

### Total number of jobs in per page
JOBS_PER_PAGE = 20

req = requests.get(BASE_URL+'/sites')
soup = BeautifulSoup(req.content, "html.parser")
domains = get_countries_domain(soup)
# staus variable to track status of the website
non_english_countries = {'angola':139, 'argentina':126, 'austria':55, 'belarus':57, 'belgium':58, 'benin':140, 'bolivia':127, 'bosnia and herzegovina':59, 'brazil':128, 'bulgaria':60, 'burundi':143, 'cameroon':145, 'central african republic':146, 'chile':129,'colombia':130, 'costa rica':108, 'croatia':61, 'cyprus':62, 'czech republic':63, 'denmark':64, 'dominican republic':111, 'ecuador':131,  'el salvador':112, 'estonia':65, 'ethiopia':156, 'finland':66, 'france':67, 'gabon':157, 'germany':69, 'greece':70, 'greenland':212,'guadeloupe':217, 'guatemala':114, 'honduras':116, 'hungary':71, 'israel':17, 'italy':74, 'japan':18, 'kazakhstan':75, 'latvia':77,  'liechtenstein':78, 'lithuania':79, 'luxembourg':80, 'madagascar':166, 'mali':168, 'martinique':218,'mexico':118, 'montenegro':85, 'morocco':171, 'mozambique':172, 'netherlands':86, 'nicaragua':119,'norway':87, 'panama':120, 'paraguay':133, 'peru':134, 'poland':88, 'portugal':89, 'romania':90, 'russia':91, 'senegal':178, 'serbia':93,'slovakia':94, 'slovenia':95,'south korea':39, 'spain':96, 'sweden':97, 'switzerland':98,'thailand':44, 'togo':187, 'tunisia':188, 'turkey':99,'ukraine':100,'uruguay':136, 'venezuela':137}

status = req.status_code

print("""
      1. If Input is keyword and CountryID press 1(All).
      2. If Input is keyword and CountryID press 1(New).
      3. If Input is only workorderid press 2(All).
      4. If Input is only workorderid press 2(New).
      
      """)
input_type = int(input("Press 1 or 2 or 3 or 4: "))

if input_type  == 1 or input_type == 2:
    keyword_input = input("Enter a keyword: ").strip()
    workorder_id =input("Enter workorder Id:- ").strip()
    country_id = input("Enter Country Id:- ").strip()
    query = "select top 100 * from IndeedInput where IsCareerjetJobProcessed=0 and CountryId={} and IsActive=1 and SearchKeyword in ('{}') order by Id desc".format(country_id,keyword_input)

elif  input_type  == 3 or input_type == 4 :
    #workorder_id =input("Enter workorder Id:- ").strip()
    #country_id = input("Enter Country Id:- ").strip()
    
    query ="select top 100 * from IndeedInput where  iscareerjetjobprocessed is null and isactive = 1 and workorderid in (504) and countryid in (48,153,16,19,21,24,165,31,35,37, 51)" #and searchkeyword in ('learning officer') "#.format(workorder_id)
    #query ="select top 100 * from IndeedInput where  IsADZUNAjobProcessed=0 and searchkeyword not in('recruiter','training','fastly') and CountryId={} and workorderid={}   and countryid in (13,125,182,38,36,88,198,86,74,67,69,107,128,55,192,101) and  IsActive=1  order by Id desc ".format(country_id,workorder_id)

else:
    print("Your input is wrong. Please run again")


while True:
    con = Training_database_connect()
    cur = con.cursor()
    table =pd.read_sql_query(query,con)
    print(len(table))
    print("-"*60)
    table.loc[table.Location == "United Kingdom", "Location"] = "UK"
    table.loc[table.Location == "Italy", "Location"] = "Italia"
    
    #If no keyword is there
    if len(table)<1:
        break

    
    job_set = [i for i in table['SearchKeyword']]
    city_set1 = [i for i in table['Location']]
    country = [i for i in table['CountryId']]
    Id = [i for i in table['Id']]
    Wid = [i for i in table['WorkOrderId']]
    Key_Loc = list(zip(job_set,city_set1,country,Id,Wid))
        
    for value in Key_Loc: 
        
        try:
            job_qry = value[0].strip().replace(' ','+').lower()  # replace space to '+' sign if two or more words is there
 
            city = value[1].strip() .replace(' ','+').lower()    # replace space to '+' sign if two or more words is there
            file_name = job_qry.replace('+','_')+' '+city.replace('+','_')
            
            if re.search('&',job_qry): job_qry=job_qry.replace("&",'%26')
            
            for c_name, c_code in non_english_countries.items():
                if c_code == value[2]:
                    country_name = c_name
                    domain = domains[c_name]
            
            main_url = domain+'/search/jobs?s='+job_qry+'&l='+city
            #https://www.careerjet.ae/search/jobs?s=program+manager&l=United+Arab+Emirates
            #
            page = requests.get(main_url, timeout=50)
            main_soup = BeautifulSoup(page.text, 'lxml')
            try:
                total_jobs_country = get_total_jobs(main_soup,non_english=True)
                total_pages_country = print_job_pages(total_jobs_country)
            except:
                cur.execute("update IndeedInput set iscareerjetjobprocessed =1, UpdatedDate=? where Id = ?",(datetime.datetime.now(),value[3]))
                cur.commit()
                continue
            
            cities = get_countries_list(soup)
            
            if len(cities) != 0 :
                for city in cities : 
                    print(city)
                    #https://www.careerjet.ae/program-manager-jobs/dubai-123161.html
                    #https://www.careerjet.ae/program-manager-jobs/dubai-123161.html
                    url = domain + cities[city] 
                    soup = link_Result(url)
                    
                    total_jobs_city = get_total_jobs(soup,non_english=True)
                    total_pages_city = print_job_pages(total_jobs_city)
                    
                    sub_cities = get_sub_cities(soup)
                    
                    if len(sub_cities) != 0 :
                        for sub_city in sub_cities : 
                            print(sub_city)
                            url = domain + sub_cities[sub_city] 
                            soup = link_Result(url)
                            
                            total_jobs_sub_city = get_total_jobs(soup,non_english=True)
                            total_pages_sub_city = print_job_pages(total_jobs_sub_city)
                            
                            get_jobs = page_loop(total_pages_sub_city,input_type,domain,value[2],value[4],sub_cities[sub_city],non_english=True)
                            jobs.extend(get_jobs)
                            
                    else:
                        get_jobs = page_loop(total_pages_city,input_type,domain,value[2],value[4],cities[city],non_english=True)
                        jobs.extend(get_jobs)
                    
            else:
                search_div = main_soup.find(id = 'search-content')
                search_div_ul = search_div.find('ul',class_='tabs-r')
                url_new_seg = search_div_ul.find('a')['href']
                #https://www.careerjet.ae/program-manager-jobs.html?p=2
                get_jobs = page_loop(total_pages_country,input_type,domain,value[2],value[4],url_new_seg,non_english=True)
                jobs.extend(get_jobs)
            #Searching for pagecount
            create_json(jobs,country_name)
            cur.execute("update IndeedInput set iscareerjetjobprocessed =1, UpdatedDate=? where Id = ?",(datetime.datetime.now(),value[3]))
            cur.commit()
        except Exception as e:
            print(e)
            continue