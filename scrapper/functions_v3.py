import cv2
import pandas as pd
import os
import time
from bs4 import *
import concurrent.futures
from .download import Downloading
from difflib import SequenceMatcher
from w3lib.url import canonicalize_url
from urllib.parse import urlparse 

from .functions_v2 import send_first_notice,send_created_temp_csv,send_normal_notice



scrape = Downloading()

'''Function making dir '''
def make_dir(urls,task_pk):
    
    t = 'Temp'
    if not os.path.exists(t):
        os.mkdir(t)
    #it will be task no. or image name or
    #folder_name  = datetime.datetime.now().strftime('%H_%M_%S-%Y_%m_%d')  
    folder_name = f'task-{task_pk}'
    folder_name = scrape.make_folder(t,folder_name)
    
    #mk image folder
    folders = []
    for k in range(1,len(urls)+1):
        names = 'image'+str(k)
        main_path = scrape.make_folder(folder_name,names)
        folders.append(main_path)
    #append dir in urls list
    for i in range(len(urls)):
        urls[i].append(folders[i])
    
    return urls

'''FUNCTION TO REMOVE DUPLICATE LINKS ''' 
def remove_duplicate_href(dictionary):

    img0 = dictionary['img0']
    img1 = dictionary['img1']
    img2 = dictionary['img2']
    
    print()
    print(f"[images links get Image 1:{len(img0)} Image 2:{len(img1)} Image 3:{len(img2)}]")
  
    for key in img0:
        img1.pop(key, None)
        img2.pop(key,None)
      
    time.sleep(0.3)
    print(f"[Removing Duplicate Links Image 1:{len(img0)} Image 2:{len(img1)} Image 3:{len(img2)}]")
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

'''CREATE CSV FILE'''
#append_new_links into data.csv
def append_new_links(main_csv,temp_csv):
    df2 = pd.read_csv(temp_csv)
    df2.to_csv(main_csv,mode='a', index=False, header=False)
    #del temp.csv
    if os.path.exists(temp_csv):
        os.remove(temp_csv)
    else:
        pass

def compare_urls(url1, url2):
    
    url1 = canonicalize_url(url1)
    url2 = canonicalize_url(url2)
    url1_parsed = urlparse(url1)
    url2_parsed = urlparse(url2)

    domain = SequenceMatcher(None, url1_parsed.netloc, url2_parsed.netloc).ratio()
    path = SequenceMatcher(None, url1_parsed.path, url2_parsed.path).ratio()
    
    return domain,path

def compare(data,temp):
    
    data_links = data.values.tolist()
    temp_links = temp.values.tolist()
    
    for data_l in data_links:
        for temp_l in temp_links:
            # get percentage of domain name and path string
            domain_scr,path_scr = compare_urls(data_l[0],temp_l[0])
            if domain_scr > 0.85:
                if path_scr >= 0.65:
                    print(data_l[0],temp_l[0])
                    #find index of an element
                    index_num = temp_links.index(temp_l)
                    # Delete element in list
                    del temp_links[index_num]
    df = pd.DataFrame(temp_links, columns =['urls', 'type','base64str'])
    return df
#Check new links
def check_new_links(folder_name,df,task_pk):
    #first time run
    if not os.path.exists(folder_name+'/data.csv'):
       
        data_csv_address=folder_name+'/data.csv'
        data_first_notice_addrees=folder_name+'/first_notice.csv'
        temp_csv_addrees=folder_name+'/temp.csv'
        
        df.to_csv(data_csv_address, index=False)
        df.to_csv(data_first_notice_addrees, index=False)
        
        total_links=len(df)
        send_first_notice(data_csv_address,temp_csv_addrees,task_pk,total_links)
    else:
        #compare with old links with current links
        main_data = pd.read_csv(folder_name+'/data.csv')
        new_links_data = df[~df['urls'].isin(main_data['urls'])].dropna()

        if len(new_links_data):
            # Remove similar links
            new_links_data_2 = compare(main_data,new_links_data)
            if len(new_links_data_2):

                if not os.path.exists(folder_name+'/temp.csv'):
                    
                    temp_csv_address=folder_name+'/temp.csv'
                    new_links_data_2.to_csv(temp_csv_address, index=False)
                    total_links=len(new_links_data_2)
                    send_created_temp_csv(temp_csv_address,task_pk,total_links)
                
                else:
                    temp_csv_data = pd.read_csv(folder_name+'/temp.csv')
                    df3 = new_links_data_2[~new_links_data_2['urls'].isin(temp_csv_data['urls'])].dropna()
                    
                    if len(df3):
                        # Remove similar links
                        df3_2 = compare(temp_csv_data,df3)
                        print("df3 running")
                        if len(df3_2):
                            print("df3_2 running")
                            temp_csv_address=folder_name+'/temp.csv'
                            df3_2.to_csv(temp_csv_address, mode='a', index=False, header=False)
                            total_links=len(df3)
                            send_normal_notice(temp_csv_address,task_pk,total_links)

def csv_file(data,folder_name,task_pk):

    #columns
    dataframe  = {'urls':[],'type':[],'base64str':[]}
    for key ,value in data.items():
        for val in value:
            dataframe['urls'].append(str(val[0]))
            dataframe['base64str'].append(val[1])
            dataframe['type'].append(key)
    
    #dump dictionary in file
    df = pd.DataFrame.from_dict(dataframe)
    #check new links found or not
    check_new_links(folder_name,df,task_pk)

'''REFINE DATA FUNCTION'''
def refine_data(data,folder_name,task_pk):
    
    exact_imgs = {}
    similar_imgs = {}
    side_imgs = {}
    main_data = {}
    
    for result in range(len(data)):
        
        img_name = 'img'+str(result)
        temp_similar_imgs,temp_exact_imgs,temp_side_link_imgs= data[result]
        
        #store into dictionary
        exact_imgs[img_name] = temp_exact_imgs
        similar_imgs[img_name] = temp_similar_imgs
        side_imgs[img_name] = temp_side_link_imgs

    matches_imgs = remove_duplicate_href(exact_imgs)
    similar_data = remove_duplicate_href(similar_imgs)
    side_data    = remove_duplicate_href(side_imgs)

    main_data['Similar_images'] = similar_data
    main_data['Exact'] = matches_imgs
    main_data['Side_imgs'] = side_data
    
    print(main_data)
    #Store in csv file 
    csv_file(main_data,folder_name,task_pk)
    
    return main_data 


'''FUNCTION MAKE INPUT FOR THREAD'''
def arg_thread(threads,folder_name,img_path,urls):
    
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
def script(urls_list,task_pk):
    

    #unpack list
    img_array,urls,folder_name = urls_list
    
    #input args to thread
    threads = len(urls)
    url_list,folders = arg_thread(threads,folder_name,img_array,urls)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.map(scrape.google, url_list,folders)
    data = list(future) 
    
    #Refine Data and removing suplicate links
    main_data  = refine_data(data,folder_name,task_pk)
    
    return main_data

def main(urls,task_pk):
    task_pk_global=[task_pk]
    #mkdir and arguments
    urls_list = make_dir(urls,task_pk)
    threads = len(urls_list)

    # input 
    # urls_list = [[imge_path,folder_path,['googlelenslink','googlelenslink','googlelenslink']],[imge_path,folder_path,['googlelenslink','googlelenslink','googlelenslink']]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.map(script, urls_list,task_pk_global)

    data = list(future)

    return data


    
