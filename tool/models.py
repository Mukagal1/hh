from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

# Пользовательский профиль
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('boss', 'Boss'),
        ('hr', 'HR'),
        ('user', 'User'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    skills = models.ManyToManyField('Skill', blank=True)
    resume = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

# Навыки пользователей
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Чат между пользователями
class Chat(models.Model):
    sender = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name='sender', default=None)    
    receiver = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name='receiver', default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id}"

# Сообщения в чате
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey("UserProfile", related_name='sent_messages', on_delete=models.CASCADE, default=None)
    receiver = models.ForeignKey("UserProfile", related_name='received_messages', on_delete=models.CASCADE, default=None)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Правильное поле

    def __str__(self):
        return f"{self.sender.user.username}: {self.receiver.user.username} - {self.text}"

class Test(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = (
        ('MC', 'Multiple Choice'),
        ('TF', 'True/False'),
    )
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES)

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField()

    def __str__(self):
        return self.text

