# This script downloads PUMD diary files from an arbitrary year from the BLS website. It extracts the .csv from the .zip, returns a list of unique values from certain columns, and then resaves the .csv file as a new .zip file.

# Set the year to search for in the last cell of the notebook, and then pass that into the search_bls() function

import pandas as pd 
import os
import requests
import re
from zipfile import ZipFile
from bs4 import BeautifulSoup

def download_file(file_url, file_name):
    """ Downloads selected zip file from BLS 

        Keyword Arguments:
        file_url -- URL of file to download
        file_name -- name of downloaded file

        Returns:
        zip_file_path -- path to downloaded zip file

     """
    r = requests.get(file_url)

    if r.status_code == 200:
        print(f'Downloading file: {file_name} ')
        with open(file_name, "wb") as zip:
            zip.write(r.content)

        if os.path.isfile(file_name):
            print(f'Success! File downloaded: {file_name}.')
            zip_file_path = file_name
        else:
            print(f'Error! File not downloaded: {file_name}.')
            zip_file_path = ''
    else:
        print(f'Error. Invalid URL/file: {file_url}.')
        zip_file_path = ''

    return zip_file_path

def extract_csv(zip_file_path):
    """ Extracts specific csv file from zip_file 

        Keyword Arguments:
        zip_file -- name of zip archive

        Returns:
        expd_file_path - text string of csv path & filename

     """
    # list to hold all expd... files
    expd_list = []

    # check if zip_file_path isn't empty and if it exists in PWD
    if zip_file_path != '' and os.path.isfile(zip_file_path): 

        with ZipFile(zip_file_path, 'r') as zip:
            # loop through all members of the archive
            for filemember in zip.namelist():
                # if expd is in the file name, then applend that name to the expd list
                if 'expd' in filemember:
                    expd_list.append(filemember)
            #sort expd_list in ascending order, just in case the .zip file wasn't saved in ascending order 
            expd_list.sort()

            #get first file from list
            first_expd_file = expd_list[0] 

            # extract to PWD
            zip.extract(first_expd_file)

        if os.path.isfile(first_expd_file):
            print(f'Success: File Extracted: {first_expd_file}')
            expd_file_path = first_expd_file
        else:
            print(f'Error in Extraction. {first_expd_file} not extracted.')
            expd_file_path = ''
    else:
        print(f'Error in Extraction. {zip_file_path} not available.')
    
    #return textstring of extractedfile  
    return expd_file_path




def analyze_csv(csv_file_path):
    """ analyze csv file in  csv_file_path

        Keyword Arguments:
        csv_file_path -- file path to csv file to analyze
     """

    # check if csv_file_path isn't empty and if it exists in PWD
    if csv_file_path != '' and os.path.isfile(csv_file_path): 

        # begin analyis
        df = pd.read_csv(csv_file_path)
        unique_ids = list(df['NEWID'].unique())

        # report analysis
        print('Analysis Complete')
        print(f'There are {len(unique_ids)} unique ids in {csv_file_path}. They are:')
        print(unique_ids)

    else:
        print(f'Error analyzing CSV. {csv_file_path} not available.')


def save_new_zip(csv_file_path):
    """ saves new zip archive from file in csvfile_path

        Keyword Arguments:
        csv_file_path -- file path to csv file
     """
    
    # check if csv_file_path isn't empty and if it exists in PWD
    if csv_file_path != '' and os.path.isfile(csv_file_path): 
        # make new file name by removing path reference from csv_file_path
        pos_last_slash = csv_file_path.rfind('/') + 1
        new_file_name = csv_file_path[pos_last_slash:] + '.zip'

        # create new zip archive
        with ZipFile(new_file_name,'w') as zip:
            zip.write(csv_file_path)
        
        # test for successful file creation
        if os.path.isfile(new_file_name):
            print(f'Success: CSV saved to new zip archive: {new_file_name}')
        else:
            print(f'Error creating new archive. {new_file_name} created.')
    
    else:
        print(f'Error creating new archive. {csv_file_path} not available.')

        
        
def search_bls(year):
    """ searches the BLS for PUMD Diary files for the Year that is passed into the function 

        Keyword Arguments:
        year -- The year to search for 
     """

    # alert user that we're starting the scrape
    print('Starting scrape...')

    #  set url variables for bls site and PUMD html page
    bls_base_url = 'https://www.bls.gov'
    pumd_url = bls_base_url + '/cex/pumd_data.htm'

    # try to scrape BLS pumd page
    r = requests.get(pumd_url)

    if r.status_code == 200:

        #get soup object to scrape page
        soup = BeautifulSoup(r.content, 'lxml')

        #  diary links in csv format all take this form: '/cex/pumd/data/comma/diaryYY.zip'
        #  so we parse the year argument and create a file to look for, and then create a test_url to find the file on the page. 
        zip_file = 'diary' + str(year)[2:4] + '.zip'
        test_url =  '/cex/pumd/data/comma/' + zip_file

        diary_link = soup.find(href=test_url)
        #  if we find an available link, we download the zip and extract it. 
        if(diary_link):
            download_link = bls_base_url + diary_link['href']
            zip_file_path = download_file(download_link,zip_file)
            csv_to_analyze = extract_csv(zip_file_path)
            analyze_csv(csv_to_analyze)
            save_new_zip(csv_to_analyze)

        #  if link isn't found, report to the user that the selected year is not available. 
        else:
            print(f'PUMD Diary for {year} is not available')

    #  if pumd_url isn't valid, report to the user that the pumd_url is not available. 
    else:
        print(f'Error! {pumd_url} not valid.')

# Set the Year variable in this cell, and run the search_bls function from here with the selected year. 

year = 2010

search_bls(year)



