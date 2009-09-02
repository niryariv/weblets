import datetime
from google.appengine.ext import db

class Script(db.Model):
    name  = db.StringProperty (required=True)
    description   = db.StringProperty (required=False, default='')
    listable = db.BooleanProperty (default=False)
    
    code  = db.TextProperty (required=False, default='')
    docs  = db.TextProperty (required=False, default='')
    
    created_at  = db.DateTimeProperty (auto_now_add=True)
    updated_at  = db.DateTimeProperty (auto_now=True)
    
    created_by  = db.UserProperty (auto_current_user=True)
    
    def name_to_key(self, scriptname):
        return ("s_%s" % scriptname)

    def key_to_name(self, scriptname):
            return scriptname[2:]