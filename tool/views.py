from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Skill, UserProfile, Test, Chat, Message

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'ok', 'user': username,
                                 'role': user.userprofile.role})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=400)
    return render(request, 'login.html')

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'User already exists'}, status=400)
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return JsonResponse({'status': 'ok'})
    return render(request, 'signup.html')

def signout(request):
    logout(request)
    return redirect('login_view')

def main(request):
    return render(request, 'main.html')

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'profile.html', {'user': user})

@login_required
def skills(request):
    if request.method == "POST":
        skill_ids = request.POST.getlist("skills[]")  # Получаем список выбранных скиллов
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        selected_skills = Skill.objects.filter(id__in=skill_ids)
        
        user_profile.skills.add(*selected_skills)  # Добавляем новые скиллы пользователю

        return JsonResponse({"message": "Скиллы успешно добавлены!", "selected": list(skill_ids)})

    skills = Skill.objects.all()
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    return render(request, 'skills.html', {'skills': skills})

@login_required
def tests(request):
    tests = Test.objects.all()
    return render(request, 'tests.html', {'tests': tests})

@login_required
def chats(request):
    user_profile = request.user.userprofile
    chats = Chat.objects.filter(participants=user_profile)
    users = UserProfile.objects.exclude(id=user_profile.id)  # Все пользователи, кроме текущего

    return render(request, 'chats.html', {'chats': chats, 'users': users})

@login_required
def start_chat(request, user_id):
    user_profile = request.user.userprofile
    other_user = get_object_or_404(UserProfile, id=user_id)

    # Проверяем, есть ли уже чат
    chat = Chat.objects.filter(participants=user_profile).filter(participants=other_user).first()

    if chat:
        return redirect('chat_detail', chat.id)  # Если чат есть, открываем его

    # Создаем новый чат
    chat = Chat.objects.create()
    chat.participants.add(user_profile, other_user)
    return redirect('chat_detail', chat.id)


@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    messages = chat.message_set.all().order_by("created_at")  

    # Определяем собеседника
    companion = chat.participants.exclude(id=request.user.id).first()
    companion_username = companion.user.username if companion else "Неизвестный"

    if request.method == "POST":
        text = request.POST.get("message")
        if text:
            Message.objects.create(chat=chat, sender=request.user.userprofile, text=text)
            return redirect("chat_detail", chat_id=chat.id)  # Перезагрузка страницы для отображения нового сообщения

    return render(request, 'chat_detail.html', {
        'chat': chat,
        'messages': messages,
        'companion_username': companion_username if companion else "Аноним"
    })

@login_required
def send_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if request.method == "POST":
        text = request.POST.get('text')
        if text:
            Message.objects.create(chat=chat, sender=request.user.userprofile, text=text)

    return redirect('chat_detail', chat_id=chat.id)

@login_required
def search_user(request):
    query = request.GET.get('q', '').strip()
    if query:
        user = User.objects.filter(username__icontains=query).first()
        if user:
            return JsonResponse({"user_id": user.id, "username": user.username})
    return JsonResponse({})