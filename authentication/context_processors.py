from datetime import datetime, timedelta
from .api import *

def global_context(request):
    """"""
    context = {}
    # joined_this_week = False
    first_time_login = False
    
    try:
        # user_token = request.session['user_token']
        last_login = request.session['last_login']
        
        # user_data = user_details(user_token)
    
        # date_joined_session = user_data['date_joined']
        # date_stripped = datetime.strptime(date_joined_session, '%Y-%m-%d %H:%M:%S')
        # date_joined = date_stripped.date()

        # date_now = datetime.now().date()

        # if (date_now-date_joined).days < 7 :
        #     joined_this_week = True    
        # else:
        #     joined_this_week = False    
        
        if last_login:
            first_time_login = False
        else:
            first_time_login = True

        # context['joined_this_week'] = joined_this_week
        context['first_time_login'] = first_time_login
        
    except Exception as e:
        print(str(e))
    
    return context