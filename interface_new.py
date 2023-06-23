import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config_new import community_token, acces_token
from core_new import VkTools
import base_new
import psycopg2
conn = psycopg2.connect(database="postgres", user="postgres", password="38621964")

class BotInterface():

    def __init__(self, community_token, acces_token):
        self.bot = vk_api.VkApi(token=community_token)
        self.tools = VkTools(acces_token)
        self.info = {}
        self.longpoll = VkLongPoll(self.bot)
        self.users = []
        self.offset = 0
        self.user = []

    def message_send(self, user_id, message, attachment=None):
        self.bot.method('messages.send',
                      {'user_id': user_id,
                       'message': message,
                       'attachment': attachment,
                       'random_id': get_random_id()
                       }
                      )

    def handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command == 'привет':
                    base_new.base.create_db(conn)
                    self.info = self.tools.get_profile_info(event.user_id)
                    print(self.info)
                    if self.info['city'] is None:
                        self.info['city'] = self.get_city(event)
                    elif self.info['bdate'] is None:
                        self.info['bdate'] = self.get_bdate(event)
                    elif self.info['sex'] is None:
                        self.info['sex'] = self.get_sex(event)
                    self.message_send(event.user_id, f'Здравствуй, {self.info["name"]}, напиши поиск или далее')

                elif command == 'поиск' or 'далее':
                    self.message_send(event.user_id, 'Начинаем искать!')
                    if self.users:
                        user = self.users.pop()
                        photos_user = self.tools.get_photos(user['id'])
                        attachment = ''
                        for photo in photos_user:
                            attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                    else:
                        self.users = self.tools.search_users(self.info)
                        self.user = self.users.pop()
                        print(self.user)
                        # check_lists = base_new.base.select_profiles(conn, self.info['id'], self.user['id'])
                        # for check_list in check_lists:
                        #     print( )
                        while base_new.base.select_profiles(conn, self.info['id'], self.user['id']):
                            self.user = self.users.pop()
                            if len(self.users) == 0:
                                break
                        # while self.user['id'] == check_list[1]:
                        #     self.user = self.users.pop()
                            print(self.user)

                        photos_user = self.tools.get_photos(self.user['id'])
                        attachment = ''
                        for photo in photos_user:
                            attachment += f'photo{photo["owner_id"]}_{photo["id"]},'

                            self.offset +=50
                            # else:
                            #     # offset += 1
                            #     print('Проблема с таблицами')
                        self.message_send(event.user_id,
                                          f'Встречайте {self.user["name"]} ссылка : vk.com/id{self.user["id"]}',
                                          attachment=attachment
                                         )
                        base_new.base.insert_profiles(conn, event.user_id, self.user['id'], self.user['name'])

                # elif command == 'заново':
                #     base_new.base.delete_db(conn)
                #     self.message_send(event.user_id, 'Таблицы очищены, можно начать поиск заново')

                elif command == 'пока':
                    self.message_send(event.user_id, 'До встречи!')
                    break
                else:
                    self.message_send(event.user_id, 'Ошибка, начките заново')

    def get_bdate(self, event):
        if self.info['bdate'] is None:
            self.message_send(event.user_id, f'Напишите год Вашего рождения')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    self.info['bdate'] = event.text.lower()
                    return self.info['bdate']

    def get_city(self, event):
        if self.info['city'] is None:
            self.message_send(event.user_id, f'В каком городе ищете пару?')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    self.info['city'] = event.text.capitalize()
                    return self.info['city']

    def get_sex(self, event):
        if self.info['sex'] is None:
            self.message_send(event.user_id, f'какого пола ищете пару?')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    self.info['sex'] = event.text.lower()
                    return self.info['sex']

if __name__ == '__main__':
    bot = BotInterface(community_token, acces_token)
    bot.handler()


