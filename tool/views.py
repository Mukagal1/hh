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
from django.db.models import Q
from .utils import compute_similarity

def index(request):
    return redirect('login_view')

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print(user.userprofile.role)
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
        role = data.get('role')
        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'User already exists'}, status=400)
        user = User.objects.create_user(username=username, password=password)
        user.userprofile.role = role
        user.save()
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

    userskills = request.user.userprofile.skills.all()
    otherskills = Skill.objects.exclude(id__in=userskills)
    userrole = request.user.userprofile.role
    print(userrole)

    return render(request, 'skills.html', {'otherskills': otherskills, 'userskills': userskills, 'userrole': userrole})

@login_required
def tests(request):
    tests = Test.objects.all()
    return render(request, 'tests.html', {'tests': tests})

@login_required
def chats(request):
    user_profile = request.user.userprofile
    chats= Chat.objects.filter(sender=user_profile) | Chat.objects.filter(receiver=user_profile)
    users = User.objects.exclude(id=request.user.id)

    return render(request, 'chats.html', {'chats': chats, 'users': users, 'user': request.user})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if request.method == "POST":
        data = json.loads(request.body)
        message_text = data.get('text')
        sender = request.user.userprofile
        receiver = chat.receiver if chat.sender == sender else chat.sender
        message = Message.objects.create(chat=chat, sender=sender, receiver=receiver, text=message_text)
        return JsonResponse({"status": "ok", "message": message.text, "sender": message.sender.user.username, "created_at": message.created_at.strftime("%Y-%m-%d %H:%M:%S")})

    if request.user.userprofile != chat.sender and request.user.userprofile != chat.receiver:
        return HttpResponseBadRequest("You are not a participant of this chat")
    messages = Message.objects.filter(chat=chat)
    return render(request, 'chat_detail.html', {'chat': chat, 'messages': messages})

@login_required
def chat_with_user(request, user_id):
    user_profile = request.user.userprofile
    other_user_profile = get_object_or_404(UserProfile, user_id=user_id)

    # Проверяем, существует ли уже чат между этими пользователями
    chat = Chat.objects.filter(
        (Q(sender=user_profile) & Q(receiver=other_user_profile)) |
        (Q(sender=other_user_profile) & Q(receiver=user_profile))
    ).first()

    if not chat:
        # Создаем новый чат, если он не существует
        chat = Chat.objects.create(sender=user_profile, receiver=other_user_profile)

    return redirect('chat_detail', chat_id=chat.id)

@login_required
def search_user(request):
    query = request.GET.get('q', '').strip()
    if query:
        user = User.objects.filter(username__icontains=query).first()
        if user:
            return JsonResponse({"user_id": user.id, "username": user.username})
    return JsonResponse({})

@login_required
def profiles(request):
    users = UserProfile.objects.exclude(user=request.user)
    return render(request, 'users.html', {'users': users})

@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'user_detail.html', {'user': user})

@login_required
def set_resume(request):
    if request.method == "POST":
        resume = request.POST.get("resume")
        user_profile = request.user.userprofile
        user_profile.resume = resume
        user_profile.save()
        return redirect('profile', username=request.user.username)
    return redirect('profile', username=request.user.username)

@login_required
def search_candidates(request):
    users = []
    if request.method == "POST":
        search_text = request.POST.get("search_text", "").strip()
        if search_text:
            users = UserProfile.objects.exclude(user=request.user)
            ranked_users = sorted(
                users, key=lambda user: compute_similarity(user.resume, search_text), reverse=True
            )
            users = ranked_users

    return render(request, 'search_candidates.html', {'users': users})

@login_required
def add_skill(request):
    if request.method == "POST":
        data = json.loads(request.body)
        skill_name = data.get("skill")
        skill, created = Skill.objects.get_or_create(name=skill_name)
        if created:
            return JsonResponse({"id": skill.id})
        else:
            return JsonResponse({"message": "Скилл уже существует!"})
