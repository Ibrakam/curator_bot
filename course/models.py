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
    phone = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=100, choices=CHOICE, default='user')
    registration_date = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f"<User(id={self.user_id}, name='{self.full_name}')>"

    def __str__(self):
        return f"<User(id={self.user_id}, name='{self.full_name}', phone='{self.phone}')>"

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


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
    admin_notes = models.FileField(upload_to='call_records', null=True, blank=True)

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


class AnswerForComplain(models.Model):
    user_id = models.IntegerField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f"<AnswerForComplain(user_id={self.user_id}, answer='{self.answer}')>"

    class Meta:
        db_table = 'answers_for_complain'
        verbose_name = 'Ответ на жалобу'
        verbose_name_plural = 'Ответы на жалобы'


class Complaint(models.Model):
    user_id = models.IntegerField()
    complain = models.TextField()
    user_info = models.ForeignKey(User, on_delete=models.CASCADE, null=True, to_field='phone')
    created_at = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f"<Complaint(user_id={self.user_id}, complain='{self.complain}')>"

    class Meta:
        db_table = 'complaints'
        verbose_name = 'Жалоба'
        verbose_name_plural = 'Жалобы'
