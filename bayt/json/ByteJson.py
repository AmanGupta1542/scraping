
import re
from utility import *
import json
import os
from datetime import datetime
from string import punctuation

def remove_punc_from_text(text):
    keyword = ['"',';','?',',','.',':','-','|','(',')','/','!','–','_','*']
    s = list(punctuation)
    s.remove('&')
    s.remove("'")
    pattern = re.compile("\\"+"|\\".join(keyword))
    text = re.sub(r"\s{1,}", ' ', re.sub(pattern, ' ',  text)).strip()
    return text.replace(" & "," and ").replace("&"," and ")

    
def get_previous_date(post_date):
    #date_N_days_ago = datetime.now() - timedelta(days=n_day)
    #return date_N_days_ago.strftime("%Y-%m-%d")

    today = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), '%Y-%m-%d')
    pre_date = datetime.strptime(post_date, '%Y-%m-%d')
    delta = today - pre_date
    return delta.days


def replaceing_text(row):
    row['JobTitle']= row['JobTitle'].replace('?','')
    row['CompanyName']= row['CompanyName'].replace('?','')
    row['Location']= row['Location'].replace('?','')
    #row['JobPosted']= row['JobPosted'].replace('?','')
    return row

#change the directory
#os.chdir('C:/Users/demofrogs/Desktop/PythonProgram/indeed_proxy/JsonFile')
#os.chdir('C:/Users/demofrogs/Desktop/Python Program/indeed -proxy/JsonFile')
os.chdir('C:/Users/demofrogs/Desktop/Python Program/bayt/Json')

path = os.getcwd()
files = os.listdir() # get all files
json_files = [f for f in files if f[-4:] == 'json'] # filter json files
con1 = Sfrogs_database_connect()
cur = con1.cursor()

for file in json_files: 
    #file=json_files[163]
    print(file)
    json_file =open(file)
    data = json_file.read()
    l = []; c = 1
    for row in json.loads(data,encoding='ascii'): 
        print(c);c+=1
        row = replaceing_text(row)
        # UPDATE IndeedJobPostTemp SET JobDatedays = Jobposted WHERE id = @Id
        try:
            if row['CompanyName'] != '':
                jobdate_copy= get_previous_date(row['JobPosted'])  ## day "2021-09-19"
                row['JobTitle'] = remove_punc_from_text(row['JobTitle'])
                row['Summary'] = remove_punc_from_text(row['Summary'])
                try:
                    cur =cur.execute("insert into training.dbo.ByteJobPostTemp(Keyword, JobTitle, CompanyName, Location,Summary, \
                            CountryCode, Url,Source,JobPosted,WorkOrderId,jobdate,jobDatedays,jobdays) values(?,?,?,?,?,?,?,?,?,?,?,?,?)",(row['Keyword'],row['JobTitle'],\
                            row['CompanyName'],row['Location'].split(',')[0],row['Summary'],\
                            row['CountryCode'],row['Url'],'ByteJobs',row['JobPosted'],row['WoId'],row['JobPosted'],jobdate_copy,jobdate_copy))
                    cur.commit()
                except Exception as e:
                    with open(path+'\\'+'errorfile.txt', 'a+') as outfile:
                        outfile.write(",\n")
                        json.dump(row, outfile)
                        outfile.close()
        except Exception as e:
            with open(path+'\\'+'errorfile.txt', 'a+') as outfile:
                outfile.write(",\n")
                json.dump(row, outfile)
                outfile.close()
    json_file.close()
    os.remove(path+'\\'+file)
