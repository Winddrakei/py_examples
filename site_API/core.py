import requests
from typing import Dict
from config import *

BASE_URL = 'https://real-time-product-search.p.rapidapi.com/search'


class APIResponse:
	""" Модель работы с API  """
	def __init__(self, querystring: Dict) -> None:
		self.url = BASE_URL
		self.querystring = querystring
		self.headers = {
			"X-RapidAPI-Key": X_RAPID_API_KEY,
			"X-RapidAPI-Host": X_RAPID_API_HOST
		}

	def get_items(self) -> Dict:
		"""
			Функция получает данные по API и собирает их в словарь
			Ограничение сервера: 1 запрос в минуту
		"""
		response = requests.get(self.url, headers=self.headers, params=self.querystring)
		result = response.json()
		found_items = {'item_list': [], 'status': False, 'error': None}
		try:
			if result['status'] == 'OK':
				found_items['status'] = True
				for res in result['data']:
					item = dict()
					item['title'] = res['product_title']
					item['image'] = res['product_photos'][0]
					item['price'] = res['offer']['price']
					item['url'] = res['product_page_url']
					found_items['item_list'].append(item)
		except KeyError:
			found_items['error'] = result['message']
		return found_items
