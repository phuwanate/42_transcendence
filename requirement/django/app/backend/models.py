from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

############################## For Custom Auth User ##############################
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)
    score = models.IntegerField(default=0)
    # avatar = models.FileField(upload_to='avatars', blank=True, null=True, default='avatars/default.png')
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True, default='avatars/default.png')
    is_online = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    friend = models.ManyToManyField('self')
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
############################## For Custom Auth User ##############################

############################## Notification ##############################
class Notification(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='senders')
    accepter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='accpeters')
    date = models.DateTimeField(auto_now_add=True, null=True)
    class Meta:
        unique_together = ('sender', 'accepter')

    def __str__(self):
        return f"{self.sender.username} -> {self.accepter.username}"
############################## Notification ##############################

############################## Block List ##############################
class BlockedList(models.Model):
    blocker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='blockers')
    blocked = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='blocked')
    date = models.DateTimeField(auto_now_add=True, null=True)
    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f"{self.blocker.username} -> {self.blocked.username}"

############################## Block List ##############################
