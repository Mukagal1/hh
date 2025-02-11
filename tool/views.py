from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import json
from django.http import JsonResponse, HttpResponseBadRequest

def index(request):
    return JsonResponse({"message": "Hello, world!"})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({"error": "Username and password are required"}, status=400)

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"message": "Login successful"}, status=200)
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return HttpResponseBadRequest("Invalid request method")
    
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')

            if not username:
                return JsonResponse({"error": "Username is required"}, status=400)
            if not email:
                return JsonResponse({"error": "Email is required"}, status=400)
            if not password or not confirm_password:
                return JsonResponse({"error": "Password and confirm password are required"}, status=400)
            if password != confirm_password:
                return JsonResponse({"error": "Passwords do not match"}, status=400)

            user = User.objects.create_user(username=username, email=email, password=password)
            return JsonResponse({"message": "User created successfully"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return HttpResponseBadRequest("Invalid request method")
    
def signout(request):
    logout(request)
    return JsonResponse({"message": "Signout successful"})