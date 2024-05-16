from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.
class MyUserManager(BaseUserManager):
    def create_user(self, email,password,**kwargs):
        if not email:
            raise ValueError('Users must provide an email address')
        if not password:
            raise ValueError('Users must provide a password')
        
        user = self.model(
            email = self.normalize_email(email),
            **kwargs
        )

        password = user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email,password,**kwargs):
        if not email:
            raise ValueError('Users must provide an email address')
        if not password:
            raise ValueError('Users must provide a password')
        
        user = self.model(
            email = self.normalize_email(email),
            **kwargs
        )
        user.is_superuser = True
        password = user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(max_length=100, unique= True, blank=False)    
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        return self.email
    


class WatchList(models.Model):
    symbol = models.CharField(max_length = 7, blank=False)
    user = models.ForeignKey(User, related_name='watchlist',on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(name="unique_user_symbol",fields=["symbol","user"])
        ]

    def save(self, *args, **kwargs):
        self.symbol = self.symbol.upper()
        super(WatchList,self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.symbol

def upload_path(instance,filename):
    return '/'.join(['static',filename])

class Plotting(models.Model):
    plot = models.ImageField(blank=True)
    user = models.ForeignKey(User,related_name='plotting',on_delete=models.CASCADE)
