from django.db import models


# Create your models here.
class User(models.Model):
    CHOICE = (
        ('user', 'user'),
        ('sales_department', 'Отдел продаж'),
        ('curator', 'Куратор'),
        ('support', 'Поддержка'),
        ('refund', 'Возврат'),
    )

    user_id = models.IntegerField(unique=True)
    phone = models.CharField(max_length=20)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, choices=CHOICE, default='user')
    registration_date = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f"<User(id={self.user_id}, name='{self.full_name}')>"

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    start_date = models.DateField()

    def __repr__(self):
        return f"<Course(name='{self.name}')>"

    class Meta:
        db_table = 'courses'
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class RequestModel(models.Model):
    CHOICE = (
        ('sales_department', 'Отдел продаж'),
        ('support', 'Поддержка'),
    )

    user_id = models.IntegerField(null=False)
    department = models.CharField(max_length=100, choices=CHOICE, default='sales_department')
    request_type = models.CharField(max_length=100)
    status = models.CharField(default='pending', max_length=100)
    details = models.FileField(upload_to='call_records', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __repr__(self):
        return f"<RequestModel(user_id={self.user_id}, department='{self.department}')>"

    class Meta:
        db_table = 'requests'
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'


class Refund(models.Model):
    CHOICE = (
        ('pending', 'Ожидает'),
        ('approved', 'Возврат одобрен'),
        ('rejected', 'Возврат отклонен'),
    )

    user_id = models.IntegerField(null=False)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    stream = models.CharField(max_length=100)
    reason = models.TextField()
    status = models.CharField(default='pending', max_length=100, choices=CHOICE)
    admin_notes = models.TextField()

    def __repr__(self):
        return f"<Refund(user_id={self.user_id}, course='{self.course}')>"

    class Meta:
        db_table = 'refunds'
        verbose_name = 'Возврат'
        verbose_name_plural = 'Возвраты'


class ContactInfo(models.Model):
    CHOICE = (
        ('sales_department', 'Отдел продаж'),
        ('curator', 'Куратор'),
        ('support', 'Поддержка'),
    )

    phone_number = models.CharField(max_length=20)
    tg_username = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=100, choices=CHOICE, default='sales_department')

    def __repr__(self):
        return f"<ContactInfo(phone_number={self.phone_number}, tg_username='{self.tg_username}')>"

    def __str__(self):
        return self.tg_username

    class Meta:
        db_table = 'contact_info'
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'


class Question(models.Model):
    user_id = models.IntegerField()
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f"<Question(user_id={self.user_id}, question='{self.question}')>"

    class Meta:
        db_table = 'questions'
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
