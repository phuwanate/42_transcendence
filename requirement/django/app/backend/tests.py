import json
from django.test import Client
from django.test import TestCase
from django.conf import settings
from .models import Notification
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import authenticate, login, logout, get_user_model

CLIENT_NUMB = 10

# Create your tests here.
class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url ='/api/auth/login'
        self.payload = {
            "username": "user1234",
            "password": "password1234"
        }
        
    def test_login_success(self):
        """
            If login success should return 200
        """
        User = get_user_model()
        user = User.objects.create_user(username="user1234", password="password1234")
        
        response = self.client.post(
            self.login_url, 
            json.dumps(self.payload),
            content_type='application/json')
        updated_user = User.objects.get(username="user1234")
 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Login success')
        self.assertEqual(updated_user.is_online , True)
        
    def test_login_with_invalid_username(self):
        """
            If login with invalid username should return 401
        """
        User = get_user_model()
        user = User.objects.create_user(username="user1234", password="password1234")
        payload = {
            "username": "user12345",
            "password": "password1234"
        }
        
        response = self.client.post(
            self.login_url, 
            json.dumps(payload),
            content_type='application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['error'], 'Invalid username or password')
    
    def test_duplicate_login(self):
        """
            If user login 2 times with the same session 
        """
        User = get_user_model()
        user = User.objects.create_user(username="user1234", password="password1234")
        for i in range(2):        
            response = self.client.post(
            self.login_url, 
            json.dumps(self.payload),
            content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'User is already logged in')

    def test_login_with_method_not_allowed(self):
        """
            If login with invalid username should return 405
        """
        response = self.client.get(self.login_url,)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], 'Method not allowed')

class RegiterTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url ='/api/auth/register'
        self.payload = {
            "username": "user1234",
            "password": "password1234"
        }
        self.file_upload = {
            'name': 'test_avatar.jpg',
            'content': b'test image content',
            'content_type': 'image/jpeg'
        }
   
    def test_register_success(self):
        """
            Expect response body as a multipart/form-data
            If user registeration success should return status 201
        """
        avatar = SimpleUploadedFile(
            name=self.file_upload['name'],
            content=self.file_upload['content'],
            content_type=self.file_upload['content_type']
        )
        response = self.client.post(
            self.register_url,
            data={
                'username': self.payload['username'],
                'password': self.payload['password'],
                'avatar': avatar
            }
        )
        User = get_user_model()
        user = User.objects.get(username=self.payload['username'])
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], 'Create user success')
        self.assertEqual(user.avatar, f'avatars/{self.file_upload['name']}')
  
    def test_register_success_without_avatar(self):
        """
            Expect response body is multipart/form-data
            If user registered success should return status 201
        """
        response = self.client.post(
            self.register_url,
            data={
                'username': self.payload['username'],
                'password': self.payload['password'],
            }
        )
        User = get_user_model()
        user = User.objects.get(username=self.payload['username'])
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], 'Create user success')
        self.assertEqual(user.avatar, f'avatars/default.png')

    def test_register_with_method_not_allowed(self):
        """
            If login with invalid username should return 405
        """
        response = self.client.get(self.register_url,)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], 'Method not allowed')

class LogoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.client2 = Client()
        self.logout_url ='/api/auth/logout'
        self.login_url = '/api/auth/login'
        
        User = get_user_model()
        self.user = User.objects.create_user(username="user1234", password="password1234")
        self.payload = {
            "username": "user1234",
            "password": "password1234"
        }
        self.client.post(
            self.login_url, 
            json.dumps(self.payload),
            content_type='application/json')

    def test_logout_success(self):
        """
            If logout success should return 200
        """
        response = self.client.post(self.logout_url, content_type='application/json')
        User = get_user_model()
        updated_user = User.objects.get(username="user1234")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Logout success')
        self.assertEqual(updated_user.is_online, False)

    def test_logout_failed(self):
        """
            If logout before login should return 401
        """
        response = self.client2.post(self.logout_url, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['error'], 'User is not logged in')

    def test_logout_with_method_not_allowed(self):
        """
            If logout with method other than POST should return 405
        """
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], 'Method not allowed')

class UserProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url ='/api/users/'
        User = get_user_model()
        self.user = User.objects.create_user(username="user1234", password="password1234")
        self.payload = {
            "username": "user1234", 
            "password": "password1234"
        }
        response = self.client.post(
            "/api/auth/login", 
            json.dumps(self.payload),
            content_type='application/json')
    
    def test_exist_user_profile(self):
        payload = {
	        "id": 1,
	        "username": "user1234",
	        "avatar": f"{settings.MEDIA_URL}avatars/default.png",
	        "is_online": True 
        }
        response = self.client.get(f'{self.url}{self.user.id}/profile')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), payload)

class UpdateUserAvatarTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url ='/api/users/'
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username="user1234", password="password1234")
        self.payload = {
            "username": "user1234",
            "password": "password1234"
        }
        self.file_upload = {
            'name': 'test_avatar2.jpg',
            'content': b'test image content',
            'content_type': 'image/jpeg'
        }
        response = self.client.post(
            "/api/auth/login", 
            json.dumps(self.payload),
            content_type='application/json')

    def test_update_user_avatar_success(self):
        """
            if success new avatar path should not be the same as the old avatar path.
        """
        avatar = SimpleUploadedFile(
            name=self.file_upload['name'],
            content=self.file_upload['content'],
            content_type=self.file_upload['content_type']
        )
        #/api/users/:id/update_avatar
        response = self.client.post(
            f'{self.url}update_avatar',
            data={
                'avatar': avatar
            },
        )
        
        update_user = self.User.objects.get(username="user1234")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'User update avatar success')
        self.assertNotEqual(update_user.avatar, self.user.avatar)
    
    def test_update_user_avatar_with_empty_file(self):
        """
            If upload empty file should return 404 Not found the avatar file
        """
        response = self.client.post(
            f'{self.url}update_avatar',
            data={ },
        )
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'Not Found the avatar file')

class SendFriendRequest(TestCase):
    def setUp(self):
        self.url ='/api/users/'
        self.User = get_user_model()
        self.client = [Client() for i in range(CLIENT_NUMB)]
        self.user = [self.User.objects.create_user(username=f"user{i+1}", password=f"password{i+1}") for i in range(CLIENT_NUMB)]
        self.payload = [{"username": f"user{i+1}", "password": f"password{i+1}"} for i in range(CLIENT_NUMB)]
        
        for i in range(CLIENT_NUMB):
            self.client[i].post(
                "/api/auth/login", 
                json.dumps(self.payload[i]),
                content_type='application/json')
    
    def test_send_friend_request_success(self):
        """
            If success notification table should map correct sender and accepter to table.
        """ 
        for i in range(CLIENT_NUMB - 1):
           response = self.client[i].post(f'{self.url}{self.user[CLIENT_NUMB - 1].id}/notifications/friend_request')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Send friend request success')

class GetNotificationTest(TestCase):
    def setUp(self):
        self.url ='/api/users/'
        self.User = get_user_model()
        self.client = [Client() for i in range(CLIENT_NUMB)]
        self.user = [self.User.objects.create_user(username=f"user{i+1}", password=f"password{i+1}") for i in range(CLIENT_NUMB)]
        self.payload = [{"username": f"user{i+1}", "password": f"password{i+1}"} for i in range(CLIENT_NUMB)]
        for i in range(CLIENT_NUMB):
            self.client[i].post(
            "/api/auth/login", 
            json.dumps(self.payload[i]),
            content_type='application/json')
        for i in range(CLIENT_NUMB - 1):
            self.client[i].post(f'{self.url}{self.user[CLIENT_NUMB - 1].id}/notifications/friend_request')

    def test_get_notification_success(self):
        response = self.client[CLIENT_NUMB - 1].get(f'{self.url}notifications')
        expected_load = [
                {
                    'noti_id': i + 1,
                    'user_id': self.user[i].id,
                    'username': self.user[i].username,
                    'avatar': self.user[i].avatar.url,
                    'is_online': True
                }
                for i in range(CLIENT_NUMB - 1)
            ]
        # print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_load)

class AcceptFriend(TestCase):
    def setUp(self):
        self.url ='/api/users/'
        self.User = get_user_model()
        self.client = [Client() for i in range(CLIENT_NUMB)]
        self.user = [self.User.objects.create_user(username=f"user{i+1}", password=f"password{i+1}") for i in range(CLIENT_NUMB)]
        self.payload = [{"username": f"user{i+1}", "password": f"password{i+1}"} for i in range(CLIENT_NUMB)]
        for i in range(CLIENT_NUMB):
            self.client[i].post(
            "/api/auth/login", 
            json.dumps(self.payload[i]),
            content_type='application/json')
        for i in range(CLIENT_NUMB - 1):
            self.client[i].post(f'{self.url}{self.user[CLIENT_NUMB - 1].id}/notifications/friend_request')
    
    def test_accept_friend_success(self):
        """
            If accept success the last user should be freind with all users.
            Notification should decrement by CLIENT_NUMB - 1.
        """
        #Before
        response = self.client[CLIENT_NUMB - 1].get(f'{self.url}notifications')
        notification = response.json()

        for i in range(CLIENT_NUMB - 1):
            sender_id = notification[i]['user_id']
            accept_response = self.client[CLIENT_NUMB - 1].put(f'{self.url}{sender_id}/friends/accept')
        #After
        new_response = self.client[CLIENT_NUMB - 1].get(f'{self.url}notifications')
        new_notification = new_response.json()

        self.assertEqual(accept_response.status_code, 201)
        self.assertEqual(accept_response.json()['message'], 'Accept friend success')
        self.assertNotEqual(len(notification), len(new_notification))
        
        #Query friend's id to compare with all users'id that was send friend request to the last user.
        update_user = self.User.objects.get(id=self.user[CLIENT_NUMB - 1].id)
        friend = update_user.friend.all()
        for i in range(CLIENT_NUMB - 1):
            self.assertEqual(self.user[i].id, friend[i].id)

