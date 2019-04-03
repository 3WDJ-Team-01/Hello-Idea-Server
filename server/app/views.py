from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from .models import *
from .serializers import (
    LoginUserSerializer,
    UserSerializer,
    CreateUserSerializer,
)
from knox.models import AuthToken


class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user_id": user.user_id,
                "user_email": user.user_email,
                "user_name": user.user_name,
                "user_birth": user.user_birth,
                "user_gender": user.user_gender,
                "user_img": user.user_img,
                "user_bgimg": user.user_bgimg,
                "token": AuthToken.objects.create(user),
            }
        )


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user),
            }
        )


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

# class UserTopicAPI(generics.GenericAPIView):
#     serializer_class = UserTopicSerializer
#
#     def post(self, request):
#         key = Project.objects.filter(user_id_id=request.data['user_id']).values('project_topic', 'created_at').order_by('-created_at')
#         return Response(key)
#
# class GroupTopicAPI(generics.GenericAPIView):
#     serializer_class = GroupTopicSerializer
#
#     def post(self, request):
#         key = Group_entry.objects.filter(user_id_id=request.data['user_id']).values('group_id_id')
#         id = []
#         for a in key:
#             id.append(a['group_id_id'])
#         value = []
#         for a in id:
#             topic = Project.objects.filter(group_id_id=a).values('group_id', 'project_topic', 'created_at')
#             value.append(topic[0])
#         #sorted(value, key=lambda x: datetime.strptime(x, '%m-%Y'))
#
#         return Response(value)
#
#         # # follow 된 사람들의 프로젝트 topic
#         # key = Follow.objects.filter(user_id_id=request.data['user_id']).values('partner_id')
#         # test = []
#         # for a in key:
#         #     test.append(a['partner_id'])
#         # topic = []
#         # num = 0
#         # for a in test:
#         #     key = Project.objects.filter(user_id_id=a).values('project_topic', 'created_at')
#         #     name = User.objects.filter(user_id=a).values('user_name')
#         #     topic.append(key[0])
#         #     topic[num].update(name[0])
#         #     num += 1
#         # return Response(topic)