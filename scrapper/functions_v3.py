import cv2
import pandas as pd
import os
import time,datetime
import pickle
from bs4 import *
import concurrent.futures

from .download import Downloading 
from .functions import upload_to_aws
scrape = Downloading()
response_urls=[]
'''Function making dir '''
def make_dir(urls):
    
    t = 'temp'
    if not os.path.exists(t):
        os.mkdir(t)
    
    folder_name = datetime.datetime.now().strftime("%d-%m-%Y %H_%M_%S")#%H_%M_%S-%Y_%m_%d
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
     
     
    for key in img0:
        img1.pop(key, None)
        img2.pop(key,None)
    time.sleep(0.3)
     
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
def csv_file(data,folder_name):

    #columns
    dataframe  = {'Similar_imgs_links':[],'Similar_imgs_str':[],'Exact_imgs_links':[],'Exact_imgs_str':[]}

    for key ,value in data.items():
        for val in value:
            if key == 'Similar_images':
                dataframe['Similar_imgs_links'].append(val[0])
                dataframe['Similar_imgs_str'].append(val[1])
            else:
                dataframe['Exact_imgs_links'].append(val[0])
                dataframe['Exact_imgs_str'].append(val[1])
    
    #dump dictionary in file
    df = pd.DataFrame.from_dict(dataframe, orient='index')
    df = df.transpose()
    data_name = datetime.datetime.now().strftime("%H_%M_%S")+".csv"
    df.to_csv(folder_name+'/'+data_name, index=False) 
    return [folder_name+'/'+data_name,data_name]
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

    
    matches_imgs = remove_duplicate_href(exact_imgs)
    similar_data = remove_duplicate_href(similar_imgs)

    main_data['Similar_images'] = similar_data
    main_data['Exact'] = matches_imgs
    
    #store data into pickle
    data_name = datetime.datetime.now().strftime("%H_%M_%S")+".pkl"
    with open(folder_name+'/'+data_name, 'wb') as handle:
        pickle.dump(main_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    #create csv file
    data_name = datetime.datetime.now().strftime("%H_%M_%S")+".pkl"
    csv_response=csv_file(main_data,folder_name) 
    csv_url=upload_to_aws(csv_response[0],csv_response[1])
    pkl_url = upload_to_aws(folder_name+'/'+data_name,data_name)
    response_urls.append(csv_url)
    response_urls.append(pkl_url)
    main_data['urls']=response_urls
    
    
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
def script(urls_list):
    
    scrape  = Downloading()
    #unpack list
    img_array,urls,folder_name = urls_list
    
    #input args to thread
    threads = len(urls)
    url_list,folders = arg_thread(threads,folder_name,img_array,urls)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.map(scrape.google, url_list,folders)
    data = list(future) 
    #Refine Data
    main_data  = refine_data(data,folder_name)
    
    return main_data

def main(urls):
    
    #mkdir and arguments
    urls_list = make_dir(urls)
    threads = len(urls_list)

    # input 
    # urls_list = [[imge_path,folder_path,['googlelenslink','googlelenslink','googlelenslink']],[imge_path,folder_path,['googlelenslink','googlelenslink','googlelenslink']]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.map(script, urls_list)

    data = list(future)
    
    return data

