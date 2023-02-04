from bs4 import *
import pickle
import concurrent.futures
import time,datetime
import os,cv2
import pandas as pd

import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime
import concurrent.futures
import boto3
from botocore.exceptions import NoCredentialsError
import datetime
from bs4 import *
import pickle
import concurrent.futures
import time,datetime
import os,cv2
from .download import Downloading
import requests
import shutil
import requests
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
import requests
import random
import time
import json
import pandas as pd
# Import the Images module from pillow
from PIL import Image
import os
import datetime
from pathlib import Path
import shutil




ACCESS_KEY = 'AKIARPPQWUWXQJGAVPSZ'
SECRET_KEY = '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'
BUKET_NAME= "cs181106"

USER_AGENTS = [
('Mozilla/5.0 (X11; Linux x86_64) '
'AppleWebKit/537.36 (KHTML, like Gecko) '
'Chrome/57.0.2987.110 '
'Safari/537.36'),  # chrome
('Mozilla/5.0 (X11; Linux x86_64) '
'AppleWebKit/537.36 (KHTML, like Gecko) '
'Chrome/61.0.3163.79 '
'Safari/537.36'),  # chrome
('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
'Gecko/20100101 '
'Firefox/55.0'),  # firefox
('Mozilla/5.0 (X11; Linux x86_64) '
'AppleWebKit/537.36 (KHTML, like Gecko) '
'Chrome/61.0.3163.91 '
'Safari/537.36'),  # chrome
('Mozilla/5.0 (X11; Linux x86_64) '
'AppleWebKit/537.36 (KHTML, like Gecko) '
'Chrome/62.0.3202.89 '
'Safari/537.36'),  # chrome
('Mozilla/5.0 (X11; Linux x86_64) '
'AppleWebKit/537.36 (KHTML, like Gecko) '
'Chrome/63.0.3239.108 '
'Safari/537.36'),  # chrome
]
ACCESS_KEY = 'AKIARPPQWUWXQJGAVPSZ'
SECRET_KEY = '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'
BUKET_NAME= "cs181106"
unsupported_browser = 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'

header = {
    'user-agent':'',
    'referer':'https://www.google.com/',
    'X-Requested-With': 'XMLHttpRequest'

    }
    
s = requests.Session()
with open('facebook_cookie.json') as c:
    load = json.load(c)

for cookie in load:
    s.cookies.set(cookie['name'],cookie['value'])

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--headless')
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920x1080")
options.add_argument('--disable-gpu')



def check_html(text,query,url):
    soup = BeautifulSoup(text, 'lxml')
    text = soup.get_text()
    if "unsupported browser" in text.lower():
        header["user-agent"] = unsupported_browser
        request_page = s.get(url,headers=header,timeout=20)
        return check_html(request_page.text,query,url)
        
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    out = '\n'.join(chunk for chunk in chunks if chunk)
    out = out.lower()
    if len(out) == 0:
        return "doubt",0
    count_occurance = (out.count(query.lower()))
    if count_occurance >0:
        return True,count_occurance
    else:
        if "javascript" in out or "robot" in out:  
            return "doubt",0

        return False,0
            
def get_text_html(input_data):
   
    url,query,title = input_data
    user_agent = random.choice(USER_AGENTS)
    header["user-agent"] = user_agent
    dictionary = {}
    dictionary["url"] = url
    dictionary["query"] = query
    dictionary["title"] = title

    try:

        request_page = s.get(url,headers=header,timeout=20)
        output,occu = check_html(request_page.text,query,url)
        print(output,occu)
        #request_page.html.render(timeout=8000)

    except Exception as err:
        output =  False


    if output != True:
        try:
            user_agent = random.choice(USER_AGENTS)
            options.add_argument('user-agent={}'.format(user_agent))
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ['enable-automation'])
            options.add_argument("--enable-javascript")
            

            driver = webdriver.Chrome(executable_path = 'chromedriver', options=options)
            driver.set_page_load_timeout(30)
            driver.get(url)
            time.sleep(10)
            output,occu = check_html(driver.page_source,query,url)
            if output != True:
                driver.close()
                dictionary["present"] = False
                dictionary["occurance"] = 0
                return dictionary
        except Exception as e:
            output,occu = check_html(driver.page_source,query,url)
            driver.close()
            
            if output == True:
                dictionary["present"] = True
                dictionary["occurance"] = occu
                return dictionary
            
            dictionary["present"] = False
            dictionary["occurance"] = 0 
            return dictionary
    dictionary["present"] = output
    dictionary["occurance"] = occu
    # print('dictionarydictionarydictionarydictionary')
    # print('dictionarydictionarydictionarydictionary')
    # print('dictionarydictionarydictionarydictionary')
    # print('dictionarydictionarydictionarydictionary')
    # print('dictionarydictionarydictionarydictionary')
    # print(dictionary)             
    return dictionary



