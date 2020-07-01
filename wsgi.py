
import sys
 
# app's path
sys.path.insert(0,"/home/nginx/anaconda2/envs/flask")
 
from manager import app
 
# Initialize WSGI app object
application = app
