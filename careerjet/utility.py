# -*- coding: utf-8 -*-
"""
Created on Wed Sep 29 15:19:48 2021

@author: madhyauser
"""
import requests
from bs4 import BeautifulSoup
import time 
import json
from datetime import date, timedelta,datetime
from dateutil import relativedelta
import pyodbc
from math import ceil
from googletrans import Translator
translator = Translator()


def Sfrogs_database_connect():
    """
    conncet Sfrogs Databse 
    """
    con1 = pyodbc.connect('Driver={SQL Server};'
              'Server='
              'Database='
              'uid='
              'pwd='
              'Trusted_Connection=no;')
    return con1


def Training_database_connect():
    """
    conncet Training Databse 
    """
    con = pyodbc.connect('Driver={SQL Server};'
                  'Server='
                  'Database='
                  'uid='
                  'pwd='
                  'Trusted_Connection=no;')
    return con

def get_ex_date(date_string) :
    #translation = translator.translate(date_string,dest='en')
    #date_string = translation.text
    time_ago_list = ['minute ago','minutes age','mins ago', 'hour ago', 'hours ago', 'day ago', 'days ago', 'month ago', 'months ago', 'year ago', 'years ago','just now','right now']
     
    first_alpha_index = date_string.find(next(filter(str.isalpha,date_string)))
    all_alphabets = date_string[first_alpha_index :].lower()
    if all_alphabets in time_ago_list:
        list_index = time_ago_list.index(all_alphabets)
        if list_index == 11:
            job_date = date.today()
            return job_date
        
        try :
            number = int(date_string[0:first_alpha_index].strip())
            current_date = date.today().strftime('%Y-%m-%d')
            current_date = datetime.strptime(current_date,"%Y-%m-%d")
            if list_index == 0 :
                job_date = date.today()
            elif list_index == 1 or list_index == 2:
                job_date = date.today()
            elif list_index == 3:
                job_date = date.today()
            elif list_index == 4:
                if datetime.now().hour >= int(date_string[0:first_alpha_index]):
                    job_date = date.today()
                else :
                    job_date = date.today() - timedelta(days=1)
            elif list_index == 5:
                job_date = date.today() - timedelta(days=1)
            elif list_index == 6:
                job_date = date.today() - timedelta(days=number)
            elif list_index == 7:
                job_date = current_date - relativedelta.relativedelta(months=1)
            elif list_index == 8:
                job_date = current_date - relativedelta.relativedelta(months=number)
            elif list_index == 9:
                job_date = current_date - relativedelta.relativedelta(years=1)
            elif list_index == 10:
                job_date = current_date - relativedelta.relativedelta(years=number)
            elif list_index == 11 or list_index == 12:
                job_date = date.today()
            else:
                job_date = ''
            return job_date
        except Exception as e :
            print(e)
            return ''
    else :
        #print('Date Not Found')
        return ''
    
def get_countries_domain(soup):
    country_with_domain = {}
    main_div = soup.find(id = 'sites')
    try :
        main_div_ul = main_div.find('ul')
        country_domain_list = main_div_ul.find_all('li') 
        for dom in country_domain_list:
            country_with_domain[dom.find('a').text.strip().lower()] = dom.find('a')['href']
        #print(country_with_domain)
        return country_with_domain
    except :
        return country_with_domain
    
def get_countries_list(soup):
    #ex_link = 'https://www.careerjet.co.in/search/jobs?s=&l=India'
    #page = requests.get(ex_link , timeout=50)
    #soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")  
    cities = {}
    try:
        inner_div = soup.find(id ='search-form-inner')
        inner_div_ul = inner_div.find('ul', class_='facets locations')
        inner_div_li = inner_div_ul.find_all('li', class_='child')
        for li in inner_div_li:
            cities[li.text.strip().lower()] = li.find('a')['href']
        return cities  
    except Exception as e:
        print(e)
    finally:
        return cities
    
def print_job_pages(total_jobs):
    print('Total Jobs : ',total_jobs)
    total_pages = ceil(total_jobs/20)
    print('Total Pages : ',total_pages)
    return total_pages
    
def get_sub_cities(soup):
    sub_cities = {}
    try:
        location_div = soup.find(id = 'search-location')
        location_ul = location_div.find('ul', class_='facets locations')
        location_li = location_ul.find_all('li', class_='child')
        for li in location_li:
            sub_cities[li.text.strip().lower()] = li.find('a')['href']
        return sub_cities  
    except:
        return sub_cities
    
def page_loop(total_pages,input_type,country_domain,country_code,woid, c_url,non_english=False,keyword=''):    
    jobs = []
    count=1
    try:
        sub_city_segs = c_url.split('?')
        for page in range(1,(total_pages+1) if total_pages <= 100 else 100): 
        #https://www.careerjet.ae/program-manager-jobs/dubai-123161.html?p=2
        #https://www.careerjet.ae/program-manager-jobs/dubai-123161.html?p=1
            if input_type == 2 or input_type == 4:
                soup = link_Result(country_domain + sub_city_segs[0] +'?p='+str(page)+'&'+sub_city_segs[1])
            else:
                soup = link_Result(country_domain + sub_city_segs[0] + '?p='+str(page))
                print(country_domain + sub_city_segs[0] + '?p='+str(page))
                
            all_posts = get_job_data(soup) 
            
            if len(all_posts) != 0 :
                for post in all_posts: 
                    print(count)
                    count+=1
                    jobdata = get_post_data(post,country_domain,non_english)
                    job_post = {
                        'unique_id':jobdata[3],
                        'Keyword':keyword,
                        'JobTitle': jobdata[1].replace("'",''),
                        'CompanyName': jobdata[5].replace("'",'').replace(' amp; ',' & '),
                        'Location': jobdata[6].replace("'",''),
                        'Summary': jobdata[4].replace("'",''),
                        'CountryCode':country_code,
                        'Url' : jobdata[0],
                        'WoId' : woid,
                        'JobPosted': jobdata[2]
                        }
                    #print(job_post)
                    jobs.append(job_post)
        return jobs
    except Exception as e:
        print(e)
        return jobs
    
