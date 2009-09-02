from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required

from app.lib.baseview import baseview
from app.lib.utils import *
from app.lib.wrapper import *
from app.lib import textile

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
                'home_url'   : 'http://' + self.request.host + "/"
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
        
        tpl =  { 
                'script'    : script, 
                'can_edit'  : (users.get_current_user() == script.created_by),
                'logged_in' : (users.get_current_user() is not None),
                'textile_docs' : textile.textile(script.docs)
                }
        
        if users.get_current_user() is None:
            tpl['login_url']  = users.create_login_url('/_source/%s' % scriptname)
        else:
            tpl['logout_url'] = users.create_logout_url('/_source/%s' % scriptname)
        

        if script is None:
            self.error(404)
        else:
            self.render_template('form.html', tpl)
        

    def post(self, scriptname):
        if users.get_current_user() is None:
            return self.render('Please <a href="%s">login</a> to create a script' % users.create_login_url('/'))
            
        scriptname = self.request.get('scriptname')

        # clean this up - move validations to the Model
        err = scriptname_error(scriptname)
        if err is not None:
            self.redirect("/?%s" % urllib.urlencode({ 'msg' : err, 'scriptname' : scriptname }))
            
        else:        
            Script(key_name=name_to_key(scriptname), name=scriptname).put()
            self.redirect('/_source/%s' % scriptname)
        

    def put(self, scriptname):
        code = self.request.get('code', '')
        docs = self.request.get('docs', '')
        
        description = self.request.get('description', '')
        listable = self.request.get('listable', default_value='false')

        format = self.request.get('format')
        
        script = Script.get_by_key_name(name_to_key(scriptname))

        if users.get_current_user() != script.created_by:
            self.error(500)
            
        elif script is None:
            self.error(404)

        else:
            script.code = code
            script.docs = docs
            script.description = description
            script.listable = (listable == "true")
                
            script.put()
            if format != 'xhr': 
                self.redirect('/_source/%s' % scriptname)



class RunHandler(baseview):
    '''
    executes the user script
    '''

    def _execute(self, scriptname, method):
        script = Script.get_by_key_name(name_to_key(scriptname))
        if script is None:
            return self.error(404)

        code = script.code.replace("\r", '').strip()
        
        namespace = { 
                        'self': self
                    }

        prefix ='''import sys ; sys.modules['app'] = None ; sys.modules['google.appengine.ext'] = None \n'''
        code = prefix + code + "\n\n" + method + "()"
        try:
            exec code in namespace
        except Exception, err:
            self.error(500)
            self.render("ERROR: %s \n" % err)
        
        
    def get(self, scriptname):
        self._execute(scriptname, 'get')
        
        
    def post(self, scriptname):
        self._execute(scriptname, 'post')


    def put(self, scriptname):
        self._execute(scriptname, 'put')

    
    def delete(self, scriptname):
        self._execute(scriptname, 'delete')
