import logging
import os
from typing import Optional

from aiogram import types
from django.db import transaction

from course.models import (User, RequestModel, Refund,
                           ContactInfo, Question, AnswerForComplain,
                           Complaint)
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


async def update_refund_status(request_id: int, status: str, file_path: str = None):
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
                request.admin_notes = file_path

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


async def download_media(message: types.Message, destination_dir: str = "call_records") -> Optional[str]:
    """
    Универсальный метод сохранения файлов с поддержкой всех типов медиа
    """
    # Убедимся, что директория для сохранения существует
    # os.makedirs(destination_dir, exist_ok=True)

    try:
        # Для голосовых и аудио сообщений
        if message.voice:
            file = await message.bot.get_file(message.voice.file_id)
            file_path = os.path.join(destination_dir, f"voice_{message.message_id}_{message.voice.file_unique_id}.ogg")
            await message.bot.download_file(file.file_path, file_path)
            return file_path

        if message.audio:
            file = await message.bot.get_file(message.audio.file_id)
            # Используем расширение из mime_type или дефолтное
            ext = message.audio.mime_type.split('/')[-1] if message.audio.mime_type else 'mp3'
            file_path = os.path.join(destination_dir,
                                     f"audio_{message.message_id}_{message.audio.file_unique_id}.{ext}")
            await message.bot.download_file(file.file_path, file_path)
            return file_path

        # Для документов
        if message.document:
            file = await message.bot.get_file(message.document.file_id)
            file_path = os.path.join(destination_dir,
                                     message.document.file_name or f"document_{message.message_id}_{message.document.file_unique_id}")
            await message.bot.download_file(file.file_path, file_path)
            return file_path

        # Для видео
        if message.video:
            file = await message.bot.get_file(message.video.file_id)
            ext = message.video.mime_type.split('/')[-1] if message.video.mime_type else 'mp4'
            file_path = os.path.join(destination_dir,
                                     f"video_{message.message_id}_{message.video.file_unique_id}.{ext}")
            await message.bot.download_file(file.file_path, file_path)
            return file_path

        # Для видео-заметок
        if message.video_note:
            file = await message.bot.get_file(message.video_note.file_id)
            file_path = os.path.join(destination_dir,
                                     f"video_note_{message.message_id}_{message.video_note.file_unique_id}.mp4")
            await message.bot.download_file(file.file_path, file_path)
            return file_path

        logging.error(f"Неподдерживаемый тип файла: {message.content_type}")
        return None

    except Exception as e:
        logging.error(f"Ошибка при сохранении файла: {e}")
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
def update_user(user_id: int, phone_number: str, full_name: str, username: str):
    try:
        user = User.objects.get(user_id=user_id)
        user.phone = phone_number
        user.full_name = full_name
        user.username = username
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


@sync_to_async
def save_complaint(user_id: int, answer: str) -> int:
    """
    Сохраняет вопрос в базе данных

    :param user_id: ID пользователя
    :param answer: Текст вопроса
    :return: ID сохраненного вопроса
    """
    try:
        answer = AnswerForComplain.objects.create(
            user_id=user_id,
            answer=answer,
        )
        return answer.id
    except Exception as e:
        raise ValueError(f"Ошибка при сохранении вопроса: {str(e)}")


@sync_to_async
def get_answer(answer_id: int) -> dict:
    """
    Получает информацию о вопросе по его ID

    :param answer_id: ID вопроса
    :return: Словарь с информацией о вопросе или None
    """
    try:
        asnwer = AnswerForComplain.objects.get(id=answer_id)
        return {
            'id': asnwer.id,
            'user_id': asnwer.user_id,
            'answer': asnwer.answer,
            'created_at': asnwer.created_at
        }
    except AnswerForComplain.DoesNotExist:
        return {None: None}
    except Exception as e:
        raise ValueError(f"Ошибка при получении вопроса: {str(e)}")


@sync_to_async
def delete_answer(answer_id: int):
    """
    Удаляет вопрос по его ID

    :param answer_id: ID вопроса
    :return: True, если удаление успешно
    """
    try:
        with transaction.atomic():
            # Получаем вопрос с блокировкой для обновления
            answer = AnswerForComplain.objects.select_for_update().get(id=answer_id)

            # Удаляем вопрос
            answer.delete()

            return True
    except AnswerForComplain.DoesNotExist:
        raise ValueError(f"Вопрос с ID {answer_id} не найден")
    except Exception as e:
        raise ValueError(f"Ошибка при удалении вопроса: {str(e)}")


@sync_to_async
def add_complaint(user_id, complain):
    """
    Добавляет жалобу в базу данных

    :param user_id: ID пользователя
    :param complain: Текст жалобы
    :return: ID жалобы
    """
    try:
        with transaction.atomic():
            user = User.objects.select_for_update().get(user_id=user_id)
            complaint = Complaint.objects.create(
                user_id=user_id,
                user_info=user,
                complain=complain
            )
        return complaint.id
    except Exception as e:
        raise ValueError(f"Ошибка при сохранении жалобы: {str(e)}")


@sync_to_async
def get_all_complaint():
    """
    Получает информацию о жалобе по еей ID

    :return: Словарь с информацией о жалобе или None
    """
    try:
        complaint = Complaint.objects.all()
        complaint_list = []
        for i in complaint:
            complaint_list.append({
                'id': i.id,
                'user_id': i.user_id,
                'user_info': i.user_info,
                'complaint': i.complain
            })
        return complaint_list
    except Complaint.DoesNotExist:
        return None
    except Exception as e:
        raise ValueError(f"Ошибка при получении жалобы: {str(e)}")
