import requests
import time
import os
import base64
import cv2
import sys
import numpy as np
import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



class Downloading():
    
    def __init__(self):
       
        #matching threashold
        self.thresh = 800
        #intialize wait time
        self.wait = 10
        #limit how many you want ot download similar images
        self.limit = 20
        #max num of pages appear on google page
        self.limit_of_pages = 50
        
    '''Function is to mkdir'''
    def make_folder(self,folder_name,folders):

        path = os.path.join(folder_name,folders)
        if not os.path.exists(path):
            os.mkdir(path)
        return path
    def download_images(self,b64_string,folder_name):
        name = datetime.datetime.now()
        download_img = f"images{name}.jpg"
        sav = os.path.join(folder_name,download_img)
        print(download_img)
        # img_data = b64_string.encode()
        # content = base64.b64decode(img_data)
        # with open(sav, "wb") as fh:
        #     fh.write(content)

    '''Function is to download and convert base64 str '''
    def beautifull_soup(self,image_bytes,folder_name,func_folder,i):


        download_img = f"images{i+1}.jpg"
        similar_images_folder = self.make_folder(folder_name,func_folder)
        saving_path = f"{similar_images_folder}/{download_img}"
        
        #saving image to dir
        with open(saving_path, "wb+") as f:
            f.write(image_bytes)
        
        #read and convert into base64
        with open(saving_path, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read())
        ##bytes into numpy array
        img_array = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)
     
        return download_img,saving_path,b64_string,img_array

    '''Function is to match 2 images '''
    def features_matching(self,target_img,img2):

        # img1 = cv2.imread(target_img)
        img1 = target_img  
        img2 = img2
        h  , w , c = img2.shape
        dim = (w,h)
        img1 = cv2.resize(img1, dim, interpolation = cv2.INTER_AREA)
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        #sift
        sift = cv2.SIFT_create()

        keypoints_1, descriptors_1 = sift.detectAndCompute(img1,None)
        keypoints_2, descriptors_2 = sift.detectAndCompute(img2,None)
        #feature matching
        bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

        matches = bf.match(descriptors_1,descriptors_2)
        matches = sorted(matches, key = lambda x:x.distance)
        

        return matches

    '''FUNCTION TO SCRAPE AND DOWNLOAD SIMILAR IMAGES'''  
    def similar_images(self,browser,img_array,folder_name):

        similar_imgs = {}
        count = 0
        #intialize wait time
        # time.sleep(5)
        # browser.refresh()
        wait = WebDriverWait(browser, self.wait)
        
        #check lens links are expire or not
        try:
            expire_links = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'b0I81c'))).text
            if 'expired' in expire_links:
                print('LINKS OF IMAGES ARE EXPIRE TRY AGAIN WITH NEW LINKS')
                sys.exit()
        except:
            pass

        #get to find source button link
        try:
            # time.sleep(5)
            # link = browser.find_element(By.CLASS_NAME,'WpHeLc').get_attribute('href')
            find_source_link = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'WpHeLc'))).get_attribute('href')
        except:
            print('ROBOT reCAPTCHA  !!!!!!!')
            sys.exit() 
        

        # get all href links of similar page images   
        href = browser.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "xuQ19b", " " ))]')
        
        
        #XPATH OF SIDE BAR IMAGE SECTION
        try:
            element = browser.find_element(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "b57KQc", " " ))]')
        
            # Scroll down
            print("[%] Scrolling down.")
            verical_ordinate = 100
            for i in range(self.limit):
                browser.execute_script("arguments[0].scrollTop = arguments[1]", element, verical_ordinate)
                verical_ordinate += 100
                time.sleep(0.3)  # bot id protection
            
        
            for i in range(self.limit):
                browser.execute_script("arguments[0].scrollTop = arguments[1]", element, verical_ordinate)
                verical_ordinate += 100
                time.sleep(0.3)  # bot id protection
        except:
            print('SIDE BAR CSS SELECTOR IS UPDATED YOU HAVE TO UPDATE XPATH')
        
    
        for i,x in enumerate(href):
            temp_similar_img = []
            href = x.find_element(By.CSS_SELECTOR,'a.GZrdsf').get_attribute('href')
            src = x.find_element(By.CSS_SELECTOR,'img.wETe9b').get_attribute('src')
            
            
            if href != None and src != None:
                #break loop when limit is cross
                
                try:
                    
                    image_bytes = requests.get(src).content
                    
                    try:
                        image_bytes = str(image_bytes, 'utf-8')
                    
                    except UnicodeDecodeError:

                        #downloading and convert in base64str images
                        download_img,saving_path,b64_string,decoded =  self.beautifull_soup(image_bytes,folder_name,'similar_images',i)
                        count+=1
                        if count > self.limit:
                            break
                        #Features Macthing
                        target_img = img_array 
                        img2 = cv2.imread(saving_path)
                        # img2 = decoded
                        matches = self.features_matching(target_img,img2)

                        total = 0 
                    try:
                        avrg = min(50,len(matches))
                        
                        for i in range(avrg):
                            total = total + (matches[i].distance)
                        print(f"[%]Similar images {download_img} [%]Matches Average {(total/avrg)}")
                        
                        #threshhold to match image
                        if (total/avrg) < self.thresh:
                            
                            print("match")
                            most_similar = self.make_folder(folder_name,'most_similar')
                            sav = f"{most_similar}/{download_img}"
                            cv2.imwrite(sav,img2)
        
                            similar_imgs[href] = 'b64_string'
                    except:
                        pass
                    
                except:
                    pass
       
        
        return similar_imgs,find_source_link


    '''FUNCTION TO SCRAPE AND DOWNLOAD EXACT IMAGES AND SIDE LINKS IMAGES'''
    def scrape_images(self,wait,browser,xpath_element,img_src,img_href,page_limit):
        
        exact_imgs = {}
        folder_name = 'ok'
        
        page_down_limit = 5
        if page_limit:
            page_down_limit = 50
        
        side_link_element = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
        
        # Scroll down
        print("[%] Scrolling down.")
    
        for i in range(page_down_limit):
            side_link_element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)  # bot id protection

        # for i in range(page_down_limit):
        #     side_link_element.send_keys(Keys.PAGE_DOWN)
        #     time.sleep(0.3)  # bot id protection
        try:
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "mye4qd", " " ))]'))).click()
            for i in range(15):
                side_link_element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)  # bot id protection
        except:
            pass
        print("[%] Reached end of Page.")

        xpath = browser.find_elements(By.XPATH, xpath_element)
        for no,xpath in enumerate(xpath):
            side_img_src = xpath.find_element(By.CSS_SELECTOR,img_src).get_attribute('src')
            side_img_href = xpath.find_element(By.CSS_SELECTOR,img_href).get_attribute('href')

            
            if side_img_href and side_img_src:

                #encrypted links
                if 'https' in side_img_src:
                    image = side_img_src
                    
                    image_bytes = requests.get(image).content
                    
                    try:
                        
                        image_bytes = str(image_bytes, 'utf-8')
                        
                    except UnicodeDecodeError:

                        #convert bytes into base64 string
                        b64_string = base64.b64encode(image_bytes).decode("utf-8")
                        self.download_images(b64_string,folder_name)
                #split base64 link into string if src is not encrypted
                else:
                    b64_string = side_img_src.split(',')[1]
                    self.download_images('b64_string',folder_name)
                    
                    

             
                exact_imgs[side_img_href] = 'b64_string'
      
        return  exact_imgs
    
    def exact_images(self,browser,exact_imgs_run):
        
        exact_imgs = {}
        side_imgs  = {}

        if exact_imgs_run:
            
            href = None
            #get img button link to click for exact image page
            wait = WebDriverWait(browser, self.wait)
            try:
            
                img_button = wait.until(EC.visibility_of_element_located((By.ID, 'Z6bGOb')))
            
            except:
                print('ROBOT CAPTHA !!!!!!!')
                sys.exit()

            try:
                href = img_button.find_element(By.CSS_SELECTOR,'a').get_attribute('href')
            
            except:
                pass

        
            if href is not None:
                img_button.click()
                xpath_element = '//*[contains(concat( " ", @class, " " ), concat( " ", "BUooTd", " " ))]'
                img_src = 'img.Q4LuWd'
                img_href = 'a.VFACy'
                exact_imgs = self.scrape_images(wait,browser,xpath_element,img_src,img_href,True)
            else:
                print('EXACT IMAGES NOT AVAILABLE')
            return exact_imgs
        
        else:
            
            wait = WebDriverWait(browser, self.wait)
            # Exact image butoon and open new window of chrome
            xpath_element = '//*[contains(concat( " ", @class, " " ), concat( " ", "Sth6v", " " ))]'
            img_src = 'img'
            img_href = 'a'
            side_imgs = self.scrape_images(wait,browser,xpath_element,img_src,img_href,False)
            
            return side_imgs
    
    '''FUNCTION TO SCRAPE AND DOWNLOAD SIDE IMAGES'''
    def side_links(self,find_source_link):
        
        #chrome window
        side_link_imgs = {}
        chrome_options = Options()
        # side_link_imgs = ''
        # chrome_options.add_argument("--headless")
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.set_window_size(1024, 768)
        browser.get(find_source_link)
        wait = WebDriverWait(browser, self.wait)
        #button to jump next page
        
        # side_link_imgs = []
        for _ in range(self.limit_of_pages):
            #button to jump on next page
            try:
                next_page = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#pnnext')))
            except:
                next_page = None
            #scrape all images and links on current page
            temp_side_link_imgs = self.exact_images(browser,False)
            side_link_imgs |= temp_side_link_imgs
            
            
            if next_page:
                next_page.click()    
            else:
                break

        return side_link_imgs
    
    def google(self,url_list,folders):
        
        temp_side_link_imgs = {}
        temp_similar_imgs = {}
        temp_exact_imgs = {}
        #UNPACK ARGS
        url,img_array,folder_name = url_list

        img_path = self.make_folder(folder_name,folders)
    
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.set_window_size(1024, 768)
        
        #Similar images funtions
        print("[%] Successfully launched Script")
        browser.get(url)
        temp_similar_imgs,find_source_link = self.similar_images(browser,img_array,img_path)

        #Match images funtions
        # find_source_link = 'https://www.google.com/search?tbs=sbi:AMhZZitkmNSC28pBupJjbejR3h5MqICvq7SPhEDUrYzTqrKIRQo2yPHrqrXKgivxPGkd14-pZX9lS5EF62mwDSgDdTKx7adbbrKpDcgBDQcEMtHzgUwUUrTfvxY66ImLWXxwhiD2kcEvlg8fUJT6u6NxOWLgPWqi-A'
        # browser.get(find_source_link)
        # temp_exact_imgs = self.exact_images(browser,True)
        
        # time.sleep(5)
        # print("[%] Successfully opened link Side Images.")
        # find_source_link = 'https://www.google.com/search?tbs=sbi:AMhZZiuq8l-IOV8l3zDmK-2TeN4nqKjSubGI4130fBVDM9thuZw8g9BXPcTTHU17v1vi8sGTwUnPlZDd_18zjSjHshukRb0NpRppVdsVtDMm9X3Z5XXBhbJoXGaSCbgzXMplX3NLONg8kSM2IN3UaIJW0GecnFAlfYQ'
        # temp_side_link_imgs = self.side_links(find_source_link)
        
        browser.close()
        print("[%] Closed.")
        
        return temp_similar_imgs, temp_exact_imgs, temp_side_link_imgs
