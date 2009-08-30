from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required

from lib.baseview import baseview
from lib.webshell import *
from lib.wrapper import *

from models import *

import urllib
import logging
import sys


class DefaultHandler(baseview):
    '''    Homepage    '''
    def get(self):
        
        tpl = { 
                'msg' : self.request.get('msg'),
                'scriptname' : self.request.get('scriptname'),
                'logged_in'  : (users.get_current_user() is not None),
                'home_url'   : self.request.url
              }

        if users.get_current_user() is None:
            tpl['login_url']  = users.create_login_url('/')
        else:
            tpl['logout_url'] = users.create_logout_url('/')
        
        self.render_template('index.html', tpl)
        

class SourceHandler(baseview):
    '''
    Display/edit source code
    '''

    def get(self, scriptname):
        script = Script.get_by_key_name(name_to_key(scriptname))

        if script is None:
            self.error(404)
        else:
            self.render_template('form.html', { 'script' : script, 'can_edit' : (users.get_current_user() == script.created_by) })
        

    def post(self, scriptname):
        if users.get_current_user() is None:
            return self.render('Please <a href="%s">login</a> to create a script' % users.create_login_url('/'))
            
        scriptname = self.request.get('scriptname')

        err = scriptname_error(scriptname)
        if err is not None:
            self.redirect("/?%s" % urllib.urlencode({ 'msg' : err, 'scriptname' : scriptname }))
            
        else:        
            Script(key_name=name_to_key(scriptname), name=scriptname).put()
            self.redirect('/_source/%s' % scriptname)
        

    def put(self, scriptname):
        code = self.request.get('code', '')
        docs = self.request.get('docs', '')

        format = self.request.get('format')
        
        script = Script.get_by_key_name(name_to_key(scriptname))

        if users.get_current_user() != script.created_by:
            self.error(500)
            
        elif script is None:
            self.error(404)

        else:
            script.code=code
            script.docs=docs
            script.put()
            if format != 'xhr': 
                self.redirect('/_source/%s' % scriptname)



class RunHandler(baseview):
    '''
    executes the user script
    '''

    def _loadscript(self, name):
        script = Script.get_by_key_name(name_to_key(name))
        code = script.code.replace("\r", '').strip()
        
        self.namespace = { 
                            'self': self
                         }

        prefix ='''import sys ; sys.modules['app'] = None ; sys.modules['google.appengine.ext'] = None \n'''
        self.code = prefix + code
        
        
    def get(self, scriptname):
        self._loadscript(scriptname)
        
        code = self.code + "\nget()"
        exec code in self.namespace
        
        
    def post(self, scriptname):
        self._loadscript(scriptname)
        
        code = self.code + "\npost()"
        exec code in self.namespace


    def put(self):
        pass

    
    def delete(self):
        pass
