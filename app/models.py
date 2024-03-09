from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.
class MyUserManager(BaseUserManager):
    def create_user(self, email, first_name,password,**kwargs):
        if not email:
            raise ValueError('Users must provide an email address')
        if not password:
            raise ValueError('Users must provide a password')
        
        user = self.model(
            email = self.normalize_email(email),
            first_name=first_name,
            **kwargs
        )

        password = user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, first_name,password,**kwargs):
        if not email:
            raise ValueError('Users must provide an email address')
        if not password:
            raise ValueError('Users must provide a password')
        
        user = self.model(
            email = self.normalize_email(email),
            first_name=first_name,
            **kwargs
        )
        user.is_superuser = True
        password = user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(max_length=100, unique= True, blank=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length = 150, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def get_short_name(self):
        return self.first_name

    def __str__(self) -> str:
        return self.email
    


class WatchList(models.Model):
    symbol = models.CharField(max_length = 7, blank=False, unique=True)
    user = models.ForeignKey(User, related_name='watchlist',on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.symbol = self.symbol.upper()
        super(WatchList,self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.symbol

def upload_path(instance,filename):
    return '/'.join(['covers',filename])

class Plotting(models.Model):
    plot = models.ImageField(blank=True)
    user = models.ForeignKey(User,related_name='plotting',on_delete=models.CASCADE)
