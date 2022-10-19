import os
from rate_scrapper.rate_ext import get_rate

path = os.getcwd()
print('Current Directory', path)
 
# prints parent directory
print('Parent directory', os.path.abspath(os.path.join(path, os.pardir)))


x = get_rate()
print(x)

