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
        fields = ("user_id", "user_email", "user_name", "user_img", "user_bgimg", "user_gender")


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

class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ("project_id", "user_id", "group_id", "project_topic")

# class ExploreSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Project
#         fields = ("project_id", "user_id", "group_id", "project_topic")

class NotifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("send_id", "receive_id", "notify_cont")

    def create(self, validated_data):
        send_id = validated_data['send_id']
        receive_id = validated_data['receive_id']
        notify_cont = validated_data['notify_cont']

        notify = Notification(
            send_id = send_id,
            receive_id = receive_id,
            notify_cont = notify_cont,
        )
        notify.save()
        return notify

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ("send_id", "receive_id", "request_cont")

    def create(self, validated_data):
        send_id = validated_data['send_id']
        receive_id = validated_data['receive_id']
        request_cont = validated_data['request_cont']

        request = Request(
            send_id = send_id,
            receive_id = receive_id,
            request_cont = request_cont,
        )
        request.save()
        return request

class Idea_createSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = ("project_id", "user_id", "parent_id", "idea_cont", "idea_senti", "is_forked")

    def create(self, validated_data):
        project_id = validated_data['project_id']
        user_id = validated_data['user_id']
        parent_id = validated_data['parent_id']
        idea_cont = validated_data['idea_cont']
        idea_senti = validated_data['idea_senti']
        is_forked = validated_data['is_forked']

        idea = Idea(
            project_id = project_id,
            user_id = user_id,
            parent_id = parent_id,
            idea_cont = idea_cont,
            idea_senti = idea_senti,
            is_forked = is_forked
        )
        idea.save()
        return idea

class Idea_locCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea_loc
        fields = ("idea_id", "idea_x", "idea_y", "idea_width", "idea_height")

    def create(self, validated_data):
        idea_id = validated_data['idea_id']
        idea_x = validated_data['idea_x']
        idea_y = validated_data['idea_y']
        idea_width = validated_data['idea_width']
        idea_height = validated_data['idea_height']

        idea_loc = Idea_loc(
            idea_id = idea_id,
            idea_x = idea_x,
            Idea_y = idea_y,
            Idea_width = idea_width,
            idea_height = idea_height,
        )
        idea_loc.save()
        return idea_loc