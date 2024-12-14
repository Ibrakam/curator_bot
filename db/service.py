import logging
import os

from django.db import transaction

from course.models import User, RequestModel, Refund, Course, ContactInfo, Question
from db import get_db
from asgiref.sync import sync_to_async


@sync_to_async
def add_user(user_id: int, phone: str = '', full_name: str = ''):
    user, created = User.objects.get_or_create(user_id=user_id, defaults={'phone': phone, 'full_name': full_name})
    return not created


@sync_to_async
def add_request(user_id, department, request_type):
    request_id = RequestModel.objects.create(user_id=user_id, department=department, request_type=request_type)
    return request_id.id


@sync_to_async
def add_refund(user_id, name, surname, course, stream, reason):
    refund_id = Refund.objects.create(user_id=user_id, name=name, surname=surname, course=course, stream=stream,
                                      reason=reason)
    return refund_id.id


async def close_request_in_database(request_id: int):
    """
    Окончательно закрывает заявку

    Args:
        request_id (int): ID заявки
    """
    try:
        # Используем sync_to_async для работы с синхронным кодом Django в асинхронной функции
        from asgiref.sync import sync_to_async

        @sync_to_async
        def _close():
            try:
                request = RequestModel.objects.get(id=request_id)
                request.status = 'closed'

                # Устанавливаем время резолюции
                from django.utils import timezone
                request.resolved_at = timezone.now()

                request.save()
                return True
            except RequestModel.DoesNotExist:
                logging.error(f"Заявка с ID {request_id} не найдена")
                return False
            except Exception as e:
                logging.error(f"Ошибка закрытия заявки: {e}")
                return False

        return await _close()

    except ImportError:
        logging.error("Не удалось импортировать необходимые модули")
        return False


async def update_request_status(request_id: int, status: str, file_path: str = None):
    """
    Обновляет статус заявки и добавляет файл записи разговора

    Args:
        request_id (int): ID заявки
        status (str): Новый статус заявки
        file_path (str, optional): Путь к файлу записи разговора
    """
    try:
        # Используем sync_to_async для работы с синхронным кодом Django в асинхронной функции
        from asgiref.sync import sync_to_async

        @sync_to_async
        def _update():
            try:
                request = RequestModel.objects.get(id=request_id)
                request.status = status

                # Если передан путь к файлу, обновляем поле с файлом
                if file_path:
                    from django.core.files import File
                    request.details = File(open(file_path, 'rb'))

                # Устанавливаем время резолюции, если статус финальный
                if status in ['completed', 'rejected']:
                    from django.utils import timezone
                    request.resolved_at = timezone.now()

                request.save()
                return True
            except RequestModel.DoesNotExist:
                logging.error(f"Заявка с ID {request_id} не найдена")
                return False
            except Exception as e:
                logging.error(f"Ошибка обновления заявки: {e}")
                return False

        return await _update()

    except ImportError:
        logging.error("Не удалось импортировать необходимые модули")
        return False


async def update_refund_status(request_id: int, status: str):
    """
    Обновляет статус заявки и добавляет файл записи разговора

    Args:
        request_id (int): ID заявки
        status (str): Новый статус заявки
        file_path (str, optional): Путь к файлу записи разговора
    """
    try:
        # Используем sync_to_async для работы с синхронным кодом Django в асинхронной функции
        from asgiref.sync import sync_to_async

        @sync_to_async
        def _update():
            try:
                request = Refund.objects.get(id=request_id)
                request.status = status

                request.save()
                return True
            except Refund.DoesNotExist:
                logging.error(f"Заявка с ID {request_id} не найдена")
                return False
            except Exception as e:
                logging.error(f"Ошибка обновления заявки: {e}")
                return False

        return await _update()

    except ImportError:
        logging.error("Не удалось импортировать необходимые модули")
        return False


