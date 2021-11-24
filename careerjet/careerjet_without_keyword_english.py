# -*- coding: utf-8 -*-
"""
Created on Wed Sep 29 13:51:14 2021

@author: Aman Gupta
"""

from math import ceil
from utility import *
from time import strftime

JOBS_PER_PAGE = 20

soup = link_Result("https://www.careerjet.ae/sites")
domains = get_countries_domain(soup)

english_countries = {'afghanistan':2, 'australia':192, 'bangladesh':6, 'botswana':141, 'canada':107, 'cayman islands':240,'china':10, 'egypt':153, 'gibraltar':220, 'hong kong':232, 'india':13, 'indonesia':14, 'ireland':73, 'kenya':162, 'kuwait':21,'libya':165,'malaysia':25,'malta':82, 'mauritius':170, 'namibia':173, 'new zealand':198,'nigeria':175,'oman':31, 'pakistan':32, 'philippines':34,'puerto rico':213, 'qatar':35,'saudi arabia':37,'singapore':38, 'south africa':182, 'taiwan':42, 'tanzania':186, 'uganda':189, 'united arab emirates':48, 'united kingdom':101,'united states of america':125,'vietnam':50, 'zambia':190}


print("""
      1. All jobs
      2. New job
      """)
      
input_type = int(input("Press 1 or 2 : "))

for country in domains: 
    if country in english_countries.keys() : 
        try:
            country_domain = domains[country]
            jobs = []
            count = 1
            soup = link_Result(country_domain + '/search/jobs')
            
            search_div = soup.find(id = 'search-content')
            search_div_ul = search_div.find('ul',class_='tabs-r')
            url_new_seg = search_div_ul.find('a')['href']
            url_new_seg_split = url_new_seg.split('?') 
             
            if input_type == 2 :
                soup = link_Result(country_domain + url_new_seg)
        
            time_stamp = strftime("%d_%m_%Y")
            print('File Name : ',country.replace('+','_')+'_'+time_stamp+'.json')
                
            total_jobs_country = get_total_jobs(soup)
            total_pages_country = print_job_pages(total_jobs_country)
            
            cities = get_countries_list(soup)
            if len(cities) != 0 :
                for city in cities : 
                    print(city)
                    url = country_domain + cities[city] 
                    soup = link_Result(url)
                    
                    total_jobs_city = get_total_jobs(soup)
                    total_pages_city = print_job_pages(total_jobs_city)
                    
                    sub_cities = get_sub_cities(soup)
                    
                    if len(sub_cities) != 0 :
                        for sub_city in sub_cities : 
                            print(sub_city)
                            url = country_domain + sub_cities[sub_city] 
                            soup = link_Result(url)
                            
                            total_jobs_sub_city = get_total_jobs(soup)
                            total_pages_sub_city = print_job_pages(total_jobs_sub_city)
                            
                            get_jobs = page_loop(total_pages_sub_city,input_type,country_domain,english_countries[country],'',sub_cities[sub_city])
                            jobs.extend(get_jobs)
                    else:
                        get_jobs = page_loop(total_pages_city,input_type,country_domain,english_countries[country],'',cities[city])
                        jobs.extend(get_jobs)
            else:
                get_jobs = page_loop(total_pages_country,input_type,country_domain,english_countries[country],'',url_new_seg)
                jobs.extend(get_jobs)
            
            create_json(jobs,country)
        except Exception as e:
            print(e)
            continue