from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from .serializers import *
from knox.models import AuthToken
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
# from categoryclassifier.Bi_LSTM import Classifier
from django.utils import timezone
from urllib.request import urlopen
from urllib.request import HTTPError
from bs4 import BeautifulSoup
from django.db.models import F
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types



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

class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

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

# Main 페이지에 접근 할 때 로그인한 해당 유저의 그룹 정보
class GroupAPI(generics.GenericAPIView):
    def post(self, request):
        group = Group_entry.objects.filter(user_id=request.data['user_id']).values('group_id')
        temp = []
        test = []
        for a in group:
            temp.append(a['group_id'])
            group_content = Group.objects.filter(group_id=a['group_id']).values('group_id', 'group_name', 'group_intro', 'group_bgimg', 'group_img')
            test.append(group_content[0])
        return Response(
            test
        )

# Main, 개인페이지, 그룹페이지에서의 카테고리별 프로젝트 내용을 뿌려주는 부분
class ProjectAPI(generics.GenericAPIView):
    def post(self, request):

        if(request.data['group_id'] == 0):
            user_topic = Project.objects.filter(user_id_id=request.data['user_id']).values('project_topic', 'project_tendency','created_at').order_by('-created_at')
            Project_result = {"Society" : [], "Sport" : [], "It" : [], "Politics" : [], "Economy" : [], "Life" : []}
            for a in user_topic:
                if(a["project_tendency"] == "society"):
                    Project_result["Society"].append(a)
                elif(a["project_tendency"] == "it"):
                    Project_result["It"].append(a)
                elif (a["project_tendency"] == "sport"):
                    Project_result["Sport"].append(a)
                elif (a["project_tendency"] == "politics"):
                    Project_result["Politics"].append(a)
                elif (a["project_tendency"] == "Economy"):
                    Project_result["It"].append(a)
                elif (a["project_tendency"] == "Life"):
                    Project_result["Life"].append(a)

            return Response(
                Project_result
            )
        if(request.data['user_id']==0):
            topic = Project.objects.filter(group_id_id=request.data['group_id']).values('project_topic', 'project_img', 'project_tendency').order_by('-created_at')
            Project_result = {"Society": [], "Sport": [], "It": [], "Politics": [], "Economy": [], "Life": []}
            for a in topic:
                if (a["project_tendency"] == "society"):
                    Project_result["Society"].append(a)
                elif (a["project_tendency"] == "it"):
                    Project_result["It"].append(a)
                elif (a["project_tendency"] == "sport"):
                    Project_result["Sport"].append(a)
                elif (a["project_tendency"] == "politics"):
                    Project_result["Politics"].append(a)
                elif (a["project_tendency"] == "Economy"):
                    Project_result["It"].append(a)
                elif (a["project_tendency"] == "Life"):
                    Project_result["Life"].append(a)

            return Response(
                Project_result
            )

# Explore 페이지의 간지네모(네이버 뉴스 크롤링) 뿌려주는 부분
class NewsAPI(generics.GenericAPIView):
    def get(self, request):
        try:
            html = urlopen("https://news.naver.com/main/home.nhn")
            bsobj = BeautifulSoup(html, "html.parser")

        except HTTPError as e:
            print(e)

        array = [None] * 6

        for i in range(6):
            array[i] = dict([
                ("Category", None),
                ("Comment", None),
                ("img_src", None),
                ("img_href", None),
            ])
        i = 0

        # Category 크롤링
        try:
            for headline in bsobj.findAll("h4", {"class": "tit_sec"}):
                array[i]['Category'] = headline.get_text()
                i += 1

        # http((?!\").)*
        except AttributeError as e:
            print(e)

        i = 0
        # 주석 크롤링
        try:
            for headline1 in bsobj.findAll('dd'):
                array[i]['Comment'] = headline1.get_text()
                i += 1

        # http((?!\").)*
        except AttributeError as e:
            print(e)

        i = 0
        # img src & href 크롤링
        test = bsobj.findAll('dl', attrs={"class": "mtype_img"})

        try:
            for headline1 in test:
                array[i]['img_src'] = headline1.find('img').get('src')
                array[i]['img_href'] = headline1.find('a').get('href')
                i += 1

        # http((?!\").)*
        except AttributeError as e:
            print(e)

        return Response(
            array
        )

