from rest_framework import serializers
from .models import garden,User,message
#Serializers effectively constructs a their object based on their model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email','password','date_joined']
    def create(self, validated_data):
        user = User(email = validated_data['email'],
                    username = validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return(user)


class GardenSerializer(serializers.ModelSerializer):
    class Meta:
        model = garden
        fields = ['ownerID', 'date_created', 'longitude','latitude','bio', 'name']

class messageSerializer(serializers.ModelSerializer):
    class Meta:
        model = message
        fields = ['date_sent', 'gardenID', 'senderID','body']

