#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 20:00:29 2023

@author: ravj

Script to webscrap fitpass studios (WIP)
"""
# %% libraries
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

# 





# %% main
# URL of the website to scrape
url = "https://www.fitpass.com/mx/mapa"

# Send an HTTP GET request to the URL
response = requests.get(url)
print(response.text)

# get the soup
soup = BeautifulSoup(response.content)

# TODO: PASS FUNCTION FROM NOTEBOOK TO HERE
