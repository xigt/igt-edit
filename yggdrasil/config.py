# Configuration file for the web interface
import os

# -------------------------------------------
# Get the default paths for the project...
# -------------------------------------------
from urllib.parse import urljoin

APPLICATION_ROOT = '/editor/'
PROJ_ROOT    = os.path.dirname(os.path.dirname(__file__))
STATIC       = os.path.join(PROJ_ROOT, 'static')
STATIC_URL   = os.path.join(APPLICATION_ROOT, 'static/')
# -------------------------------------------

XIGT_DIR = '/Users/rgeorgi/Dropbox/riples/data/xigt_data/XAML'

# Debug mode?
DEBUG = True

# INTENT
INTENT_LIB = '/opt/intent'

# XIGT
XIGT_LIB = '/opt/xigt'

# SLEIPNIR
SLEIPNIR_LIB = '/opt/sleipnir'

# ODIN_UTILS_DIR
ODIN_UTILS   = '/opt/odin-utils'

# XIGTVIZ DIR
XIGTVIZ      = os.path.join(STATIC, 'xigtviz')
XIGTVIZ_URL  = urljoin(STATIC_URL, 'xigtviz')

# PDF Data Dir
PDF_DIR = '/odin_pdfs'

# -------------------------------------------
# Users DB
USER_DB = '/var/www/yggdrasil-users/users.js'

# -------------------------------------------
# Values for line
# -------------------------------------------
LINE_TAGS = ['L','G','T','M','B']
LINE_ATTRS = ['AC', 'AL', 'CN', 'CR', 'DB', 'EX', 'LN', 'LT', 'SY']

# -------------------------------------------
# Reasons
# -------------------------------------------
BAD_REASONS = {'noisy':"This is too noisy to recover.",
               'notigt':"This is not an IGT instance."}
OK_REASONS  = {'notsure':"I'm not sure"}
