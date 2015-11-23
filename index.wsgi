import sys, os
sys.path.append(os.path.dirname(__file__))

from werkzeug.wsgi import DispatcherMiddleware
from interfaces.browser import app as browser
from interfaces.lister import app as lister
from interfaces.backend import app as backend


application = DispatcherMiddleware(browser,
                                   {'/list':lister,
                                    '/corp':backend})