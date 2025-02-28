from django.contrib import admin
from .models import UserProfile, Skill, Chat, Message, Test, Question, Choice

admin.site.register(UserProfile)
admin.site.register(Skill)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Choice)
