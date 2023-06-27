from datetime import datetime
import vk_api
from config_new2 import acces_token
from vk_api.exceptions import ApiError

class VkTools():

    def __init__(self, acces_token):
        self.api = vk_api.VkApi(token=acces_token)

    def get_profile_info(self, user_id):
        try:
            info, = self.api.method('users.get',
                                    {'user_id': user_id,
                                     'fields': 'city,bdate,sex,first_name,last_name'
                                     }
                                    )
        except ApiError:
            info = {}
            print('Ошибка получения get_profile_info')

        user_info = {'name': info['first_name'] + ' ' + info['last_name'] if 'first_name' in info and 'last_name' in info else None,
                     'id': info.get('id'),
                     'bdate': info.get('bdate'),
                     # 'home_town': info.get('home_town'),
                     'sex': info.get('sex'),
                     'city': info.get('city')['title'] if 'city' in info else None
                     }

        return user_info

    def search_users(self, user_info, offset = 0):

        sex = 1 if user_info['sex'] == 2 else 2
        city = user_info.get('city')
        bdate_year = user_info.get('bdate').split('.')[2]
        now = datetime.now().strftime('%Y')
        age = int(now) - int(bdate_year)

        profiles = self.api.method('users.search',
                                {'count': 50,
                                 'offset': offset,
                                 'age_from': age - 5,
                                 'age_to': age + 5,
                                 'sex': sex,
                                 'hometown': city,
                                 'status': 6,
                                 'is_closed': False,
                                 'has_photo': True
                                 }
                                )
        try:
            profiles = profiles['items']
        except ApiError:
            profiles = []
            print('Ошибка получения user_search')
        result = []
        for profile in profiles:
            if profile['is_closed'] == False:
                result.append({'id': profile['id'],
                            'name': profile.get('first_name')  + ' ' + profile.get('last_name'),
                               }
                              )
        return result

    def get_photos(self, id):
        photos = self.api.method('photos.get',
                                 {'owner_id': id,
                                  'album_id': 'profile',
                                  'extended': 1
                                  }
                                 )
        try:
            photos = photos['items']
        except KeyError:
            photos = {}
            print('Ошибка получения user_search')
        result = []
        for photo in photos:
            result.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                       )
        result.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)
        return result[:3]

if __name__ == '__main__':
    tools = VkTools(acces_token)