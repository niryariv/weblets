import datetime
from google.appengine.ext import db

class Script(db.Model):
    name  = db.StringProperty   (required=True)
    
    code  = db.TextProperty     (required=False, default='')
    docs  = db.TextProperty     (required=False, default='')
    
    created_at  = db.DateTimeProperty (auto_now_add=True)
    updated_at  = db.DateTimeProperty (auto_now=True)
    
    created_by  = db.UserProperty(auto_current_user=True)
  

