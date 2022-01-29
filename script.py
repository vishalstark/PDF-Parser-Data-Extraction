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
import sys, getopt

FILE_NAME = ''
PARSING_FILE_NAME = ''
final_pdf_name = ''

file_name = ''
currentdir = os.getcwd()

df = pd.DataFrame()
df_final = pd.DataFrame()

all_col_names = []
req_col_names = []

d = {}

def main(argv):
    
    global FILE_NAME
    global final_pdf_name
    global PARSING_FILE_NAME

    try:
        opts, args = getopt.getopt(argv,"hi:o:p:",["ifile=","ofile=","pfile="])
    except getopt.GetoptError:
        print('scripy.py -i <inputfile> -o <outputfile> -p <paramfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile> -p <param_file>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            FILE_NAME = arg
        elif opt in ("-o", "--ofile"):
            final_pdf_name = arg
        elif opt in ("-p", "--pfile"):
            PARSING_FILE_NAME = arg

def getConv():

    global currentdir
    global file_name
    global FILE_NAME

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


def init():

    global file_name
    global req_col_names
    global all_col_names
    global df
    global PARSING_FILE_NAME

    params = pd.read_csv(PARSING_FILE_NAME,usecols=['Field Name'])
    req_col_names = params['Field Name'].values.tolist()
    all_col_names=req_col_names
    all_col_names.append('Zoning:')
    all_col_names.append('Owner Occupied:')

    
    df = pd.read_csv(file_name,header=None,usecols=[0],skip_blank_lines=True)
    df.dropna(axis=0,inplace=True)
    df = df.reset_index()
    df.drop(columns=['index'],inplace=True)

def incenerate():
    global file_name
    os.remove(file_name)

def process_text(string):
    global d
    req_col_names = all_col_names
    req_col_names = all_col_names[1:]
    covered = []
    pos = []
    for i in req_col_names:
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
    global final_pdf_name
    global df
    
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

    df_final = df_final[all_col_names]

    df_final.drop(columns=['Zoning:','Owner Occupied:'],inplace=True)

    df_final.to_csv(f'{final_pdf_name}')

    print(f'Data Saved in {final_pdf_name}')
    
    incenerate()

if __name__ == '__main__':
    main(sys.argv[1:])
    getConv()
    init()
    process_pdf()

