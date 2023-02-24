from spotify import user_auth
from constants import *

user_auth(CLIENT_ID, 'code', REDIRECT_URI, SCOPES)
