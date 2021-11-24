# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 10:47:23 2021

@author: madhyauser
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep 29 13:51:14 2021

@author: Aman Gupta
"""

from math import ceil
from utility import *
from time import strftime
import sys, os

JOBS_PER_PAGE = 20

soup = link_Result("https://www.careerjet.ae/sites")
domains = get_countries_domain(soup)

non_english_countries = {'angola':139, 'argentina':126, 'austria':55, 'belarus':57, 'belgium':58, 'benin':140, 'bolivia':127, 'bosnia and herzegovina':59, 'brazil':128, 'bulgaria':60, 'burundi':143, 'cameroon':145, 'central african republic':146, 'chile':129,'colombia':130, 'costa rica':108, 'croatia':61, 'cyprus':62, 'czech republic':63, 'denmark':64, 'dominican republic':111, 'ecuador':131,  'el salvador':112, 'estonia':65, 'ethiopia':156, 'finland':66, 'france':67, 'gabon':157, 'germany':69, 'greece':70, 'greenland':212,'guadeloupe':217, 'guatemala':114, 'honduras':116, 'hungary':71, 'israel':17, 'italy':74, 'japan':18, 'kazakhstan':75, 'latvia':77,  'liechtenstein':78, 'lithuania':79, 'luxembourg':80, 'madagascar':166, 'mali':168, 'martinique':218,'mexico':118, 'montenegro':85, 'morocco':171, 'mozambique':172, 'netherlands':86, 'nicaragua':119,'norway':87, 'panama':120, 'paraguay':133, 'peru':134, 'poland':88, 'portugal':89, 'romania':90, 'russia':91, 'senegal':178, 'serbia':93,'slovakia':94, 'slovenia':95,'south korea':39, 'spain':96, 'sweden':97, 'switzerland':98,'thailand':44, 'togo':187, 'tunisia':188, 'turkey':99,'ukraine':100,'uruguay':136, 'venezuela':137}

print("""
      1. All jobs
      2. New job
      """)
      
input_type = int(input("Press 1 or 2 : "))

for country in domains: 
    if country in non_english_countries.keys() : 
        try:
            country_domain = domains[country]
            jobs = []
            count = 1
            soup = link_Result(domains[country])
            home_div = soup.find(id='home')
            url_segment = home_div.find(id='search-main')['action'].strip()
            soup = link_Result(country_domain + url_segment)
            
            search_div = soup.find(id = 'search-content')
            search_div_ul = search_div.find('ul',class_='tabs-r')
            url_new_seg = search_div_ul.find('a')['href']
            url_new_seg_split = url_new_seg.split('?') 
             
            if input_type == 2 :
                soup = link_Result(country_domain + url_new_seg)
        
            time_stamp = strftime("%d_%m_%Y")
            print('File Name : ',country.replace('+','_')+'_'+time_stamp+'.json')
                
            total_jobs_country = get_total_jobs(soup,non_english=True)
            total_pages_country = print_job_pages(total_jobs_country)
            
            cities = get_countries_list(soup)
            if len(cities) != 0 :
                for city in cities : 
                    print(city)
                    url = country_domain + cities[city] 
                    soup = link_Result(url)
                    
                    total_jobs_city = get_total_jobs(soup,non_english=True)
                    total_pages_city = print_job_pages(total_jobs_city)
                    
                    sub_cities = get_sub_cities(soup)
                    
                    if len(sub_cities) != 0 :
                        for sub_city in sub_cities : 
                            print(sub_city)
                            url = country_domain + sub_cities[sub_city] 
                            soup = link_Result(url)
                            
                            total_jobs_sub_city = get_total_jobs(soup,non_english=True)
                            total_pages_sub_city = print_job_pages(total_jobs_sub_city)
                            
                            get_jobs = page_loop(total_pages_sub_city,input_type,country_domain,non_english_countries[country],'',sub_cities[sub_city],non_english=True)
                            jobs.extend(get_jobs)
                    else:
                        get_jobs = page_loop(total_pages_city,input_type,country_domain,non_english_countries[country],'',cities[city],non_english=True)
                        jobs.extend(get_jobs)
            else:
                get_jobs = page_loop(total_pages_country,input_type,country_domain,non_english_countries[country],'',url_new_seg,non_english=True)
                jobs.extend(get_jobs)
            
            create_json(jobs,country)
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            continue