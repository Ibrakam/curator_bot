from aiogram.filters import Filter
from course.models import User
from asgiref.sync import sync_to_async


@sync_to_async(thread_sensitive=True)
def admin_id(role):
    return list(User.objects.filter(role=role).values_list("user_id", flat=True))

class IsCurator(Filter):
    async def __call__(self, message):
        user = await User.objects.get(user_id=message.from_user.id)
        if user.role == 'curator':
            return True
        return False


class IsSalesDepartment(Filter):
    async def __call__(self, message):
        user = await User.objects.get(user_id=message.from_user.id)
        if user.role == 'sales_department':
            return True
        return False


class IsSupport(Filter):
    async def __call__(self, message):
        user = await User.objects.get(user_id=message.from_user.id)
        if user.role == 'support':
            return True
        return False


class IsRefund(Filter):
    async def __call__(self, message):
        user = await User.objects.get(user_id=message.from_user.id)
        if user.role == 'refund':
            return True
        return False
