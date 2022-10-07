import os
from rate_scrapper.rate_ext import rate_on_date

path = os.getcwd()
print('Current Directory', path)
 
# prints parent directory
print('Parent directory', os.path.abspath(os.path.join(path, os.pardir)))


x = rate_on_date()
print(x)

