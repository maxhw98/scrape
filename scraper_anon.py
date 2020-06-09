import urllib.request
from selenium import webdriver
import time
import pandas as pd
import numpy as np
import re
import pygsheets
from datetime import datetime

def get_table(url):
    driver = webdriver.Firefox()
    driver.get(url)
    driver.find_element_by_id('email').send_keys('max@************.com')
    driver.find_element_by_id('password').send_keys('Password********')
    driver.find_element_by_xpath('//*[@id="app"]/div[1]/section/div[2]/div/div/div/div[4]/div[2]/button').click()

    time.sleep(7) ## change this if you have a fast or slow page, but you gotta wait for the webpage to load in
    table = driver.find_element_by_xpath('//*[@id="marketing"]/div[2]/div[2]/div/div/div/div/div/table/tbody')

    raw_w_tags = table.get_attribute('innerHTML')
    driver.quit()

    name = re.findall("\n\t*.*\n",raw_w_tags)
    total = re.findall("class=\"\">\d+",raw_w_tags)
    active = re.findall("</a></td><td>\d+",raw_w_tags)
    completed = re.findall("</a></td><td>\d+</td><td>\d+",raw_w_tags)
    replied = re.findall("</td><td>\d+</td><td>(<span>\d+|<!---->)",raw_w_tags)
    reply_perc = re.findall("(\d+\.\d{2}%|<!----></td><td><!---->)",raw_w_tags)
    status = re.findall("(Draft|Published)",raw_w_tags)
    camp_id = re.findall("</td><td>[A-z]+</td><td>\w+",raw_w_tags)


    for i in range(len(name)):
        name[i] = re.sub("\s{3,}","",name[i])
        name[i] = re.sub("\n","",name[i])
        total[i] = re.sub("class=\"\">","",total[i])
        active[i] = re.sub("</a></td><td>","",active[i])
        completed[i] = re.sub("</a></td><td>\d+</td><td>","",completed[i])
        status[i] = re.sub("</span></td><td>\w+|<!----></td><td>","",status[i])
        camp_id[i] = re.sub("</td><td>[A-z]+</td><td>","",camp_id[i])
        if replied[i] == "<!---->":
            replied[i] = "N/A"
        else:
            replied[i] = re.sub("<span>","",replied[i])
        if reply_perc[i] == "<!----></td><td><!---->":
            reply_perc[i] = "N/A"

    # construct data frame
    df = pd.DataFrame(list(zip(name,total,active,completed,replied,reply_perc,status,camp_id)))
    df.rename(columns={0:"Name",1:"Total",2:"Active",3:"Completed",4:"Replied",5:"Reply %",6:"Status",7:"Campaign ID"}, inplace=True)

    df[['Total','Active','Completed','Replied']] = df[['Total','Active','Completed',"Replied"]].apply(pd.to_numeric,errors='coerce')
    df['Reply %'] = round(df['Replied']/df['Total']*100,2)

    return(df)


#### ITERATE THROUGH clients

#CLIENT ORDER - VERY IMPORTANT
clients = ["Client 1 -- Tampa, FL","Client 2 -- Foley, AL","Client 3 -- New York, NY"]
client_url = ["https://app.gocryohelpers.com/location/**********/marketing/acquisition","https://app.gocryohelpers.com/location/*********/marketing/acquisition","https://app.gocryohelpers.com/location/***********/marketing/acquisition"]
df_list = []
gc = pygsheets.authorize(service_file="/Users/max/Desktop/pyprojects/CryoScrape-*********************.json")
API_key = "************************************"

sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/*****************************/edit#gid=0')


for i in range(len(clients)):
    curr_df = get_table(client_url[i])
    wks = sh.worksheet_by_title(clients[i]) # plus 1 becuase our first sheet is the master sheet
    wks.set_dataframe(curr_df,(1,1))
    df_list.append(curr_df)

master_sh_name = "Master Sheet"
sequences_sh_name = "Sequences"
master_df = pd.concat(df_list, keys=clients)
master_df['Location'] = master_df.index.get_level_values(0)
master_df = master_df.droplevel(level=0)
wks = sh[0]
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
title = ("Master - "+ dt_string)
wks.title = title
wks.set_dataframe(master_df,(1,1))

sequence_df = master_df[master_df['Name'].str.contains("Sequence")].groupby(["Name"]).agg({
    "Name":"first",
    "Total":sum,
    "Active":sum,
    "Completed":sum,
    "Replied":sum,
})

sequence_df["Reply %"] = sequence_df["Replied"]/sequence_df["Total"]

wks = sh.worksheet_by_title(sequences_sh_name)
wks.set_dataframe(sequence_df,(1,1))