'''
A function upload the local generated label pdf to aws s3 buket
:param filename str: local label pdf file path
.
.
.
:return str : url of uploaded file on s3

'''
def upload_to_aws(local_filename,file_name):
    
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        
        folder="scrappingResult/"
        
        s3.upload_file(local_filename,BUKET_NAME, folder+file_name)
        url=f"https://{BUKET_NAME}.s3.ap-south-1.amazonaws.com/{folder}{file_name}"
        return url
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def upload_images_on_aws(local_filename):
    
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        
        folder="scrappingImages/"
        
        s3.upload_file(local_filename,BUKET_NAME, folder+local_filename)
        url=f"https://{BUKET_NAME}.s3.ap-south-1.amazonaws.com/{folder}{local_filename}"
        return url
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def main_runner(queries,task):
    for query in queries:
        search = query.replace(' ', '+')
        results = 50
        url = (f"https://www.google.com/search?q={search}&num={results}")

        requests_results = requests.get(url)
        soup_link = BeautifulSoup(requests_results.content, "html.parser")
        links = soup_link.find_all("a")
        data = []
        stories_link = []
        for link in links:
            link_href = link.get('href')
            if "url?q=" in link_href and not "webcache" in link_href:
                title = link.find_all('h3')
                if len(title) > 0:
                    
                    dictionary = {}
                    link = (link.get('href').split("?q=")[1].split("&sa=U")[0])

                    if "youtube" in link:
                        link = link.replace("%3Fv%3D","?v=")

                    stories_link.append((link,query,title[0].getText()))
    threads = min(30, len(stories_link))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.map(get_text_html, stories_link)
    # future = get_text_html(stories_link[0])
    # print(future)
    df = pd.DataFrame.from_dict(list(future))
    folder="Temp/"
    filname="task-"+str(task)+'.csv'
    local_file_address=folder+filname
    df.to_csv (local_file_address, index = False, header=True)
    url=upload_to_aws(local_file_address,filname)
    return url


'''Function making dir '''
def make_dir(urls):
    t = 'temp'
    script = Downloading()
    
    if not os.path.exists(t):
        os.mkdir(t)
    
    folder_name = datetime.datetime.now().strftime("%d-%m-%Y %H_%M_%S")#%H_%M_%S-%Y_%m_%d
    folder_name = script.make_folder(t,folder_name)
    folders = []
    for k in range(1,len(urls)+1):
        names = 'image'+str(k)
        main_path = script.make_folder(folder_name,names)

        folders.append(main_path)
    for i in range(len(urls)):
        urls[i].append(folders[i])
    return urls

'''FUNCTION TO REMOVE DUPLICATE LINKS ''' 
def remove_same_href(dictionary):

    img0 = dictionary['img0']
    img1 = dictionary['img1']
    img2 = dictionary['img2']
    print()
    print(f"[images links get Image 1:{len(img0)} Image 2:{len(img1)} Image 3:{len(img2)}]")
    for key in img0:
        img1.pop(key, None)
        img2.pop(key,None)
    print("Removing Duplicate Links")
    time.sleep(0.3)
    print(f"[images links get Image 1:{len(img0)} Image 2:{len(img1)} Image 3:{len(img2)}]")
    dictionary['img0'] = img0
    dictionary['img1'] = img1
    dictionary['img2'] = img2
    data = []
    
    for key,value in dictionary.items():
        for key1,value1 in value.items():
            temp = []
            temp.append(key1)
            temp.append(value1)
            data.append(temp)
    
    return data

