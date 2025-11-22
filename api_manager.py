import json
import logging
import threading
from datetime import datetime
from time import time, sleep
import requests
from typing import Dict, List, Optional, Any
import os
from urllib.parse import urlencode

from Project.settings import FIRMWARE_TYPES
from Project.utils import convert_timestamp

# Прячем предупреждение при подключении к небезопасному серверу без сертификата SSL
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class APIManager:
    def __init__(self, base_url="https://api.a-pox.ru:3000"):
        self.base_url = base_url
        self.auth_token = None
        self.refresh_token = None
        self._token_expiry_time = None
        self._token_update_thread = None
        self.user_info = {}
        self.show_login_on_token_failure_callback = None

    def clean_api_manager(self):
        """Скидываем все параметры api_manager"""
        self.auth_token = None
        self.refresh_token = None
        self._token_expiry_time = None
        self._token_update_thread = None
        self.user_info = {}
        self.show_login_on_token_failure_callback = None

    def _make_request(self, method, url, data=None, json_data=None, files=None, timeout=20):
        headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}

        if files:
            try:
                response = requests.request(
                    method,
                    f"{self.base_url}{url}",
                    headers=headers,
                    data=data,
                    files=files,
                    verify=True,
                    timeout=timeout)
                logger.debug(f"Отправляемый запрос: {method} {url}")
                logger.debug(f"Заголовки: {headers}")
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout as errt:
                log_text = f"Время подключения к серверу истекло."
                logger.error(log_text)
                return {"error": log_text}
            except requests.exceptions.RequestException as e:
                log_text = f"Ошибка при выполнении запроса."
                logger.error(log_text)
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"Статус-код: {e.response.status_code}")
                    logger.error(f"Ответ сервера: {e.response.text}")
                return {"error": log_text}
            except json.JSONDecodeError as e:
                log_text = f"Ошибка декодирования JSON ответа."
                logger.error(log_text)
                if hasattr(response, 'text'):
                    logger.error(f"Сырой ответ сервера: {response.text}")
                return {"error": log_text}

        if json_data:
            headers["Content-Type"] = "application/json"

        try:
            if method.upper() == "GET":
                response = requests.request(
                    method,
                    f"{self.base_url}{url}",
                    headers=headers,
                    params=data,  # Используем params для GET-запросов
                    json=json_data,
                    verify=True,
                    timeout=timeout)
            else:
                if data:
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
                response = requests.request(
                    method,
                    f"{self.base_url}{url}",
                    headers=headers,
                    data=data,
                    json=json_data,
                    verify=True,
                    timeout=timeout)
            logger.debug(f"Отправляемый запрос: {method} {response.url}")  # Логируем полный URL
            logger.debug(f"Заголовки: {headers}")
            # Проверка ошибки
            if response.status_code == 204:
                log_text = f"Получен статус 204\nNo Content для запроса."
                logger.debug(log_text)
                return {"error": log_text}
            if not response.text.strip():
                log_text = f"Получен пустой ответ\nот сервера для запроса."
                logger.warning(log_text)
                return {"error": log_text}
            try:
                return response.json()  # Попытка декодировать JSON
            except json.JSONDecodeError as e:
                log_text = f"Ошибка декодирования JSON ответа."
                logger.error(log_text)
                logger.error(f"Статус-код: {response.status_code}")
                logger.error(f"Сырой ответ сервера: {response.text}")
                return {"error": log_text}
        except requests.exceptions.Timeout as errt:
            log_text = f"Невозможно подключиться к серверу!"
            logger.error(log_text)
            return {"error": log_text}
        except requests.exceptions.RequestException as e:
            log_text = f"Ошибка при выполнении запроса."
            logger.error(log_text)
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Статус-код: {e.response.status_code}")
                logger.error(f"Ответ сервера: {e.response.text}")
            return {"error": log_text}

    def login(self, username, password):
        """
        Если пользователь заблокирован возвращает : Incorrent username or Login
        :param username:
        :param password:
        :return: None - все ок, иначе текст ошибки
        """
        data = {"username": username, "password": password}
        response = self._make_request("POST", "/token", data=data)

        if response and "access_token" in response:
            self.auth_token = response["access_token"]
            self.refresh_token = response["refresh_token"]
            self._token_expiry_time = time() + 3600
            self._start_token_update_thread()

            user_info = self.get_user_info()
            if user_info:
                user_role = user_info.get("role", "")
                if user_role.lower() != "admin":
                    self.auth_token = None
                    self.refresh_token = None
                    self._token_expiry_time = None
                    self.user_info = {}
                    self.stop_token_updates()
                    return "Доступ разрешён только для администраторов!"
                return None
            else:
                return "Не удалось получить информацию о пользователе"
        elif response and 'detail' in response:
            return response['detail']
        elif response and 'error' in response:
            return response['error']
        else:
            return "Неизвестная ошибка сервера"

    def _start_token_update_thread(self):
        if not self._token_update_thread or not self._token_update_thread.is_alive():
            self._token_update_thread = threading.Thread(target=self._token_update_loop, daemon=True)
            self._token_update_thread.start()

    def _token_update_loop(self):
        while True:
            if not self.auth_token:
                break

            time_left = self._token_expiry_time - time()
            if time_left <= 5:
                if not self._renew_token():
                    logger.warning("Не удалось обновить токен")
                    break

            sleep_time = max(0, min(time_left, 60))
            sleep(sleep_time)

    def _renew_token(self):
        if not self.refresh_token:
            logger.error("Refresh token отсутствует для обновления")
            return False

        json_data = {"refresh_token": self.refresh_token}
        response = self._make_request("POST", "/token/refresh", json_data=json_data)

        logger.info(f"Ответ сервера на обновление токена: {response}")

        if response is None or "access_token" not in response:
            logger.error(f"Ошибка обновления токена. Ответ: {response}")
            if self.show_login_on_token_failure_callback:
                self.show_login_on_token_failure_callback()
            return False
        else:
            self.auth_token = response["access_token"]
            if "refresh_token" in response:
                self.refresh_token = response["refresh_token"]
            self._token_expiry_time = time() + 60
            return True

    def stop_token_updates(self):
        self.auth_token = None
        self.refresh_token = None
        if self._token_update_thread and self._token_update_thread.is_alive():
            self._token_update_thread.join(timeout=1.0)

    def get_user_info(self):
        response = self._make_request("GET", "/users/me")

        if 'error' in response:
            raise Exception(response['error'])

        if response:
            self.user_info = response
            return response
        return None

    def get_all_firmware_files(self, firmware_type, dev_mode):
        if firmware_type not in FIRMWARE_TYPES:
            raise ValueError("Неверный тип прошивки")

        endpoint = f"/firmware/{firmware_type}/list/all"

        params = {}
        if dev_mode is not None:
            params["dev_mode"] = str(dev_mode).lower()
        logger.debug(f"Параметры запроса: {params}")

        response: list[dict] = self._make_request("GET", endpoint, data=params)

        if isinstance(response, dict) and 'error' in response:
            raise Exception(response['error'])

        if response:
            for firmware in response:
                if "release_date" in firmware:
                    firmware["release_date"] = convert_timestamp(firmware["release_date"])
        return response

    def get_all_firmwaredata(self, dev_mode):
        all_firmware = []
        for firmware_type in FIRMWARE_TYPES:
            response: list[dict] = self.get_all_firmware_files(firmware_type, dev_mode)  # получаем прошивки по типу
            print(response)
            if isinstance(response, dict) and 'error' in response:
                raise Exception(response['error'])

            if response:
                # добавляем тип прошивки в ответ
                for line in response:
                    line['type'] = FIRMWARE_TYPES[firmware_type]
                all_firmware.extend(response)
        return all_firmware

    def get_all_users(self):
        endpoint = "/users/all"
        response = self._make_request("GET", endpoint)
        if 'error' in response:
            raise Exception(response['error'])

        logger.info("Список пользователей успешно получен")
        return response

    def create_user(self, username: str, password: str, role: str, is_active: bool) -> bool:
        endpoint = "/users/create"
        json_data = {
            "username": username,
            "password": password,
            "role": role,
            "is_active": is_active
        }
        response = self._make_request("POST", endpoint, json_data=json_data)

        if 'error' in response:
            raise Exception(response['error'])

        if response is not None:
            logger.info(f"Пользователь {username} успешно создан: {response}")
            return True
        else:
            logger.error(f"Ошибка при создании пользователя {username}")
            return False

    def edit_user_status(self, user_id: str, is_active: bool) -> bool:
        endpoint = f"/users/edit/{user_id}"
        json_data = {
            "is_active": is_active
        }
        response = self._make_request("PUT", endpoint, json_data=json_data)

        if response is not None:
            logger.info(f"Статус пользователя {user_id} успешно изменён: {response}")
            return True
        else:
            logger.error(f"Ошибка при изменении статуса пользователя {user_id}")
            return False

    def edit_user(self, user_id: str, username: Optional[str] = None,
                  password: Optional[str] = None, role: Optional[str] = None,
                  is_active: Optional[bool] = None) -> bool:
        endpoint = f"/users/edit/{user_id}"
        json_data = {}

        if username is not None:
            json_data["username"] = username
        if password is not None:
            json_data["password"] = password
        if role is not None:
            json_data["role"] = role
        if is_active is not None:
            json_data["is_active"] = is_active

        if not json_data:
            return True

        response = self._make_request("PUT", endpoint, json_data=json_data)

        if response is not None:
            logger.info(f"Пользователь {user_id} успешно отредактирован: {response}")
            return True
        else:
            logger.error(f"Ошибка при редактировании пользователя {user_id}")
            return False

    def get_user_history(self, user_id: str) -> Optional[List[Dict]]:
        endpoint = f"/users/{user_id}/history"
        response = self._make_request("GET", endpoint)

        if 'error' in response:
            raise Exception(response['error'])

        if response is not None:
            logger.info(f"История изменений пользователя {user_id} успешно получена")
            return response
        else:
            logger.error(f"Не удалось получить историю изменений пользователя {user_id}")
            return None

    def update_firmware_status(self, firmware_type: str, firmware_id: str, is_active: bool, dev_mode: bool) -> bool:
        endpoint = f"/firmware/{firmware_type}/{firmware_id}/status?is_active={str(is_active).lower()}&dev_mode={str(dev_mode).lower()}"
        response = self._make_request("PUT", endpoint)
        if 'error' in response:
            raise Exception(response['error'])
        if response is not None:
            logger.info(f"Статус прошивки {firmware_id} ({firmware_type}) успешно изменён: {response}")
            return True
        else:
            logger.error(f"Ошибка при изменении статуса прошивки {firmware_id} ({firmware_type})")
            return False

    def add_firmware(self, firmware_type: str, version: str, release_date: str, description: str,
                     info: str, is_active: bool, dev_mode:bool, file_path: str) -> bool:
        # Форматируем release_date в нужный формат: YYYY-MM-DDTHH:MM:SS+00:00
        formatted_release_date = datetime.fromisoformat(release_date.split('.')[0]).strftime("%Y-%m-%dT%H:%M:%S+00:00")

        # Формируем query-параметры
        query_params = {
            "version": version,
            "release_date": formatted_release_date,
            "description": description,
            "info": info if info else "",
            "is_active": str(is_active).lower(),  # Сервер ожидает "true"/"false" как строку
            "dev_mode": str(dev_mode).lower()  # Сервер ожидает "true"/"false" как строку
        }
        # Кодируем query-параметры в URL
        endpoint = f"/firmware/{firmware_type}/add?{urlencode(query_params)}"

        logger.debug(f"Query-параметры: {query_params}")
        # Отправляем только файл в теле запроса
        with open(file_path, "rb") as file:
            files = {
                "firmware": (os.path.basename(file_path), file, "application/octet-stream")
            }
            logger.debug(f"Отправляемый файл: {os.path.basename(file_path)}")
            response = self._make_request("POST", endpoint, files=files)

        if response is not None:
            logger.info(f"Прошивка {version} ({firmware_type}) успешно добавлена: {response}")
            return True
        else:
            logger.error(f"Ошибка при добавлении прошивки {version} ({firmware_type})")
            return False

    def get_firmware_history(self, firmware_type: str, firmware_id: str, dev_mode: bool) -> list:
        endpoint = f"/firmware/{firmware_type}/{firmware_id}/history?dev_mode={str(dev_mode).lower()}"
        response = self._make_request("GET", endpoint)
        if 'error' in response:
            raise Exception(response['error'])
        if response is not None:
            logger.info(f"История изменений для прошивки {firmware_id} ({firmware_type}) успешно загружена")
            return response
        else:
            logger.error(f"Ошибка при загрузке истории изменений для прошивки {firmware_id} ({firmware_type})")
            return []

    def get_all_devices(self):
        endpoint = "/devices/list/all"
        try:
            response = self._make_request("GET", endpoint)

            if 'error' in response:
                raise Exception(response['error'])

            if response is not None:
                logger.info("Список устройств успешно получен")
                return response
            else:
                logger.error("Не удалось получить список устройств")
                return None
        except Exception as e:
            logger.error(f"Ошибка при запросе списка устройств: {e}")
            return None

    def edit_device(self, device_uid: str, name: Optional[str] = None, uid: Optional[str] = None,
                    production: Optional[bool] = None, boot_flash: Optional[bool] = None,
                    app_flash: Optional[bool] = None, activation: Optional[bool] = None) -> bool:
        endpoint = f"/devices/edit/{device_uid}"
        json_data = {}

        if name is not None:
            json_data["name"] = name
        if uid is not None:
            json_data["uid"] = uid
        if production is not None:
            json_data["production"] = production
        if boot_flash is not None:
            json_data["boot_flash"] = boot_flash
        if app_flash is not None:
            json_data["app_flash"] = app_flash
        if activation is not None:
            json_data["activation"] = activation

        if not json_data:
            return True

        response = self._make_request("PUT", endpoint, json_data=json_data)

        if 'error' in response:
            raise Exception(response['error'])

        if response is not None:
            logger.info(f"Устройство с UID {device_uid} успешно отредактировано: {response}")
            return True
        else:
            logger.error(f"Ошибка при редактировании устройства с UID {device_uid}")
            return False

    def delete_device(self, device_uid: str) -> bool:
        endpoint = f"/devices/delete/{str(device_uid)}"
        response = self._make_request("DELETE", endpoint)

        if response is not None:
            logger.info(f"Устройство с UID {device_uid} успешно удалено: {response}")
            return True
        else:
            logger.error(f"Ошибка при удалении устройства с UID {device_uid}")
            return False

    def create_device(self, name: str, uid: str, production: bool,
                      boot_flash: bool = False, app_flash: bool = False,
                      activation: bool = False) -> bool:
        endpoint = "/devices/create"
        json_data = {
            "name": name,
            "uid": uid,
            "production": production,
            "boot_flash": boot_flash,
            "app_flash": app_flash,
            "activation": activation
        }
        response = self._make_request("POST", endpoint, json_data=json_data)

        if 'error' in response:
            raise Exception(response['error'])

        if response is not None:
            logger.info(f"Устройство {name} (UID: {uid}) успешно создано: {response}")
            return True
        else:
            logger.error(f"Ошибка при создании устройства {name} (UID: {uid})")
            return False

    def get_device_history(self, device_uid: str) -> dict[Any, Any] | None:
        endpoint = f"/devices/{device_uid}/history"
        response = self._make_request("GET", endpoint)

        if 'error' in response:
            raise Exception(response['error'])

        if response is not None:
            logger.info(f"История изменений устройства с UID {device_uid} успешно получена")
            return response
        else:
            logger.error(f"Не удалось получить историю изменений устройства с UID {device_uid}")
            return None