# Main, Explore 페이지에서 사용자에게 프로젝트 추천
class Project_recommendAPI(generics.GenericAPIView):
    def post(self, request):
        temp = []
        user_tendency = Person_tendency.objects.filter(user_id=request.data['user_id']).values('user_tendency')
        temp.append(user_tendency[0]['user_tendency'])
        project_tendency = Project.objects.filter(project_tendency=temp[0]).values('project_id', 'project_topic', 'project_img','project_intro', 'project_hits', 'project_likes', 'project_tendency', 'user_id', 'group_id')
        return Response(
            project_tendency
        )

# Explore 페이지에서 유행하는 프로젝트 추천
class Popular_projectAPI(generics.GenericAPIView):
    def get(self, request):
        projects = Project.objects.annotate(sum = F('project_hits') + F('project_likes')).values('project_id', 'project_topic', 'project_img', 'project_intro', 'project_tendency', 'project_likes', 'project_hits', 'user_id', 'group_id').order_by("-sum")
        return Response(
            projects
        )

# 여러 페이지에서 Notification에 접근할 때 알림
class NotifyAPI(generics.GenericAPIView):
    serializer_class = NotifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notify = serializer.save()
        return Response(
            {
                "send_id" : notify.send_id_id,
                "receive_id" : notify.receive_id,
                "notify_cont" : notify.notify_cont,
            }
        )
# 모든 페이지에서 검색 기능(User, Group, Project)
class SearchAPI(generics.RetrieveAPIView):

    def post(self, request):
        data = self.request.data['searchTo']

        # users search
        user_key = User.objects.filter(user_name__contains=data).values('user_id')
        user_id = []
        for a in user_key:
            user_id.append(a['user_id'])

        # follower, following
        follow_count = []
        for a in user_id:
            field = {"user_id": 0, "follower": 0, "following": 0}
            follower = Follow.objects.filter(partner_id=a).count()
            following = Follow.objects.filter(user_id_id=a).count()
            field['user_id'] = a
            field['follower'] = follower
            field['following'] = following
            follow_count.append(field)

        users = User.objects.filter(user_name__contains=data).values('user_id', 'user_name')

        user_values = []
        j = 0
        for b in users:
            user_values.append(b)
            user_values[j].update(follow_count[j])
            j += 1

        repositories = Project.objects.filter(project_topic__contains=data).values('project_id', 'project_topic', 'project_intro', 'project_hits', 'project_likes')

        # groups search
        group_key = Group.objects.filter(group_name__contains=data).values('group_id')
        group_id = []
        for a in group_key:
            group_id.append(a['group_id'])

        # groups member
        temp = []
        for a in group_id:
            groups = {"group_id": 0, "count": 0}
            test = Group_entry.objects.filter(group_id_id=a).count()
            groups['group_id'] = a
            groups['count'] = test
            temp.append(groups)

        groups = Group.objects.filter(group_name__contains=data).values('group_id', 'group_name', 'group_intro')

        testing = []
        i = 0
        for b in groups:
            testing.append(b)
            testing[i].update(temp[i])
            i += 1

        return Response(
            {
                "users": user_values,
                "repositories": repositories,
                "groups": testing,
            }
        )

# 여러 페이지에서 Reqeust에 접근할 때 알림
class RequestAPI(generics.GenericAPIView):
    serializer_class = RequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request = serializer.save()
        return Response(
            {
                "send_id" : request.send_id_id,
                "receive_id" : request.receive_id,
                "request_cont" : request.request_cont
            }
        )

# Notification 읽은 시간 수정
class Notify_readAPI(generics.GenericAPIView):
    def post(self, request):
        queryset = Notification.objects.filter(notify_id = request.data['notify_id'])
        queryset.update(read_at = timezone.localtime())
        return Response(
            "update success"
        )

# Request 수락 / 거부 여부
class Reqeust_acceptAPI(generics.GenericAPIView):
    def post(self, request):
        queryset = Request.objects.filter(request_id = request.data['request_id'])
        queryset.update(is_accepted  = True)
        return Response(
            "update success"
        )

# Check 페이지에서 Notification, Reqeust 데이터 불러오기
class CheckAPI(generics.GenericAPIView):
    def post(self, request):
        notifications = Notification.objects.filter(receive_id = request.data['user_id']).values("send_id", "notify_cont", "read_at")
        requests = Request.objects.filter(receive_id=request.data['user_id']).values("send_id", "request_cont", "is_accepted")
        temp = {"notifications" : [], "requests" : []}
        temp["notifications"] = notifications
        temp["requests"] = requests
        return Response(
            temp
        )