def csv_file(data,folder_name):
    dataframe  = {'Similar_imgs_links':[],'Similar_imgs_str':[],'Exact_imgs_links':[],'Exact_imgs_str':[]}
    for key ,value in data.items():
        for val in value:
            if key == 'Similar_images':
                dataframe['Similar_imgs_links'].append(val[0])
                dataframe['Similar_imgs_str'].append(val[1])
            else:
                dataframe['Exact_imgs_links'].append(val[0])
                dataframe['Exact_imgs_str'].append(val[1])

    df = pd.DataFrame.from_dict(dataframe, orient='index')
    df = df.transpose()
    
    df.to_csv(folder_name+'/data.csv', index=False) 
'''REFINE DATA FUNCTION'''

def refine_data(data,folder_name):
    
    exact_imgs = {}
    similar_imgs = {}
    main_data = {}
    
    for result in range(len(data)):
        img_name = 'img'+str(result)
        temp_similar_imgs,temp_exact_imgs = data[result]
        exact_imgs[img_name] = temp_exact_imgs
        similar_imgs[img_name] = temp_similar_imgs

    
    matches_imgs = remove_same_href(exact_imgs)
    similar_data = remove_same_href(similar_imgs)

    main_data['Similar_images'] = similar_data
    main_data['Exact'] = matches_imgs
    
    #store data into pickle
    with open(folder_name+'/data.pkl', 'wb') as handle:
        pickle.dump(main_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    #create csv file 
    csv_file(main_data,folder_name)
    url = upload_to_aws(folder_name+'/data.pkl','data.pkl')
    main_data['result_path']=url
    return main_data 


'''FUNCTION MAKE LIST INPUT IN THREAD'''
def argthread(threads,folder_name,img_path,urls):
    
    folders = ''
    url_list = []
    
    for i in range(1,threads+1):
        folders += str(i)
    #list to run thread with imgpath
    for url in urls:
        temp = []
        temp.extend([url,img_path,folder_name])
        url_list.append(temp)
    
    return url_list,folders

''' FUNCTION TO RUN SCRIPT ''' 
def script(urls_list):
    
    script  = Downloading()
    #unpack list
    img_array,urls,folder_name = urls_list
    
    #input args to thread
    threads = len(urls)
    url_list,folders = argthread(threads,folder_name,img_array,urls)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.map(script.google, url_list,folders)
    data = list(future) 
    #Refine Data
    main_data  = refine_data(data,folder_name)
    
    return main_data

def image_scrapper(urls):
    
    #mkdir
    urls_list = make_dir(urls)
    threads = len(urls_list)
    # urls_list = [[imge_path,folder_path,['googlelenslink','googlelenslink','googlelenslink']],[imge_path,folder_path,['googlelenslink','googlelenslink','googlelenslink']]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.map(script, urls_list)

    data = list(future)

    return data




# Open the image by specifying the image path.
def resolution(image_list):
    main_response=[]
    
    resoluion = [30,60]
    date=datetime.datetime.now().strftime("%H_%M_%S_%Y_%m_%d")
    folder_name ="Temp/uploads/users/"+date+"/"
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    count = 0
    for img in range(len(image_list)):
        inner_response=[]
        read = image_list[img]
        image_file = Image.open(read)
        name = Path(read).name.split('.')[0]
        
        # Path(read).suffix
        
        if image_file.mode in ("RGBA", "P"):
            image_file = image_file.convert("RGB")


        #making dir
        image_path = folder_name+str(count)+"/"
        if not os.path.exists(image_path):
            os.mkdir(image_path)

        #copy main image to dir
        copy_main_img = Path(read).name
        copy_path = os.path.join(image_path,copy_main_img)
        shutil.copyfile(read, copy_path) 
        data=cv2.imread(copy_path)
        main_image_link=upload_images_on_aws(copy_path)
        inner_response.append(data)
        link_array=[]
        main_link=f'https://lens.google.com/uploadbyurl?url={main_image_link}'
        link_array.append(main_link)
        for re in resoluion:
            
            new_name = f'{name}_'+str(re)+'.jpg'
            sav_path =image_path+new_name
            image_file.save(sav_path, quality=re)
            resp=upload_images_on_aws(sav_path)
            link=f'https://lens.google.com/uploadbyurl?url={resp}'
            link_array.append(link)
        inner_response.append(link_array)
        count+=1
        main_response.append(inner_response)
    return(main_response)