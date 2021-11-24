# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 15:23:48 2020
"""

from bs4 import BeautifulSoup
import time
import requests
import pyodbc
from datetime import datetime
from math import ceil
import json
import sys, os

def exception_fun(e):
    print(e)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
        
def getDate(date) :
    month = date[0:3].lower()
    monthList = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
    
    if month in monthList :       
        monthNumber = str(monthList.index(month) + 1)   
        
        if int(monthNumber) > datetime.now().month or int(date[4:6]) > datetime.now().day:
            year = str((datetime.now().year)-1)
        else :
            year = str(datetime.now().year)
        if int(monthNumber) < 10 :
            monthNumber = "0" + monthNumber
        dateInMonth = str(date[4:6])
        exactDate = year+"-"+monthNumber+"-"+dateInMonth
        return exactDate
    else :
        print("Date not found")
        return 0

def bayt_get_total_pages(soup):
    totalPages = 0
    try:
        #main_div = soup.find(id =  'results_inner')
        class_card_p0b = soup.findAll("div", {"class": "card p0b"})
        spanTagCount = class_card_p0b[0].findAll("span")
        countString = spanTagCount[0].text.strip().find("Jobs") - 1
        totalJobs = int(spanTagCount[0].text[0:countString])
        print('Total Jobs : ',totalJobs)
        if totalJobs > 20:
           totalPages = ceil(int(totalJobs)/20)
           return totalPages
        else:
           totalPages = 1
           return totalPages
    except Exception as e:
        exception_fun(e)
        return totalPages
    
def bayt_get_page_all_post(soup):
    results_inner_card = soup.find(id = "results_inner_card")
    ### Getting all li element in the allPosts variable.
    try:
        allPosts = results_inner_card.findAll("li",{"data-js-job": True})
        return allPosts
    except Exception as e:
        exception_fun(e)
        return False
    
def bayt_get_city_list(soup):
    #ex_link = 'https://www.bayt.com/en/india/jobs/'
    #page = requests.get(ex_link , timeout=50)
    #soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")
    cities = []
    city_outer_div = soup.find_all('div', class_='accordion-animate')
    city_inner_div = city_outer_div[1].find('div',class_='accordion-content')
    city_inner_div_li = city_inner_div.find('ul').find_all('li',class_='t-small')
    for city in city_inner_div_li:
        try:
            cities.append(city.find('a').text.strip().lower())
        except Exception as e:
            exception_fun(e)
            continue
        
    city_inner_div2 = city_inner_div.find_all('div')
    try:
        city_inner_div_li2 = city_inner_div2[-1].find('ul').find_all('li')
        
        for city in city_inner_div_li2:
            try :
                cities.append(city.find('a').text.strip().lower())
            except Exception as e:
                exception_fun(e)
                continue
    except Exception as e:
         exception_fun(e)
        
    return cities
            
def Sfrogs_database_connect():
    """
    conncet Sfrogs Databse 
    """
    con1 = pyodbc.connect('Driver={SQL Server};'
              'Server= '
              'Database= '
              'uid= '
              'pwd= '
              'Trusted_Connection=no;')
    return con1


def Training_database_connect():
    """
    conncet Training Databse 
    """
    con = pyodbc.connect('Driver={SQL Server};'
                  'Server= '
                  'Database= '
                  'uid= '
                  'pwd= '
                  'Trusted_Connection=no;')
    return con


def page_loop(totalPages,table_type,country_code,woid,job_qry,main_url):
    jobs = []
    count=1
    try:
        for start in range(1, (totalPages+1) if totalPages<=500 else 501): 
            
            if table_type == 2 or table_type == 4 :
                urll = main_url + '&page='+str(start)
            else:
                urll = main_url + '/?page='+str(start)
    
            print(urll)
            page = requests.get(urll , timeout=50)
            soup = get_soup(page.text)
            
            results_inner_card = soup.find(id = "results_inner_card")
            ### Getting all li element in the allPosts variable.
            try:
                allPosts = results_inner_card.findAll("li",{"data-js-job": True})
            except Exception as e:
                exception_fun(e)
                allPosts = False
    
    
            if allPosts == False:
                time.sleep(3)
                print("Sleep for a second and try again")
                page = requests.get(urll , timeout=50)
                soup = get_soup(page.text)
                results_inner_card = soup.find(id = "results_inner_card")
                try:
                    allPosts = results_inner_card.findAll("li",{"data-js-job": True})
                except Exception as e:
                    exception_fun(e)
                    print('soup')
                    print(soup)
                    print('results inner card')
                    print(results_inner_card)
                    allPosts = False
                            
            if allPosts != False:
                for post in allPosts: 
                    print(count)
                    count+=1
                    jobdata = extract_company(post)
                    if jobdata[1] != 'confidential company':
                        #job data after parsing
                        job_post = {
                        'unique_id':post['data-job-id'],
                        'Keyword':job_qry.replace('+',' ').replace("'",''),
                        'JobTitle': jobdata[0].replace("'",''),
                        'CompanyName': jobdata[1].replace("'",'').replace(' amp; ',' & '),
                        'Location': jobdata[2].replace("'",''),
                        'Summary': jobdata[3].replace("'",''),
                        'CountryCode':country_code,
                        'Url' : "https://www.bayt.com"+jobdata[4],
                        'WoId' : woid,
                        'JobPosted': jobdata[5]
                        }
                        #print(job_post)
                        #break
                        jobs.append(job_post)
                    
        return jobs        #
    except Exception as e:
        exception_fun(e)
        return jobs

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

def get_soup(text):
    # convert Pagesource into lxml or html format
	return BeautifulSoup(text, "lxml", from_encoding="utf-8")

def link_Result(ex_link):
    page = requests.get(ex_link , timeout=50)
    #soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")
    return BeautifulSoup(page.text, "lxml", from_encoding="utf-8")

def extract_company(post):
    #get the company name
    try:
        
        #company = div.find(name="p", attrs={"class":"as"})
        company = post.find("b",{"class":"p10r"})
        if company is not None:
            com = company.text.strip()	
            ex_com = com.split("-")
            if (len(ex_com) == 3):
                company_Name = ex_com[0].lower().strip()
            elif (len(ex_com) == 2):
                company_Name = ex_com[0].lower().strip()
            else :
                company_Name = ''
            #company_Name = ex_com[0].lower()
            #company_Name = ex_com[-2].lower().strip()
    except Exception as e:
         exception_fun(e)
         company_Name=''
    #get the job titile
    try:
        if post.find('h2') != None:
            ex_jobtitle = post.find('h2').text.strip()
        #ex_jobtitle =a.text
        else :
            ex_jobtitle =""

    except Exception as e:
         exception_fun(e)
         ex_jobtitle = ''
    #get the job link    
    try:
        ex_link= post.find('h2').find('a').attrs['href']
        
    except Exception as e:
         exception_fun(e)
         ex_link = ''
    soup = link_Result('https://www.bayt.com'+ex_link)
    
    #with open('soup.txt', 'w') as outfile:
        #outfile.write(str(soup))
    #get the job location
    ex_location = ''
    ex_summ = ''
    
    try:
       ex_location=com.split("-")[-1].strip()
    except Exception as e:
        exception_fun(e)
        ex_location =''
    # get the job Description/ summary
    summ = soup.find('div', class_='card-content is-spaced')
    if summ != None:
        try:
            ex_summ = summ.text.replace("\n"," ").strip()
            ex_summ =ex_summ[:4000]             
        
        except Exception as e:
            exception_fun(e)
            summ_div = post.find('div',{"class":"t-small"})
            if summ_div != None:
                summ = summ_div.find("p")
                try:
                    ex_summ = summ.text.replace("\n"," ").strip()
                    ex_summ =ex_summ[:4000]
                except Exception as e:
                    exception_fun(e)
                    ex_summ = ''
    try :
        job_date = company.next_sibling.strip()
        ex_job_date = getDate(job_date)
    except Exception as e:
        exception_fun(e)
        try:
            job_date_ul = soup.find("ul",{"class":"list is-basic t-small"})
            job_date_div = job_date_ul.find_all("li")
            job_date = job_date_div[2].find("span").text.strip()
            ex_job_date = getDate(job_date)
        except Exception as e:
            exception_fun(e)
            ex_job_date = None
    data=[ex_jobtitle, company_Name, ex_location, ex_summ, ex_link,ex_job_date]
    return data
        
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
    
  

