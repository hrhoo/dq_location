import pandas as pd
import numpy as np
import folium as fo
from time import sleep
from bs4 import BeautifulSoup as bs

# from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pprint import pprint

""" Data by 2024 July 26"""

""" prepare the driver
    
"""
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument("location=default")
# user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36"
# chrome_options.add_argument("user-agent={0}".format(user_agent))
# driver = webdriver.Chrome(options=chrome_options)
# driver.implicitly_wait(10)
# dq_locator_url = "https://www.dairyqueen.com/en-ca/locations/"

""" click dirctory
    
    driver: webdriver.Chrome
"""
# DIRECTORY_LOCATION = "#section-1 > div > div > div > div.Locations_location-sidebar__container__Axdj1.w-full.mx-auto.my-0.lg\:absolute.inset-0.pointer-events-none > aside > div.Locations_location-directory__T7Lla.px-6 > a"
# def click_directory(driver: webdriver.Chrome):
#     driver.refresh()

#     target = WebDriverWait(driver, 20).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, DIRECTORY_LOCATION))
#     )
#     driver.execute_script("arguments[0].click();", target)
#     return


"""Prepare containers and go through the loop to get the data
    
"""
# # 'NT' 'NU' are missing
# province_code = ["AB", "BC", "MB", "NB", "NL", "NS", "ON", "PE", "QC", "SK", "YT"]
# Province = []
# City = []
# City_compare = []
# Latitude = []
# Longitude = []
# Address = []


"""Get all the names of cities from the website

"""
# df = pd.read_csv('projects/python/crawler/DQ/province_city.csv')

# for prov in province_code:
#     sleep(1)
#     driver.get(dq_locator_url + prov)

#     sleep(5)
#     html = driver.page_source
#     soup = bs(html, "html.parser")
#     cities = soup.find_all("a", class_="body--2 -bold link mt-4 mr-2")

#     for city in cities:
#         herf = city.get("href").split("/")
#         prov_, city_ = herf[3], herf[4]
#         city_compare = city.text

#         province.append(prov_)
#         City.append(city_)
#         City_compare.append(city_compare)

# df = pd.DataFrame()
# df["Province"] = province
# df["City"] = City
# df["City_compare"] = City_compare
# print(df)
# df.to_csv('projects/python/crawler/DQ/province_city.csv', index=False)


"""Remove duplicates from the dataframe
"""
# df = df.drop_duplicates(subset=["Province","City"])
# df_dp = df.duplicated(subset=["Province","City"])
# df.reset_index(drop=True, inplace=True)
# df.to_csv('projects/python/crawler/DQ/province_city.csv', index=False)
# print(df)
# pprint("===========================================")

""" Get addresses from the website
    
"""
# check_ON = False
# df = pd.read_csv('projects/python/crawler/DQ/province_city.csv')
# for prov, ct in zip(df["Province"], df["City"]):

#     # if prov == "on":
#     #     check_ON = True
#     # if check_ON == False:
#     #     continue

#     sleep(1)
#     driver.get(dq_locator_url + prov + "/" + ct)
#     sleep(1)


#     html = driver.page_source
#     soup = bs(html, "html.parser")
#     branches = soup.find_all("li", {"class": "Locations_location__MOdkU flex justify-between relative"})

#     if len(branches) == 0:
#         driver.get(dq_locator_url + prov + "/" + ct)
#         sleep(5)
#         driver.refresh()
#         sleep(3)
#         html = driver.page_source
#         soup = bs(html, "html.parser")
#         branches = soup.find_all("li", {"class": "Locations_location__MOdkU flex justify-between relative"})
#         if len(branches) == 0:
#             pprint(branches)
#             print("No branches")
#             print(prov, ct)
#             print("===========================================") # there were three cities having no branches (St JohnApos S is the same as St Johns(NL), Weston(ON) (actually has 1 location), South Lancaster(ON))
#             continue

#     for branch in branches:
#         lat, lng = branch.get("id").split(",")
#         city = branch.find("a").get("href").split("/")
#         prv, city, addr = city[3], city[4], city[5]
#         City.append(city)
#         Province.append(prv)
#         Latitude.append(lat)
#         Longitude.append(lng)
#         Address.append(addr)

# df = pd.DataFrame()
# df["Province_compare"] = Province
# df["City"] = City
# df["Latitude"] = Latitude
# df["Longitude"] = Longitude
# df["Address"] = Address

# pprint(df.tail())
# df.to_csv('projects/python/crawler/DQ/DQ_location_after_ON.csv', index=False)
# print("===========================================")

"""
Combine the dataframes and remove duplicates    
"""
# df_before_ON = pd.read_csv('projects/python/crawler/DQ/DQ_location_until_ON.csv')
# df_after_ON = pd.read_csv('projects/python/crawler/DQ/DQ_location_after_ON.csv')
# df_combined = pd.concat([df_before_ON, df_after_ON], ignore_index=True)
# df_combined.to_csv('projects/python/crawler/DQ/DQ_location_with_dup.csv', index=False)
# print(df_combined.tail())

# df_combined = df_combined.drop_duplicates(subset=["Province_compare", "City", "Latitude", "Longitude"])
# df_combined.reset_index(drop=True, inplace=True)
# df_combined.to_csv('projects/python/crawler/DQ/DQ_location_with_no_dup.csv', index=False)
# print(df_combined)
# pprint("===========================================")


"""
Group by Province and City
"""
# df_branch = pd.read_csv('projects/python/crawler/DQ/DQ_location_with_no_dup.csv')
# pprint(df_branch.tail())

# pprint("groupby Province:")
# df_branch_gby_p = df_branch.groupby(["Province_compare"], as_index=False).count()
# df_branch_gby_p.to_csv('projects/python/crawler/DQ/DQ_location_gby_p.csv', index=False)
# pprint(df_branch_gby_p)

# pprint("groupby City:")
# df_branch_gby_c = df_branch.groupby(by=["Province_compare", "City"], as_index=False).count()
# df_branch_gby_c.to_csv('projects/python/crawler/DQ/DQ_location_gby_c.csv', index=False)
# pprint(df_branch_gby_c)
# pprint("===========================================")

"""
Draw the bar chart    
"""
import matplotlib.pyplot as plt
from matplotlib import cm

# df_gby_p = pd.read_csv("projects/python/crawler/DQ/DQ_location_gby_p.csv")
# ax = df_gby_p.plot.bar(
#     legend=False,
#     x="Province_compare",
#     y="City",
#     title="Number of DQ branches by Province",
#     figsize=(10, 5),
#     color=cm.tab10.colors,
# )
# ax.bar_label(ax.containers[0])
# # plt.show()

sleep(600)
