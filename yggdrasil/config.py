# Debug mode?
DEBUG = True

# INTENT
INTENT_LIB = '/opt/intent'

# XIGT
XIGT_LIB = '/opt/xigt'

# SLEIPNIR
SLEIPNIR_LIB = '/opt/sleipnir'

# -------------------------------------------
# Users DB
USER_DB = '/var/www/yggdrasil-users/users.js'

# -------------------------------------------
# Values for line
# -------------------------------------------
LINE_TAGS = ['L','G','T','M']
LINE_ATTRS = ['AC', 'CN', 'CR', 'DB', 'LN', 'SY', 'LT', 'AL', 'EX']

# -------------------------------------------
# Reasons
# -------------------------------------------
BAD_REASONS = {'noisy':"This is too noisy to recover.",
               'notigt':"This is not an IGT instance."}
OK_REASONS  = {'notsure':"I'm not sure"}