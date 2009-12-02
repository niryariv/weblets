CODE = '''

def get():
    msg = self.request.get("msg", None)
    if msg is None:
        msg = "Hi! I'm a new Weblet. "
        msg+= "Call me with ?msg=hey to print out 'hey', "
        msg+= "or edit me to start writing your own script."
    self.render(msg)
    
def post():
    pass

def put():
    pass

def delete():
    pass


'''

DOCS = '''
**Description**

General description of the script's purpose


**Params**

	param_name	Paramater description


**Examples**

* <http://example/url>

'''