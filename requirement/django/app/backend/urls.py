from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("user_register", views.user_register),
    path("auth/login", views.UserLogin, name="userLogin"),
    path("auth/register", views.UserRegister, name="userRegister"),
    path("auth/logout", views.UserLogout, name="userLogout"),
    path("users/<int:user_id>/profile", views.UserProfile, name="userProfile"),
    path("users/profile", views.OwnerProfile, name="ownerProfile"),
    path("users/update_avatar", views.UpdateUserAvatar, name="updateUserAvatar"),
    path("users/<int:user_id>/notifications/friend_request", views.SendFriendRequest, name="sendFriendRequest"),
    path("users/notifications", views.GetNotifications, name="getNotifications"),
    path("users/<int:user_id>/friends/accept", views.AcceptFriend, name="acceptFriend"),
    path("users/friends", views.GetAllFriends, name="getAllFriend"),
    path("users/friends/find_new", views.FindNewFriends, name="findNewFriends"),
    path("users/<int:user_id>/notifications/delete", views.DeleteNotification, name="deleteNotification"),
    path("users/<int:user_id>/block", views.BlockUser, name="blockUser"),
    path("users/blocked_list", views.GetUserBlockedList, name="getUserBlockedList"),
    path("users/<int:user_id>/unblock", views.UnblockUser, name="unblockUser"),
    path("get_csrf_token_and_session_id/", views.get_csrf_token_and_session_id, name="csrft_session"),
]