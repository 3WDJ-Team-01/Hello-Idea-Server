from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate

# 회원가입 시리얼라이저
class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("user_id", "user_email", "password", "user_name", "user_birth", "user_gender", "user_img", "user_bgimg", "created_at")

    def create(self, validated_data):
        email = validated_data['user_email']
        name = validated_data['user_name']
        password = validated_data['password']
        birth = validated_data['user_birth']
        gender = validated_data['user_gender']
        img = validated_data['user_img']
        bgimg = validated_data['user_bgimg']

        user_obj = User(
            user_email=email,
            user_name=name,
            user_birth=birth,
            user_gender=gender,
            user_img=img,
            user_bgimg=bgimg,
        )
        user_obj.set_password(password)
        user_obj.save()
        return user_obj

# 접속 유지중인지 확인할 시리얼라이저
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("user_id", "user_email", "user_name", "user_img", "user_bgimg")


# 로그인 시리얼라이저
class LoginUserSerializer(serializers.Serializer):
    user_email = serializers.CharField()
    password = serializers.CharField()

    # authenticate 함수는 self, username, password를 인자로 받은 후,
    # 정상적으로 인증된 경우 user 객체를 ‘하나’ 반환해야 하고, 없는 경우 None값을 반환해야 한다.
    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")

# # 개인 프로젝트 topic
# class UserTopicSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Project
#         fields = ("project_id", "user_id_id", "group_id_id", "project_topic", "project_img")
#
# # 단체 프로젝트 topic
# class GroupTopicSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group_entry
#         fields = ("group_id_id", "user_id_id")