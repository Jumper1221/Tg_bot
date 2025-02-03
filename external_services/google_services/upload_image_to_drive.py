import os

from aiogram import Bot

from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build

# pip install google-api-python-client

SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'cinkoff-store-397509-6699dd9ae142.json'

path_to_save = 'external_services/google_services/images'
os.makedirs(path_to_save, exist_ok=True)


async def save_photo_from_telegramm(photo_id: str, bot: Bot) -> str:
    # формируем имя файла
    photo_name = photo_id[:5] + '.jpeg'

    # Скачиваем файл
    await bot.download(file=photo_id, destination = os.path.join(path_to_save, photo_name))
    # Отдаем имя файла
    print('\n\n', photo_name, '\n\n')
    return photo_name


# Функция загрузки файла на гугл диск и получения ссылки
# Проблемы
# - Медленное сохранение, т.к. сначала сохраняем на локальный диск с ТГ а потом на гугл
# - Не удаляем файлы (файл остается и на локалке и в гугле). Нужно запланировать чистку

def upload_to_drive(photo_name: str) -> str:
    # Test connection to Google Drive
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)

    file_path = os.path.join(path_to_save, photo_name)
    file_metadata = {
        'name': photo_name,
        'mimeType': 'image/jpeg'
    }
    media = MediaFileUpload(file_path, mimetype='image/jpeg')

    # Загрузка файла на Google Drive
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    web_view_link = file.get('webViewLink')
    file_id = file.get('id')
    print(f'File ID: {file_id}')
    print(f'web_view_link: {web_view_link}')

    # Словарик с доступом к файлу для всех
    user_permission = {
        'type': 'anyone',  # 'user' 'group' 'domain' 'anyone'
        'role': 'reader',  # Можно использовать 'writer' или 'reader' или 'owner' в зависимости от ваших нужд
    }

    # Выдаем права доступа к файлу
    # Documentation https://developers.google.com/drive/api/reference/rest/v3/permissions
    permission = service.permissions().create(
        fileId=file_id, # ID файла
        body=user_permission, # Словарик с типом доступа
    ).execute()

    # Проверка, что файл загружен
    try:
        file_info = service.files().get(fileId=file_id, fields='id, name, mimeType, webViewLink').execute()
        print(f'File successfully uploaded: {file_info}')
        print(f"web_view_link: {file_info.get('webViewLink')}")
    except Exception as e:
        print(f'Error retrieving the file: {e}')

    # возвращаем ссылку на фото в гугл диске
    return file_info.get('webViewLink')


async def get_image_url(photo_id: str, bot: Bot) -> str:
    _filename = await save_photo_from_telegramm(photo_id, bot)
    return upload_to_drive(_filename)