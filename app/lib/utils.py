from google.appengine.api import users
from app.models import *
import urllib

import allowed_users

# def require_login(url):
#     if users.get_current_user() is None:
#         return users.create_login_url(url)
#     else:
#         return None
        

## move all this to a Model

def name_to_key(scriptname):
    return ("s_%s" % scriptname)

def key_to_name(scriptname):
    return scriptname[2:]


def scriptname_error(scriptname):

    if not (2 < len(scriptname) < 20):
        return("Name must be between 3 to 20 characters")
    
    if scriptname[0] == '_':
        return("Name can't start with underscore")

    if Script.get_by_key_name(name_to_key(scriptname)) is not None:
        return("Sorry, name already taken.")

    if urllib.quote(scriptname) != scriptname:
        return("Name must consist of URL-valid characters only")

    return None
    
    
def allowed_user(user):
    try:
        i = allowed_users.ALLOWED_USERS.index(user.email())
        return True
    except:
        return False


def can_edit(user, script):
    return (allowed_user(user.email()) and user.email() == script.created_by)
    
    