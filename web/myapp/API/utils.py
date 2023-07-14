from .models import UserInfo, Bookmarks
from django.core.exceptions import ObjectDoesNotExist
import requests

# multiple bookmarks saving
def save_list_into_db(data):
    bookmark_objects = []
    try:
        for bookmark_data in data:
            bookmark_data['userId'] = UserInfo.objects.get(userId=bookmark_data['userId'])
            
        bookmark_objects = [Bookmarks(**bookmark_data) for bookmark_data in data]

        # Use bulk_create to save all the objects into the database
        Bookmarks.objects.bulk_create(bookmark_objects)
    
    except UserInfo.DoesNotExist:
        message = "POST from Django"
        request_for_user_previous_bookmark(message)
        

# one bookmark saving
def save_dict_into_db(data):
    # logger.info(UserInfo.objects.all())
    
    # bookmark 가 userInfo의 userId를 참조하므로, 이러한 방식으로 parent-child '식별관계' 를 구축할 수 있는 것인 것 같다(? 불확실)
    data['userId'] = UserInfo.objects.get(userId=data['userId'])
    
    Bookmarks.objects.create(**data)

# save new user into database for new user
def save_new_user_into_db(data):
    if isinstance(data, list):
        _userId = data[0]['userId']
        _userEmail = data[0]['userEmail']
        
    else:
        _userId = data['userId']
        _userEmail = data['userEmail']
    _userPassword = ""
    
    UserInfo.objects.create(userId=_userId, userEmail=_userEmail, userPassword=_userPassword)


def request_for_user_previous_bookmark(message):
    extension_id = 'dpanheakmannmbojfiebgbfacghkjffj'
    extension_url = f'chrome-extension://{extension_id}/'

    data = {'message': message}
    response = requests.post(extension_url, data=data)

    if response.status_code == 200:
        print('Message sent successfully')
    else:
        print('Failed to send message')

    return response
    