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
english_countries = {'afghanistan':2, 'australia':192, 'bangladesh':6, 'botswana':141, 'canada':107, 'cayman islands':240,'china':10, 'egypt':153, 'gibraltar':220, 'hong kong':232, 'india':13, 'indonesia':14, 'ireland':73, 'kenya':162, 'kuwait':21,'libya':165,'malaysia':25,'malta':82, 'mauritius':170, 'namibia':173, 'new zealand':198,'nigeria':175,'oman':31, 'pakistan':32, 'philippines':34,'puerto rico':213, 'qatar':35,'saudi arabia':37,'singapore':38, 'south africa':182, 'taiwan':42, 'tanzania':186, 'uganda':189, 'united arab emirates':48, 'united kingdom':101,'united states of america':125,'vietnam':50, 'zambia':190}

status = req.status_code

print("""
      1. If Input is keyword and CountryID (All).
      2. If Input is keyword and CountryID (New).
      3. If Input is only workorderid (All).
      4. If Input is only workorderid (New).
      
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
    
    query ="select top 100 * from Training.dbo.IndeedInput where  iscareerjetjobprocessed is null and isactive = 1 and workorderid =670 and countryid =13" #and searchkeyword in ('learning officer') "#.format(workorder_id)
    #query ="select top 100 * from IndeedInput where  iscareerjetjobprocessed is null and isactive = 1 and workorderid in (670) and countryid in (48,153,16,19,21,24,165,31,35,37, 51)" #and searchkeyword in ('learning officer') "#.format(workorder_id)
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
        jobs = []
        try:
            job_qry = value[0].strip().replace(' ','+').lower()  # replace space to '+' sign if two or more words is there
 
            city = value[1].strip() .replace(' ','+').lower()    # replace space to '+' sign if two or more words is there
            file_name = job_qry.replace('+','_')+' '+city.replace('+','_')
            print(file_name)
            
            if re.search('&',job_qry): job_qry=job_qry.replace("&",'%26')
            
            for c_name, c_code in english_countries.items():
                if c_code == value[2]:
                    country_name = c_name
                    domain = domains[c_name]
            
            
            main_url = domain+'/search/jobs?s='+job_qry+'&l='+city
            #https://www.careerjet.ae/search/jobs?s=program+manager&l=United+Arab+Emirates
            #
            page = requests.get(main_url, timeout=50)
            main_soup = BeautifulSoup(page.text, 'lxml')
            
            if  input_type  == 2 or input_type == 4 :
                try:
                    search_div = main_soup.find(id = 'search-content')
                    search_div_ul = search_div.find('ul',class_='tabs-r')
                    url_new_seg = search_div_ul.find('a')['href']
                    main_url = domain+url_new_seg
                    page = requests.get(main_url, timeout=50)
                    main_soup = BeautifulSoup(page.text, 'lxml')
                except:
                    print('No new job find')
                    break
            print(main_url)  
            try:
                total_jobs_country = get_total_jobs(main_soup)
                total_pages_country = print_job_pages(total_jobs_country)
            except:
                cur.execute("update IndeedInput set iscareerjetjobprocessed =1, UpdatedDate=? where Id = ?",(datetime.now(),value[3]))
                cur.commit()
                continue
            #print(main_url)
            cities = get_countries_list(main_soup)
            
            if total_jobs_country >= 2000 and len(cities) != 0 :
                for c in cities : 
                    print(c)
                    #https://www.careerjet.ae/program-manager-jobs/dubai-123161.html
                    #https://www.careerjet.ae/program-manager-jobs/dubai-123161.html
                    url = domain + cities[c] 
                    soup = link_Result(url)
                    
                    total_jobs_city = get_total_jobs(soup)
                    total_pages_city = print_job_pages(total_jobs_city)
                    
                    sub_cities = get_sub_cities(soup)
                    
                    if total_jobs_city >= 2000 and len(sub_cities) != 0 :
                        for sub_city in sub_cities : 
                            print(sub_city)
                            url = domain + sub_cities[sub_city] 
                            soup = link_Result(url)
                            
                            total_jobs_sub_city = get_total_jobs(soup)
                            total_pages_sub_city = print_job_pages(total_jobs_sub_city)
                            
                            get_jobs = page_loop(total_pages_sub_city,input_type,domain,value[2],value[4],sub_cities[sub_city],keyword=job_qry)
                            jobs.extend(get_jobs)
                            
                    else:
                        get_jobs = page_loop(total_pages_city,input_type,domain,value[2],value[4],cities[c],keyword=job_qry)
                        jobs.extend(get_jobs)
                    
            else:
                try:
                    
                    if  input_type  == 2 or input_type == 4 :
                        search_div = main_soup.find(id = 'search-content')
                        search_div_ul = search_div.find('ul',class_='tabs-r')
                        url_new_seg = search_div_ul.find('a')['href']
                        url_new_seg = url_new_seg+'?nw=1'
                    else:
                        #aar-jobs.html
                        url_new_seg = '/' + job_qry + "-jobs.html"
                    get_jobs = page_loop(total_pages_country,input_type,domain,value[2],value[4],url_new_seg,keyword=job_qry)
                    jobs.extend(get_jobs)
                except: 
                    print('No new job find')
                    pass
                
                #https://www.careerjet.ae/program-manager-jobs.html?p=2
            #Searching for pagecount
            create_json(jobs,country_name, job_qry)
            cur.execute("update IndeedInput set iscareerjetjobprocessed =1, UpdatedDate=? where Id = ?",(datetime.now(),value[3]))
            cur.commit()
        except Exception as e:
            print(e)
            continue
    