def get_total_jobs(soup,non_english=False):
    main_div = soup.find(id = 'search-content')
    try:
        main_div_header = main_div.find('header')
        all_p_elemnets = main_div_header.find_all('p')
        total_jobs_span = all_p_elemnets[1].find('span').text.strip()
        if non_english :
            translation = translator.translate(total_jobs_span,dest='en')
            total_jobs_span = translation.text
        jobs_index = total_jobs_span.find(next(filter(str.isalpha,total_jobs_span)))
        number = total_jobs_span[0:jobs_index].replace(' ','').replace(',','')
        return int(number)
    except Exception as e:
        print(e)
        print('jobs not found')
        return False
    
def get_job_data(soup):
    main_div = soup.find(id = 'search-content')
    try:
        jobs_div = main_div.find('ul', class_='jobs')
        return jobs_div.find_all('li',attrs={'class':None},recursive=False)
    except:
        return []
def link_Result(ex_link):
    page = requests.get(ex_link , timeout=50)
    return BeautifulSoup(page.text, "lxml", from_encoding="utf-8")  

def create_json(jobs, country, job_qry=None):
    # get today date
    time_stamp=time.strftime("%d_%m_%Y")   # get today date
    if job_qry != None:
        with open('./Json/'+job_qry.replace('+','_')+'_'+country.replace('+','_')+'_'+time_stamp+'.json', 'w') as outfile:
            json.dump(jobs, outfile)
    else :
        with open('./Json/'+country.replace('+','_')+'_'+time_stamp+'.json', 'w') as outfile:
            json.dump(jobs, outfile)
    print("successfull")

def get_post_data(post,url,non_english=False):
    job_data = []
    post_header_div = post.find('header')
    job_link = post_header_div.find('a')['href']
    ex_link = url+job_link
    soup = link_Result(ex_link)
    
    unique_id = job_link.split('/')[-1]
    
    try: 
        job_title = post_header_div.find('a').text.strip()
        if non_english:
            job_title = translator.translate(job_title,dest='en').text
    except:
        job_div = soup.find(id = 'job')
        try:
            job_header_div = job_div.find('header')
            job_title = job_header_div.find('h1').text.strip()
            if non_english:
                job_title = translator.translate(job_title,dest='en').text
        except:
            job_title = ''
       
    post_footer_div = post.find('footer')
    try:
        post_footer_ul = post_footer_div.find('ul', class_='tags')
        post_footer_li = post_footer_ul.find('li').text.strip()
        if non_english:
            job_date_obj = get_ex_date(translator.translate(post_footer_li,dest='en').text)
        else:
            job_date_obj = get_ex_date(post_footer_li)
        try:
            job_date = job_date_obj.strftime('%Y-%m-%d')
        except :
            job_date = ''
    except:
        try:
            job_div = soup.find(id = 'job')
            post_header = job_div.find('ul', class_='tags')
            post_footer_li = post_header.find('li').text.strip()
            if non_english:
                job_date_obj = get_ex_date(translator.translate(post_footer_li,dest='en').text)
            else:
                job_date_obj = get_ex_date(post_footer_li)
            try:
                job_date = job_date_obj.strftime('%Y-%m-%d')
            except :
                job_date = ''
        except :
            job_date = None
      
    try:
        job_company = post.find('p', class_='company').text.strip()
    except :
        company_div = soup.find(id = 'job')
        try:
            job_company = company_div.find('p', class_='company').text.strip()
        except:
            job_company = ''
   
    try:
        job_location = post.find('ul', class_='location').text.strip()
    except:
        location_div = soup.find(id = 'job')
        try:
            job_company_ul = location_div.find('ul', class_='details')
            job_location = job_company_ul.find('li').text.strip()
        except:
            job_location = ''  
      
    try: 
        summary_div = soup.find(id = 'job')
        job_summary = summary_div.find('section', class_='content')
        job_summary = (job_summary.text.strip())[0:4001]
        if non_english:
            job_summary = translator.translate(job_summary,dest='en').text
    except:
        job_summary = post.find('div', class_='desc').text.strip()
        if non_english:
            job_summary = translator.translate(job_summary,dest='en').text
        

    job_data = [ex_link,job_title,job_date,unique_id,  job_summary,job_company,job_location]

    return job_data
            
            
def write_logs(log_file,text):
    """
    write_logs(text):-
    /t/t this function will store the error 
    """
    f = open(log_file,'a')
    f.write("*"*60+'\n')
    f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    f.write(text + '\n\n')  
    f.close()
    