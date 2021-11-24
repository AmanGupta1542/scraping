# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 08:47:16 2020

@author: Sanjay Sharma
"""


from re import search
from pandas import read_sql_query
from datetime import datetime
from utility import *

print("""
      1. If Input is keyword and CountryID (All Jobs) press 1.
      2. If Input is keyword and CountryID (Last 30 days Job) press 1.
      3. If Input is only workorderid (All Jobs) press 2.
      4. If Input is only workorderid (Last 30 days Job) press 2.
      """)
table_type = int(input("Press 1 or 2 or 3 or 4: "))
if table_type  == 1 or table_type  == 2:
    keyword_input = input("Enter a keyword: ").strip()
    workorder_id =input("Enter workorder Id:- ").strip()
    country_id = input("Enter Country Id:- ").strip()
    query = "select top 100 * from IndeedInput where IsbytejobProcessed=0 and CountryId={} and IsActive=1 and SearchKeyword in ('{}') order by Id desc".format(country_id,keyword_input)
elif  table_type  == 3 or table_type  == 4:
    #workorder_id =input("Enter workorder Id:- ").strip()
    #country_id = input("Enter Country Id:- ").strip()
    
    query ="select top 1 * from IndeedInput where  IsbytejobProcessed=0 and isactive = 1 and workorderid in (504,494) and countryid in (51,48,188,37,35,32,31,171,165,24,21,19,16,13,153,5,38)" #and searchkeyword in ('learning officer') "#.format(workorder_id)
    #query ="select top 100 * from IndeedInput where  IsADZUNAjobProcessed=0 and searchkeyword not in('recruiter','training','fastly') and CountryId={} and workorderid={}   and countryid in (13,125,182,38,36,88,198,86,74,67,69,107,128,55,192,101) and  IsActive=1  order by Id desc ".format(country_id,workorder_id)

else:
    print("Your input is wrong. Please run again")

print(table_type)
print(type(table_type))
while True:
    con = Training_database_connect()
    cur = con.cursor()
    table = read_sql_query(query,con)
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
        if value[1] == 'United Arab Emirates':
            value[1]=='uae'
        
        try:
            job_qry = value[0].strip() .replace(' ','-').lower()  # replace space to '+' sign if two or more words is there
 
            city = value[1].strip() .replace(' ','-').lower()    # replace space to '+' sign if two or more words is there
            file_name = job_qry.replace('+','_')+' '+city.replace('+','_')
            
            if search('&',job_qry): job_qry=job_qry.replace("&",'%26')
            countries = { 'yemen':51,'uae':48, 'tunisia':188,'saudi-arabia':37,'qatar':35,'pakistan':32,'oman':31,'morocco':171,'libya':165,'lebanon':24,'kuwait':21,'jordan':19,'iraq':16,'india':13,'egypt':153,'bahrain':5,'algeria':138}

            domain_c = [k for k,v in countries.items() if v == int(value[2])]
            domain = 'https://www.bayt.com/en/'+domain_c[0]+'/jobs/'
            #print(domain)
            
            if table_type == 2 or table_type == 4 :
                main_url = domain+job_qry+'-jobs/?filters%5Bjb_last_modification_date_interval%5D%5B%5D=1'
            else : 
                main_url = domain+job_qry+'-jobs/'
            try :
                totalPages = bayt_get_total_pages(link_Result(main_url)) 
            except:
                cur.execute("update IndeedInput set IsBytejobProcessed =1, UpdatedDate=? where Id = ?",(datetime.now(),value[3]))
                cur.commit()
                continue
            print("Total Pages : ",int(totalPages))
            jobs = []
            print(file_name)
            
            if totalPages > 500 :
                cities = bayt_get_city_list(link_Result(main_url))
                for c in cities : 
                    c = c.replace(' ','-')
                    print(c)
                    if table_type == 1 or table_type == 3 :
                        urll = 'https://www.bayt.com/en/'+domain_c[0]+'/jobs/'+job_qry+'-jobs-in-'+c+'/'
                    else :
                        urll = 'https://www.bayt.com/en/'+domain_c[0]+'/jobs/'+job_qry+'-jobs-in-'+c+'/?filters%5Bjb_last_modification_date_interval%5D%5B%5D=1'
                        #https://www.bayt.com/en/india/jobs/jobs-in-bengaluru/?filters%5Bjb_last_modification_date_interval%5D%5B%5D=1&page=2
                    #soup = link_Result(urll)
                    total_pages = bayt_get_total_pages(link_Result(urll)) 
                    print(city.replace('+','_')+'_'+time.strftime("%d_%m_%Y")+'.json')
                    print('Total Pages : ',total_pages)
                      
                    get_jobs = page_loop(total_pages,table_type,value[2],value[4],job_qry,urll) 
                    jobs.extend(get_jobs)
            else:
                get_jobs = page_loop(totalPages,table_type,value[2],value[4],job_qry,main_url)
                jobs.extend(get_jobs)
            create_json(jobs,city,job_qry)
               
            cur.execute("update IndeedInput set IsBytejobProcessed =1, UpdatedDate=? where Id = ?",(datetime.now(),value[3]))
            cur.commit()
            
        except Exception as e:
            print(e)
            continue
