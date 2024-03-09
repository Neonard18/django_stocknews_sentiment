from rest_framework import serializers
from .models import WatchList, User, Plotting
from rest_framework.authtoken.models import Token

class WatchListSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.first_name')

    class Meta:
        model = WatchList
        fields = ['id','symbol','user']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','password','first_name','last_name']
        extra_kwargs = {'id':{'read_only':True}, 'password':{'write_only':True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)
        return user
    

class PlottingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plotting
        fields =['id','plot']
        # extra_kwargs = {'id':{'read_only':True},'plot':{'read_only':True}}

