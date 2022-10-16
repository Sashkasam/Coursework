import requests
import time
import json
from tqdm import tqdm
from pprint import pprint
import collections
from datetime import datetime


# В 'tokens.txt' храним наши токены
with open('tokens.txt', 'r') as file_object:
    token_vk = file_object.readline().strip()
    token_yd = file_object.readline().strip()

# Получаем фото из профиля
class VkUser:
    url = 'https://api.vk.com/method/'
    def __init__(self, token_vk, version):
        self.params = {'access_token' : token_vk, 'v' : version}

    def get_photos(self):
        user_id = int(input("Введите id пользователя VK: "))
        count_photo = int(input("Введите количесто фотографий для скачивания: "))
        photos_url = self.url + 'photos.get'
        photos_params = { 'owner_id' : user_id, 'album_id' : 'profile', 'extended' : 1, 'photo_sizes' : 1, 'count' : count_photo}
        result = requests.get(photos_url, params = {**self.params, **photos_params}).json()
        return result['response']['items']

vk_client_photos = VkUser(token_vk,'5.131').get_photos()
photo_list = []

class Yandexloader:
    def __init__(self,token_yd):
        self.token = token_yd

    def get_headers(self):
        return {'Content-Type': 'application/json', 'Authorization': 'OAuth {}'.format(self.token)}

    def create_folder(self,folder_name): # функция создание папки на яндекс диске
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        folder_params = {'path': '/'+ folder_name}
        resp = requests.put(url, params=folder_params, headers=headers )
        print(f'Папка {folder_name} успешно создана на Яндекс диске:' )

    def upload_photo(self,folder_name): # функция загрузки файла в созданную папку
        for photos in tqdm(vk_client_photos, desc='Загрузка фотографий на Яндекс Диск .'):
            time.sleep(3)
            file_name = str(photos['likes']['count'])
            photo_date = datetime.strftime(datetime.fromtimestamp(photos['date']), '%d-%m-%Y')
            url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            headers = self.get_headers()
            photo_params = {'path': '/'+ folder_name + '/' + '_'.join([file_name, photo_date]) + '.jpeg', 'url' : photos['sizes'][-1]['url']}
            resp = requests.post(url, headers=headers,params=photo_params)
            photo_list.append({'file_name' : '_'.join([file_name, photo_date])+ '.jpeg' , 'size' : photos['sizes'][-1]['type']})
            print(photo_list)
            with open('uploads_foto.json', 'w') as file_json:
                json.dump(photo_list, file_json, indent=2)
        print(f'Все фото успешно загружены на Яндекс диск в папку {folder_name}')
        print(f'Информация по загруженным файлам успешно записана в "uploads_foto.json"')


def init():
    uploader = Yandexloader(token_yd)
    folder_name = input("Введите название папки которую хотите создать: ")
    result = uploader.create_folder(folder_name)
    result2 = uploader.upload_photo(folder_name)




if __name__ == '__main__':
   init()
