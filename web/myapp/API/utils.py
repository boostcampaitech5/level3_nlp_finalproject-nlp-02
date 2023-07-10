from .models import UserInfo, Bookmarks


def save_list_into_db(data):
    bookmark_objects = []
    for bookmark_data in data:
        bookmark_data['userId'] = UserInfo.objects.get(userId=bookmark_data['userId'])
        
    bookmark_objects = [Bookmarks(**bookmark_data) for bookmark_data in data]

    # Use bulk_create to save all the objects into the database
    Bookmarks.objects.bulk_create(bookmark_objects)


def save_dict_into_db(data):
    # logger.info(UserInfo.objects.all())
    
    # bookmark 가 userInfo의 userId를 참조하므로, 이러한 방식으로 parent-child '식별관계' 를 구축할 수 있는 것인 것 같다(? 불확실)
    Bookmarks.objects.create(userId=UserInfo.objects.get(userId=data['userId']), userEmail=data['userEmail'],
                             url=data['url'], context=data['context'],folder=data['folder'], tag=data['tag'])


def save_new_user_into_db(data):
    if isinstance(data, list):
        _userId = data[0]['userId']
        _userEmail = data[0]['userEmail']
        
    else:
        _userId = data['userId']
        _userEmail = data['userEmail']
    _userPassword = ""
    
    UserInfo.objects.create(userId=_userId, userEmail=_userEmail, userPassword=_userPassword)