# 개인 페이지 Follower, Following 정보
class User_followAPI(generics.GenericAPIView):
    def post(self, request):
        follower = Follow.objects.filter(partner_id = request.data["user_id"]).values("user_id")
        follower_id = []
        for a in follower:
            follower_id.append(a["user_id"])
        follower_users = []
        for i in follower_id:
            follower_user = User.objects.filter(user_id = i).values("user_id", "user_name", "user_img", "user_gender")
            follower_users.append(follower_user[0])

        following = Follow.objects.filter(user_id = request.data["user_id"]).values("partner_id")
        following_id = []
        for a in following:
            following_id.append(a["partner_id"])
        following_users = []
        for i in following_id:
            following_user = User.objects.filter(user_id = i).values("user_id", "user_name", "user_img", "user_gender")
            following_users.append(following_user[0])

        for b in following:
            following_id.append(b)

        temp = {"follower" : [], "following" : []}
        temp["follower"] = follower_users
        temp["following"] = following_users

        return Response(
            temp
        )

# 그룹 페이지에서 그룹원들 정보
class Group_entryAPI(generics.GenericAPIView):
    def post(self, request):
        entry = Group_entry.objects.filter(group_id = request.data['group_id']).values("user_id")
        temp = []
        for a in entry:
            temp.append(a["user_id"])
        group_member = []
        for i in temp:
            member = User.objects.filter(user_id=i).values("user_id", "user_name", "user_img", "user_gender")
            group_member.append(member[0])
        return Response(
            group_member
        )

# 아이디어 CRUD
class Idea_createAPI(generics.GenericAPIView):
    serializer_class = Idea_createSerializer
    def post(self, request):
        client = language.LanguageServiceClient()
        text = request.data['idea_cont']
        document = types.Document(
            content = text,
            type = enums.Document.Type.PLAIN_TEXT
        )
        sentiment = client.analyze_sentiment(document=document).document_sentiment
        if(sentiment.score >= 0):
            request.data["idea_senti"] = "긍정"
        else:
            request.data["idea_senti"] = "부정"
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        idea = serializer.save()
        return Response(
            {
                "parent_id" : idea.parent_id,
                "user_id": idea.user_id_id,
                "project_id": idea.project_id_id,
                "Idea_cont": idea.idea_cont,
                "Idea_senti": idea.idea_senti,
                "is_forked": idea.is_forked
            }
        )

# Idea 위치 정보 저장
class Idea_locCreateAPI(generics.GenericAPIView):
    serializer_class = Idea_locCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        idea_loc = serializer.save()
        return Response(
            {
                "idea_id" : idea_loc.idea_id,
                "idea_x": idea_loc.idea_x,
                "idea_y": idea_loc.idea_y,
                "idea_width": idea_loc.idea_width,
                "idea_height": idea_loc.idea_height
            }
        )

# Idea 정보 수정
class Idea_updateAPI(generics.GenericAPIView):
    def post(self, request):
        client = language.LanguageServiceClient()
        text = request.data['idea_cont']
        document = types.Document(
            content=text,
            type=enums.Document.Type.PLAIN_TEXT
        )
        sentiment = client.analyze_sentiment(document=document).document_sentiment
        if (sentiment.score >= 0):
            request.data["idea_senti"] = "긍정"
        else:
            request.data["idea_senti"] = "부정"
        queryset = Idea.objects.filter(idea_id=request.data['idea_id'])
        queryset.update(
            idea_cont = request.data['idea_cont'],
            idea_senti = request.data['idea_senti'],
            is_forked = request.data['is_forked']
        )
        return Response(
            "update success"
        )

# Idea 위치 정보 수정
class Idea_locUpdateAPI(generics.GenericAPIView):
    def post(self, request):
        queryset = Idea_loc.objects.filter(idea_id=request.data['idea_id'])
        queryset.update(
            idea_x = request.data['idea_x'],
            idea_y = request.data['idea_y'],
            idea_width = request.data['idea_width'],
            idea_height = request.data['idea_height']
        )
        return Response(
            "update success"
        )

# Idea, Idea_loc 삭제
class Idea_deleteAPI(generics.GenericAPIView):
    def post(self, request):
        queryset = Idea.objects.filter(idea_id=request.data['idea_id'])
        queryset.delete()
        return Response(
            "delete success"
        )

# project 생성

