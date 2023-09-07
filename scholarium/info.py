DOMAIN = 'scholarium.io'

# MAILER
EMAIL_HOST = 'smtp.hostinger.com' 
EMAIL_HOST_USER = 'mailer@scholarium.io' 
EMAIL_HOST_PASSWORD = 'hnVw35UEvflyXYPzJI7IWk2AmZkIpL8-'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
TEST_EMAIL_RECEIVER = 'jamesmacklean27@gmail.com'

# API
API_SECRET_KEY = "5af375913e149630a4dd18e2ac1548cf9bdcde9c9e03eb24e1a1f3cb5e540c4a"
API_URL = "https://scholarium.tmtg-clone.click/v1/"
COURSEBANK_DISCOVERY_URL = "https://discovery.coursebank.ph/api/v1/"
COURSEBANK_LMS_URL = "https://coursebank.ph/api/"
API_LOGIN_ACCOUNT_URL = API_URL+"login"
API_CREATE_ACCOUNT_URL = API_URL+"user/add"
API_VERIFY_ACCOUNT_URL = API_URL+"user/verify/"

API_USER_URL = API_URL+"me"
API_USER_PROFILE_URL = API_URL+"me/profile"
API_USER_EMPLOYMENT_URL = API_URL+"me/employment"
API_USER_EDUCATION_URL = API_URL+"me/education"
API_USER_PROGRAMS_URL = API_URL+"me/scholarship"
API_USER_PARTNERS_URL = API_URL+"me/partners"
API_SCHOLAR_APPLY_URL = API_URL+"me/scholarship"
API_UPDATE_PASSWORD_URL = API_URL+"me/password"

API_PARTNER_PROGRAMS_URL = API_URL+"partner/programs/"
API_SCHOLAR_UPDATE_URL = API_URL+"partner/scholarship/"

COURSEBANK_COURSES_URL = COURSEBANK_DISCOVERY_URL+"courses/?limit=9&"
COURSEBANK_USERS_URL = COURSEBANK_LMS_URL+"users"

########## ORIGINAL CODE ##########
API_TOKEN = 'TMTG tujyBpbgtum3xcctFvXZgr4ZnaRsddVRpvkwJuq8B3KEwfd4BZQtrRaj5r4vdtDm'
########## FOR TEST CODE ##########
# API_TOKEN = 'LOC_TEST b3vg5vz5t6QJqRccTTysUtaYzF9bmUUrZXDNP54hxyF3Nr6azNdmAHXRrYjSQXA5'

# Engr_James
# e84c2f7ab568bbf073ec619aee9bb0d189651e05
# qwerty
# {%csrf_token%}