async def download_media(message, destination_dir: str = "call_records"):
    """
    Универсальный метод сохранения файлов с поддержкой всех типов
    """
    # Список возможных типов файлов
    file_types = [
        ('document', message.document),
        ('audio', message.audio),
        ('video', message.video),
        ('voice', message.voice),
        ('video_note', message.video_note)
    ]

    # Находим первый непустой тип файла
    for file_type, file_object in file_types:
        if file_object:
            try:
                # Генерируем уникальное имя файла
                unique_filename = f"{file_type}_{message.message_id}_{file_object.file_unique_id}"
                file = await file_object.download(
                    destination=os.path.join(destination_dir, unique_filename)
                )
                return file.name
            except Exception as e:
                logging.error(f"Ошибка при сохранении {file_type}: {e}")
                return None

    return None


@sync_to_async
def get_contacts(role: str = 'sales_department', contact_type: str = 'phone'):
    """
    Получение контактов для различных отделов

    :param role: Роль контакта ('sales_department', 'curator', 'support')
    :param contact_type: Тип возвращаемых данных ('phone', 'username')
    :return: Список контактов
    """
    try:
        # Фильтрация по роли
        contacts = ContactInfo.objects.filter(role=role)

        # Определение возвращаемых полей
        if contact_type == 'phone':
            # Возвращаем номер телефона и имя
            return [
                {
                    'phone_number': contact.phone_number,
                    'name': contact.name or 'Без имени'
                }
                for contact in contacts
            ]
        elif contact_type == 'username':
            # Возвращаем username и имя
            return [
                {
                    'username': contact.tg_username,
                    'name': contact.name or 'Без имени'
                }
                for contact in contacts
            ]
        else:
            # Возвращаем все доступные данные
            return [
                {
                    'phone_number': contact.phone_number,
                    'username': contact.tg_username,
                    'name': contact.name or 'Без имени',
                    'role': contact.get_role_display()
                }
                for contact in contacts
            ]

    except Exception as e:
        logging.error(f"Ошибка при получении контактов: {e}")
        return []


@sync_to_async
def get_user_by_id(user_id: int):
    try:
        return User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return None


@sync_to_async
def update_user(user_id: int, phone_number: str, full_name: str):
    try:
        user = User.objects.get(user_id=user_id)
        user.phone = phone_number
        user.full_name = full_name
        user.save()
        return True
    except User.DoesNotExist:
        return False


@sync_to_async
def save_question(user_id: int, question_text: str) -> int:
    """
    Сохраняет вопрос в базе данных

    :param user_id: ID пользователя
    :param question_text: Текст вопроса
    :return: ID сохраненного вопроса
    """
    try:
        question = Question.objects.create(
            user_id=user_id,
            question=question_text,
        )
        return question.id
    except Exception as e:
        raise ValueError(f"Ошибка при сохранении вопроса: {str(e)}")


@sync_to_async
def get_question(question_id: int) -> dict:
    """
    Получает информацию о вопросе по его ID

    :param question_id: ID вопроса
    :return: Словарь с информацией о вопросе или None
    """
    try:
        question = Question.objects.get(id=question_id)
        return {
            'id': question.id,
            'user_id': question.user_id,
            'question_text': question.question,
            'created_at': question.created_at
        }
    except Question.DoesNotExist:
        return None
    except Exception as e:
        raise ValueError(f"Ошибка при получении вопроса: {str(e)}")

@sync_to_async
def delete_question(question_id: int):
    """
    Удаляет вопрос по его ID

    :param question_id: ID вопроса
    :return: True, если удаление успешно
    """
    try:
        with transaction.atomic():
            # Получаем вопрос с блокировкой для обновления
            question = Question.objects.select_for_update().get(id=question_id)

            # Удаляем вопрос
            question.delete()

            return True
    except Question.DoesNotExist:
        raise ValueError(f"Вопрос с ID {question_id} не найден")
    except Exception as e:
        raise ValueError(f"Ошибка при удалении вопроса: {str(e)}")
