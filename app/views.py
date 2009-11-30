from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required

from gaet.baseview import baseview
from app.lib.utils import *
from app.lib.wrapper import *

from models import *
from config import templates as default_tmpl

import urllib
import logging
import sys

class ImportTest(baseview):
    def get(self):
        import app.lib.import_watch as impwatch
        impwatch.activate()

        import urllib2
        from google.appengine.ext import db

        self.render (str(urllib2))
        

class DefaultHandler(baseview):
    '''    Homepage    '''
    def get(self):
        
        user = users.get_current_user()
        
        tpl = { 
                'msg' : self.request.get('msg'),
                'scriptname' : self.request.get('scriptname'),
                'logged_in'  : (users.get_current_user() is not None),
                'allowed_user': allowed_user(users.get_current_user()),
                'home_url'   : 'http://' + self.request.host + "/",
                'user'       : user
              }

        tpl['script_list']= Script.all().filter('listable', True).order('-updated_at')
        if tpl['script_list'].count() == 0: tpl['script_list'] = None
        
        if user is None:
            tpl['login_url']  = users.create_login_url('/')
        else:
            tpl['my_scripts'] = Script.all().filter('created_by', user).order('-updated_at')
            if tpl['my_scripts'].count() == 0: tpl['my_scripts'] = None
            tpl['logout_url'] = users.create_logout_url('/')
        
        self.render_template('index.html', tpl)
        

class SourceHandler(baseview):
    '''
    Display/edit source code
    '''

    def get(self, scriptname):
        script = Script.get_by_key_name(name_to_key(scriptname))

        if script is None:
            return self.error(404)
        
        tpl =  { 
                'user'      : users.get_current_user(),
                'script'    : script, 
                'can_edit'  : (users.get_current_user() == script.created_by),
                'logged_in' : (users.get_current_user() is not None),
                }
        
        if users.get_current_user() is None:
            tpl['login_url']  = users.create_login_url('/_source/%s' % scriptname)
        else:
            tpl['logout_url'] = users.create_logout_url('/_source/%s' % scriptname)
        
        self.render_template('form.html', tpl)
        

    def post(self, scriptname):
        if not allowed_user(users.get_current_user()):
            return self.error(401)
            
        scriptname = self.request.get('scriptname')

        # clean this up - move validations to the Model
        err = scriptname_error(scriptname)
        if err is not None:
            self.redirect("/?%s" % urllib.urlencode({ 'msg' : err, 'scriptname' : scriptname }))
            
        else:        
            Script(
                key_name=name_to_key(scriptname), 
                name=scriptname,
                docs=default_tmpl.DOCS,
                code=default_tmpl.CODE
                ).put()
            self.redirect('/_source/%s' % scriptname)
        

    def put(self, scriptname):
        code = self.request.get('code', '')
        docs = self.request.get('docs', '')
        
        description = self.request.get('description', '')
        listable = self.request.get('listable', default_value='false')

        format = self.request.get('format')
        
        docs = docs.replace('<', '&lt;')
        docs = docs.replace('>', '&gt;')
        
        script = Script.get_by_key_name(name_to_key(scriptname))

        if script is None:
            return self.error(404)

        if users.get_current_user() != script.created_by:
            return self.error(401)

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


        exec code in namespace
        # try:
        #     exec code in namespace
        # except Exception, err:
        #     self.error(500)
        #     self.render("ERROR %s \n" % err)
        
        
    def get(self, scriptname):
        self._execute(scriptname, 'get')
        
        
    def post(self, scriptname):
        self._execute(scriptname, 'post')


    def put(self, scriptname):
        self._execute(scriptname, 'put')

    
    def delete(self, scriptname):
        self._execute(scriptname, 'delete')


class ExportHandler(baseview):
    ''' Export datastore contents in CSV format'''

    def get(self):
        import csv

        props = Script.properties().keys()
        rows = [props.append('aaaa')]
        
        for s in Script.all().fetch(1000):
            fields = [s.key()]
            for p in props:
                data = str(getattr(s,p))
                data = data.replace("\n", "\\n")
                fields.append(data)

            rows.append(fields)
            
        self.response.headers["Content-Type"] = 'text/plain'
        writer = csv.writer(self.response.out)

        print rows
        # for item in rows:
        #     writer.writerow(item)        
        
        
        
        