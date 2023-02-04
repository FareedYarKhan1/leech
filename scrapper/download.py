import requests
import time
import os
import base64
import cv2
import shutil
import sys
import numpy as np

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
    
    '''Function is to mkdir'''
    def make_folder(self,folder_name,folders):

        path = os.path.join(folder_name,folders)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

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
        
        time.sleep(5)
        browser.refresh()
        #intialize wait time
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
            
            link = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'WpHeLc'))).get_attribute('href')
        except:
            print('ROBOT reCAPTCHA  !!!!!!!')
            sys.exit() 
        

        # get all href links of similar page images   
        href = browser.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "xuQ19b", " " ))]')
        #XPATH OF SIDE BAR IMAGE SECTION    
        element = browser.find_element(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "jXKZBd", " " ))]')
            
            
        similar_imgs = {}
        count = 0
        
        
        # Scroll down
        print("[%] Scrolling down.")
        verical_ordinate = 100
        for i in range(30):
            browser.execute_script("arguments[0].scrollTop = arguments[1]", element, verical_ordinate)
            verical_ordinate += 100
            time.sleep(0.3)  # bot id protection
        
    
        for i in range(10):
            browser.execute_script("arguments[0].scrollTop = arguments[1]", element, verical_ordinate)
            verical_ordinate += 100
            time.sleep(0.3)  # bot id protection
        
        
    
        for i,x in enumerate(href):
            
            href = x.find_element(By.CSS_SELECTOR,'a.GZrdsf').get_attribute('href')
            src = x.find_element(By.CSS_SELECTOR,'img.wETe9b').get_attribute('src')
            
            
            if href != None and src != None:
                #break loop when limit is cross
                count+=1
                if count > self.limit:
                    break
                try:
                    
                    image_bytes = requests.get(src).content
                    
                    try:
                        image_bytes = str(image_bytes, 'utf-8')
                    
                    except UnicodeDecodeError:

                        #downloading and convert in base64str images
                        download_img,saving_path,b64_string,decoded =  self.beautifull_soup(image_bytes,folder_name,'similar_images',i)
                        
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
                            
                            similar_imgs[href] = b64_string
                    except:
                        pass
                    
                except:
                    pass

            
            

        return similar_imgs,link


    '''FUNCTION TO SCRAPE AND DOWNLOAD EXACT IMAGES''' 
    def exact_images(self,browser):
        
        matches_folder_temp = ''
        href = None
        
        
        #get img button link to click for exact image page
        wait = WebDriverWait(browser, self.wait)
        try:
        
            img_button = wait.until(EC.visibility_of_element_located((By.ID, 'Z6bGOb')))
        except:
            print('ROBOT CAPTHA !!!!!!!')
            sys.exit()
        # time.sleep(5)
        # img_button = browser.find_element(By.ID,'Z6bGOb')
        try:
            href = img_button.find_element(By.CSS_SELECTOR,'a').get_attribute('href')
        except:
            pass

        exact_imgs = {}
        if href is not None:
            img_button.click()
            
            element = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
            # time.sleep(5)
            # element = browser.find_element(By.TAG_NAME, "body")
            
            
            
            # Scroll down
            print("[%] Scrolling down.")
            for i in range(30):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)  # bot id protection

            for i in range(10):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)  # bot id protection
            print("[%] Reached end of Page.")
            
            time.sleep(5)
            href = browser.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "BUooTd", " " ))]')
            count = 0

            for i,x in enumerate(href):
                src = x.find_element(By.CSS_SELECTOR,'img.Q4LuWd').get_attribute('src')
                href = x.find_element(By.CSS_SELECTOR,'a.VFACy').get_attribute('href')
               
                if href != None and src != None:
                    if 'https' in src:
                        image = src
                        
                        r = requests.get(image).content
                        
                        try:
                           
                            r = str(r, 'utf-8')
                            
                        except UnicodeDecodeError:
                            #convert bytes into base64 string
                            b64_string = base64.b64encode(r).decode("utf-8")
                            

                    else:

                        #split base64 link into string if src is not encrypted
                        b64_string =src.split(',')[1]
                        
                    print(f"[%] Exact images image{i+1}.jpg")
                    exact_imgs[href] = b64_string
                    # count+=1
                    # if count > len(href):
                    #     break
        else:
            
            print('Exact Images not found')
        
        #delete exact image folder 
        if os.path.exists(matches_folder_temp):
            shutil.rmtree(matches_folder_temp)

        return exact_imgs


    def google(self,url_list,folders):
        
        #UNPACK ARGS
        url,img_array,folder_name = url_list

        img_path = self.make_folder(folder_name,folders)
    
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.set_window_size(1024, 768)
       
        

        #similar images funtions
        browser.get(url)

        
        temp_similar_imgs,link = self.similar_images(browser,img_array,img_path)

        #Match images funtions
        print("[%] Successfully opened link Exact Images.")
        browser.get(link)
        temp_exact_imgs = self.exact_images(browser)
        browser.close()
        print("[%] Closed ChromeDriver.")

        return temp_similar_imgs,temp_exact_imgs