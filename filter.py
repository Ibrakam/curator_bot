from aiogram.filters import Filter
from course.models import User
from asgiref.sync import sync_to_async

@sync_to_async
def admin_id(user_id, role):
    user = User.objects.get(user_id=user_id)
    print(user.role)
    if user.role == role:
        print(user.id)
        return user.user_id



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
