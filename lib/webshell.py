from google.appengine.api import users

def name_to_key(scriptname):
    return ("s_%s" % scriptname)
    
def key_to_name(scriptname):
    return scriptname[2:]
    

def scriptname_error(scriptname):
    from app.models import *
    import urllib
    
    error = None
    
    if not (2 < len(scriptname) < 20):
        error = "Name must be between 3 to 20 characters"
    
    if Script.get_by_key_name(name_to_key(scriptname)) is not None:
        error = "Sorry, name already taken."
    
    if urllib.quote(scriptname) != scriptname:
        error = "Name must consist of URL-valid characters only"
        
    return error
    

def require_login(url):
    if users.get_current_user() is None:
        return users.create_login_url(url)
    else:
        return None