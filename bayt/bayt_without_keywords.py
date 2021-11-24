# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 10:20:58 2021

@author: Aman Gupta
"""

from time import strftime
from utility import *

print("""
      1. All jobs
      2. Last 30 days job
      """)
      
input_type = int(input("Press 1 or 2 : "))

countries = { 'yemen':51,'uae':48, 'tunisia':188,'saudi-arabia':37,'qatar':35,'pakistan':32,'oman':31,'morocco':171,'libya':165,'lebanon':24,'kuwait':21,'jordan':19,'iraq':16,'india':13,'egypt':153,'bahrain':5,'algeria':138}

for country in countries.keys() : 
    try:
        domain = 'https://www.bayt.com/en/'+country+'/jobs/'
        print(country+'.json')
        jobs = []
        if input_type == 1 :
            main_url = domain
        else :
            main_url = domain+'?filters%5Bjb_last_modification_date_interval%5D%5B%5D=1'
        total_pages = bayt_get_total_pages(link_Result(main_url)) 
        print(country.replace('+','_')+'_'+strftime("%d_%m_%Y")+'.json')
        print('Total Pages : ',total_pages)
     
        if total_pages > 500 :
            cities = bayt_get_city_list(link_Result(main_url))
            for city in cities : 
                city = city.replace(' ','-')
                print(city)
                if input_type == 1:
                    city_urll = main_url+'jobs-in-'+city
                else :
                    city_urll = main_url+'jobs-in-'+city+'/?filters%5Bjb_last_modification_date_interval%5D%5B%5D=1'
                    
                total_pages = bayt_get_total_pages(link_Result(city_urll)) 
                print(country.replace('+','_')+'_'+strftime("%d_%m_%Y")+'.json')
                print('Total Pages : ',total_pages)
                woid = job_qry = ''
                get_jobs = page_loop(total_pages,input_type,countries[country],woid,job_qry,city_urll) 
                jobs.extend(get_jobs)
        else :
            woid = job_qry = ''
            get_jobs = page_loop(total_pages,input_type,countries[country],woid,job_qry,main_url) 
            jobs.extend(get_jobs)
        create_json(jobs,country)
    except Exception as e :
        print(e)
        continue
    
