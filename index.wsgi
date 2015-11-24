import sys, os

sys.path.append(os.path.dirname(__file__))

from werkzeug.wsgi import DispatcherMiddleware

from browser.browser import app as browser
from sleipnir.sleipnir import app as sleipnir
from interfaces.lister import app as lister

my_dir        = os.path.abspath(os.path.dirname(__file__))

config        = os.path.join(my_dir, 'config.py')
template_path = os.path.join(my_dir, 'templates')
static_path   = os.path.join(my_dir, 'static')


application = DispatcherMiddleware(browser,
                                   {'/corp':sleipnir})


browser.debug = True
sleipnir.debug = True