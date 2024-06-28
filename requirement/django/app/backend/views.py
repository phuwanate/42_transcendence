import os
import json
from django.urls import reverse
from django.conf import settings
from .models import Notification
from django.shortcuts import render, redirect
from django.middleware.csrf import get_token
from django.contrib.sessions.models import Session
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, get_user_model

DEFAULT_AVATAR = f'avatars/default.png'

def get_csrf_token_and_session_id(request):
    csrf_token = get_token(request)
    session_id = request.session.session_key
    return JsonResponse({'csrf_token': csrf_token, 'sessionid': session_id}, status=200)


def index(request):
    return render(request, 'backend/login.html')

def user_register(request):
    return render(request, 'backend/register.html')

#1.1 /api/auth/login
def UserLogin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if request.user.is_authenticated:
            return JsonResponse({'error': 'User is already logged in'}, status=400)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            avatar_url = f'{settings.MEDIA_ROOT}/{user.avatar}'
            if avatar_url and os.path.exists(avatar_url):
                pass
            else:
                user.avatar = DEFAULT_AVATAR
            login(request, user)
            user.is_online = True
            user.save()
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=401)    
        return JsonResponse({'message': 'Login success'}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
#1.2 /api/auth/register
def UserRegister(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        avatar = request.FILES.get('avatar')
        
        if not username or not password:
            return JsonResponse({'error': 'Both username and password are required'}, status=400)
       
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, password=password)
        if avatar:
            user.avatar = avatar
        user.save()
        
        return JsonResponse({'message': 'Create user success'}, status=201)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#1.3 /api/auth/logout
def UserLogout(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            User = get_user_model()
            user = User.objects.get(id=request.user.id)
            user.is_online = False
            user.save()
            logout(request)
            return JsonResponse({'message': 'Logout success'}, status=200)
        else:
            return JsonResponse({'error': 'User is not logged in'}, status=401)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

#2.1.1 /api/users/:user_id/profile
def getUserProfile(User, user):        
    return( {
        'id': user.id,
        'username': user.username,
        'avatar': user.avatar.url,
        'is_online': user.is_online
    })

def UserProfile(request, user_id):
    if request.method == 'GET':
        try:
            if request.user.is_authenticated:
                User = get_user_model()
                user = User.objects.get(id = user_id)
                avatar_url = f'{settings.MEDIA_ROOT}/{user.avatar}'
                if avatar_url and os.path.exists(avatar_url):
                    payload = getUserProfile(User=User, user=user)
                else:
                    return JsonResponse({'error': 'Not Found the avatar file'}, status=404) 
                return JsonResponse(payload, status=200, safe=False)
            else:
                return JsonResponse({'error': 'User is not logged in'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#2.1.2 /api/users/update_avatar
def UpdateUserAvatar(request):
    if request.method == 'POST': 
        try:
            if request.user.is_authenticated:
                User = get_user_model()
                user = User.objects.get(id = request.user.id)
                avatar = request.FILES.get('avatar')
                if avatar:
                    old_avatar_path = user.avatar
                    if old_avatar_path != f'avatars/default.png' and os.path.isfile(f'{settings.MEDIA_ROOT}/{old_avatar_path}'):
                        os.remove(f'{settings.MEDIA_ROOT}/{old_avatar_path}')
                    user.avatar = avatar
                    user.save()
                    return JsonResponse({'message': 'User update avatar success'}, status=200)
 
                else:
                    return JsonResponse({'error': 'Not Found the avatar file'}, status=404) 
            else:
                return JsonResponse({'error': 'User is not logged in'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404) 
            
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
#2.2.1 GET /api/users/:user_id/friends
def GetAllFriends(request):
    if request.method == 'GET':
        try:
            if request.user.is_authenticated:
                User = get_user_model()
                user = User.objects.get(id=request.user.id)
                friend_set = user.friend.all()
                friends = [getUserProfile(User, friend) for friend in friend_set]
                return JsonResponse(friends, status=200 , safe=False)
            else:
                return JsonResponse({'error': 'User is not logged in'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#2.2.1 GET: /api/users/friends/find_new
def FindNewFriends(request):
    if request.method == 'GET':
        try:
            if request.user.is_authenticated:
                User = get_user_model()
                user = User.objects.get(id=request.user.id)
                not_friend_set =  User.objects.exclude(id=request.user.id).exclude(friend=user)
                not_friends = [getUserProfile(User, not_friend) for not_friend in not_friend_set]
                
                return JsonResponse(not_friends, status=200 , safe=False)
            else:
                return JsonResponse({'error': 'User is not logged in'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
#2.3.1 GET /api/users/notifications
def getUserNotification(User, noti):
    user = User.objects.get(id = noti.sender.id)
    return( {
        'noti_id': noti.id,
        'user_id': user.id,
        'username': user.username,
        'avatar': user.avatar.url,
        'is_online': user.is_online
    })
 
def GetNotifications(request):
    if request.method == 'GET':
        try:
            if request.user.is_authenticated:
                User = get_user_model()
                user = User.objects.get(id=request.user.id)
                notifications = Notification.objects.filter(accepter=user)
                requester = [getUserNotification(User, noti) for noti in notifications]
                return JsonResponse(requester, status=200 , safe=False)
            else:
                return JsonResponse({'error': 'User is not logged in'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
#2.3.2 PUT: /api/users/:user_id/friends/accept
def AcceptFriend(request, user_id):
    if request.method == 'PUT':
        try:
            if request.user.is_authenticated:
                User = get_user_model()
                accpeter = User.objects.get(id=request.user.id)
                sender = User.objects.get(id=user_id)
                notification = Notification.objects.get(sender=sender, accepter=accpeter)
                notification.delete()
                accpeter.friend.add(user_id)
                accpeter.save()
                return JsonResponse({'message': 'Accept friend success'}, status=201)
            else:
                return JsonResponse({'error': 'User is not logged in'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#2.3.3 POST: /api/users/:user_id/notifications/friend_request 
def SendFriendRequest(request, user_id):
    if request.method == 'POST':
        try:
            if request.user.is_authenticated:
                User = get_user_model()
                accepter = User.objects.get(id = user_id)
                sender = User.objects.get(id = request.user.id)
                notification = Notification(sender=sender, accepter=accepter)
                notification.save()
                return JsonResponse({'message': 'Send friend request success'}, status=200)
            else:
                return JsonResponse({'message': 'User is not logged in'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404) 
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#2.3.4 DELETE: /api/users/:user_id/notifications/delete
def DeleteNotification(request, user_id):
    if request.method == 'DELETE':
        try:
            if request.user.is_authenticated:
                User = get_user_model()
                accpeter = User.objects.get(id=request.user.id)
                sender = User.objects.get(id=user_id)
                notification = Notification.objects.get(sender=sender, accepter=accpeter)
                notification.delete()
                return JsonResponse({'message': 'Delete Notificantion Success'}, status=200)
            else:
                return JsonResponse({'message': 'User is not logged in'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)