class GetAllFriend(TestCase):
    def setUp(self):
        self.url ='/api/users/'
        self.User = get_user_model()
        self.client = [Client() for i in range(CLIENT_NUMB)]
        self.user = [self.User.objects.create_user(username=f"user{i+1}", password=f"password{i+1}") for i in range(CLIENT_NUMB)]
        self.payload = [{"username": f"user{i+1}", "password": f"password{i+1}"} for i in range(CLIENT_NUMB)]
        for i in range(CLIENT_NUMB):
            self.client[i].post(
            "/api/auth/login", 
            json.dumps(self.payload[i]),
            content_type='application/json')
        for i in range(CLIENT_NUMB - 1):
            self.client[i].post(f'{self.url}{self.user[CLIENT_NUMB - 1].id}/notifications/friend_request')
    
    def test_get_all_friend_success(self):
        """
            If success should return list of friends include all users but the last user.
        """
        for i in range(CLIENT_NUMB - 1):
            self.client[CLIENT_NUMB - 1].put(f'{self.url}{self.user[i].id}/friends/accept')
        response = self.client[CLIENT_NUMB - 1].get(f'{self.url}friends')

        expected_load = [
                {
                    'id': self.user[i].id,
                    'username': self.user[i].username,
                    'avatar': self.user[i].avatar.url,
                    'is_online': True
                }
                for i in range(CLIENT_NUMB - 1)
            ]
        # print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_load)
        
class FindNewFriend(TestCase):
    def setUp(self):
        self.url ='/api/users/'
        self.User = get_user_model()
        self.client = [Client() for i in range(CLIENT_NUMB)]
        self.user = [self.User.objects.create_user(username=f"user{i+1}", password=f"password{i+1}") for i in range(CLIENT_NUMB)]
        self.payload = [{"username": f"user{i+1}", "password": f"password{i+1}"} for i in range(CLIENT_NUMB)]
        for i in range(CLIENT_NUMB):
            self.client[i].post(
            "/api/auth/login", 
            json.dumps(self.payload[i]),
            content_type='application/json')
        for i in range(CLIENT_NUMB - 1):
            self.client[i].post(f'{self.url}{self.user[CLIENT_NUMB - 1].id}/notifications/friend_request')
    def test_find_new_friend_success(self):
        """
            the last client accept for incoming 1st client friend request.
            if success should return JSON with user_profile CELIENT_NUMB items exclude 1st and last client.
        """
        self.client[CLIENT_NUMB - 1].put(f'{self.url}{self.user[0].id}/friends/accept')
        expected_load = [
                {
                    'id': self.user[i].id,
                    'username': self.user[i].username,
                    'avatar': self.user[i].avatar.url,
                    'is_online': True
                }
                for i in range(CLIENT_NUMB - 1) if i != 0
            ]
        response = self.client[CLIENT_NUMB - 1].get(f'{self.url}friends/find_new')
        # print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_load)

class DeleteNotification(TestCase):
    def setUp(self):
        self.url ='/api/users/'
        self.User = get_user_model()
        self.client = [Client() for i in range(CLIENT_NUMB)]
        self.user = [self.User.objects.create_user(username=f"user{i+1}", password=f"password{i+1}") for i in range(CLIENT_NUMB)]
        self.payload = [{"username": f"user{i+1}", "password": f"password{i+1}"} for i in range(CLIENT_NUMB)]
        for i in range(CLIENT_NUMB):
            self.client[i].post(
            "/api/auth/login", 
            json.dumps(self.payload[i]),
            content_type='application/json')
        for i in range(CLIENT_NUMB - 1):
            self.client[i].post(f'{self.url}{self.user[CLIENT_NUMB - 1].id}/notifications/friend_request')
    
    def test_delete_notification_success(self):
        """
            If success notification should disappear 1 item.
        """
        before  = self.client[CLIENT_NUMB - 1].get(f'{self.url}notifications')
        
        
        response = self.client[CLIENT_NUMB - 1].delete(f'{self.url}{self.user[0].id}/notifications/delete')
        after = self.client[CLIENT_NUMB - 1].get(f'{self.url}notifications')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Delete Notificantion Success')
        self.assertNotEqual(before.json(), after.json())