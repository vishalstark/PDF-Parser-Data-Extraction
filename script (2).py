FILE_NAME = 'Binder2.pdf'
PARSING_FILE_NAME = 'Parsing_parameters_2021-06-08a.csv'

# FILE_NAME = input('Enter file name: ')
# PARSING_FILE_NAME = input('Enter Parsing File Name : ')

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os
from pathlib import Path
import pandas as pd
import time

currentdir =os.getcwd()

options = webdriver.ChromeOptions() 

prefs = {"download.default_directory" : "%s"%currentdir}

options.add_experimental_option("prefs",prefs)

options.add_argument("--no-sandbox")

options.add_argument("--headless")     

#chrome_options.add_argument("--disable-setuid-sandbox")

options.add_argument("--disable-dev-shm-usage")

#chrome_options.add_argument('--disable-features=VizDisplayCompositor')

driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)

driver.get("https://www.aconvert.com/pdf/pdf-to-csv/")

file_path = currentdir+'\\'+FILE_NAME

driver.find_element(By.ID, "file").send_keys(file_path)

driver.find_element(By.ID, "submitbtn").click()

WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[@id='tr1']/td[2]/a")))

file_name = driver.find_element(By.XPATH, "//*[@id='tr1']/td[2]/a").text

driver.find_element(By.XPATH, "//*[@id='tr1']/td[2]/a").click()

time.sleep(5)

df = pd.read_csv(file_name,header=None,usecols=[0],skip_blank_lines=True)
df.dropna(axis=0,inplace=True)
df=df.reset_index()
df.drop(columns=['index'],inplace=True)

df_final = pd.DataFrame()

params = pd.read_csv(PARSING_FILE_NAME,usecols=['Field Name'])
col_names = params['Field Name'].values.tolist()
ccol_names=col_names
ccol_names.append('Zoning:')
ccol_names.append('Owner Occupied:')

d = {}

def incenerate():
    os.remove(file_name)

def process_text(string):
    global d
    col_names = ccol_names
    col_names = col_names[1:]
    covered = []
    pos = []
    for i in col_names:
        temp_pos = string.find(i)
        if temp_pos!=-1:
            pos.append(temp_pos)
            pos.append(temp_pos+len(i))
            d[i] = ''
            covered.append(i)
    pos.append(len(string))
    j=1
    for i in covered:
        d[i] = string[pos[j]:pos[j+1]]
        d[i] = d[i].strip(' ')
        j+=2

def process_pdf():
    
    global d
    global df_final
    
    flg=0
    for i in df[0]:
        if 'Page' in i:
            df_final = df_final.append(d, ignore_index=True)
            d={}
            flg=0
        else:
            if flg==0:
                d['Address'] = i
                flg=1
            process_text(i)

    df_final = df_final.astype(str)

    df_final.applymap(str.strip)

    df_final = df_final[ccol_names]

    df_final.drop(columns=['Zoning:','Owner Occupied:'],inplace=True)

    final_pdf_name = Path(FILE_NAME).stem
    
    df_final.to_csv(f'{final_pdf_name}.csv')

    print(f'Data Saved in {final_pdf_name}.csv')
    
    incenerate()

if __name__ == '__main__':
    process_pdf()

