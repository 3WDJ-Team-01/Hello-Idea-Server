from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from .serializers import *
from knox.models import AuthToken
from categoryclassifier.Bi_LSTM import Classifier
from django.utils import timezone
from urllib.request import urlopen
from urllib.request import HTTPError
from bs4 import BeautifulSoup
from django.db.models import F
from django.db.models.functions import ExtractDay
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from konlpy.tag import Hannanum
import six

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
            user_topic = Project.objects.filter(user_id=request.data['user_id']).values('project_id','project_topic', 'project_tendency','created_at').order_by('-updated_at')
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
                elif (a["project_tendency"] == "economy"):
                    Project_result["It"].append(a)
                elif (a["project_tendency"] == "life"):
                    Project_result["Life"].append(a)

            return Response(
                Project_result
            )
        if(request.data['user_id']==0):
            topic = Project.objects.filter(group_id=request.data['group_id']).values('project_id' ,'project_topic', 'project_img', 'project_tendency').order_by('-updated_at')
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
                elif (a["project_tendency"] == "economy"):
                    Project_result["It"].append(a)
                elif (a["project_tendency"] == "life"):
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
        project_tendency = Project.objects.filter(project_tendency=temp[0]).values('project_id', 'project_topic',
                                                                                   'project_img', 'project_intro',
                                                                                   'project_hits', 'project_likes',
                                                                                   'project_tendency', 'user_id',
                                                                                   'group_id')
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
        user_key = User.objects.filter(user_name__contains=data).values('user_id', 'user_name')
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

        user_values = []
        j = 0
        for b in user_key:
            user_values.append(b)
            user_values[j].update(follow_count[j])
            j += 1

        repositories = Project.objects.filter(project_topic__contains=data).values('project_id', 'project_topic', 'user_id', 'group_id','project_intro', 'project_hits', 'project_likes', 'updated_at').order_by("-updated_at")

        # keyword search
        keyword = Idea_keyword.objects.filter(idea_keyword__contains=data).values("idea_keyword", "idea_keyword_id")
        keyword_list = {}
        for a in keyword:
            Idea_list = Idea_keyword_list.objects.filter(idea_keyword_id = a["idea_keyword_id"]).values("idea_id")[0]['idea_id']
            Idea_cont = Idea.objects.filter(idea_id = Idea_list).values("idea_id", "idea_cont", "user_id", "project_id", "is_forked")
            user_cont = User.objects.filter(user_id = Idea_cont[0]["user_id"]).values("user_name", "user_gender", "user_img")
            project_cont = Project.objects.filter(project_id=Idea_cont[0]["project_id"]).values("project_id", "project_topic", "project_intro", "project_tendency", "project_hits", "project_likes")
            keyword_list.update(user_cont[0])
            keyword_list.update(project_cont[0])
            if(Idea_cont[0]["is_forked"] == 0):
                keyword_list.update(Idea_cont[0])

        # groups search
        group_key = Group.objects.filter(group_name__contains=data).values('group_id', 'group_name', 'group_intro')
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

        testing = []
        i = 0
        for b in group_key:
            testing.append(b)
            testing[i].update(temp[i])
            i += 1

        return Response(
            {
                "users": user_values,
                "repositories": repositories,
                "groups": testing,
                "keyword" : keyword_list
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
        request.data['idea_cont'] = "None"
        request.data['idea_senti'] = "None"
        request.data["updated_at"] = timezone.now()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        idea = serializer.save()
        return Response(
            {
                "idea_id" : idea.idea_id,
                "parent_id" : idea.parent_id,
                "user_id": idea.user_id_id,
                "project_id": idea.project_id_id,
                "Idea_cont": idea.idea_cont,
                "Idea_senti": idea.idea_senti,
                "is_forked": idea.is_forked,
                "idea_color" : idea.idea_color
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
                "idea_id" : idea_loc.idea_id_id,
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
        request.data["updated_at"] = timezone.now()
        queryset = Idea.objects.filter(idea_id=request.data['idea_id'])
        queryset.update(
            idea_cont = request.data['idea_cont'],
            idea_color = request.data['idea_color'],
            idea_senti = request.data['idea_senti'],
            updated_at = request.data['updated_at']
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
        temp = request.data["idea_id"]
        for a in temp:
            queryset = Idea.objects.filter(idea_id = a)
            queryset.delete()
        return Response(
            "delete success"
        )

# Project 생성 유저/그룹
class Project_createAPI(generics.GenericAPIView):
    serializer_class = Project_createSerializer

    def post(self, request):
        if(request.data['group_id'] == 0):
            result = Classifier.Grade(request.data['project_topic'])
            maximum = max(result, key=result.get)
            request.data['project_tendency'] = maximum
            request.data["updated_at"] = timezone.now()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            project = serializer.save()
            return Response(
                {
                    "project_id" : project.project_id,
                    'project_img' : project.project_img,
                    "user_id": project.user_id,
                    "group_id": project.group_id,
                    "project_topic": project.project_topic,
                    "project_tendency": project.project_tendency,
                    "project_intro": project.project_intro,
                }
            )

        if(request.data['user_id'] == 0):
            result = Classifier.Grade(request.data['project_topic'])
            maximum = max(result, key=result.get)
            request.data['project_tendency'] = maximum
            request.data["updated_at"] = timezone.now()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            project = serializer.save()
            return Response(
                {
                    "project_id": project.project_id,
                    'project_img': project.project_img,
                    "user_id": project.user_id,
                    "group_id": project.group_id,
                    "project_topic": project.project_topic,
                    "project_tendency": project.project_tendency,
                    "project_intro": project.project_intro,
                }
            )

# 회원가입 할 때 Person_tendency에도 내용 추가
class Person_tendencyCreateAPI(generics.GenericAPIView):
    serializer_class = Person_tendencySerializer

    def post(self, request):
        request.data['it'] = 0
        request.data['sport'] = 0
        request.data['politics'] = 0
        request.data['economy'] = 0
        request.data['life'] = 0
        request.data['society'] = 0
        request.data['user_tendency'] = "None"

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        person_tendency = serializer.save()
        return Response(
            {
                "user_id" : person_tendency.user_id,
                "user_tendency": person_tendency.user_tendency,
                "it": person_tendency.it,
                "politics": person_tendency.politics,
                "economy": person_tendency.economy,
                "sport": person_tendency.sport,
                "society": person_tendency.society,
                "life" : person_tendency.life
            }
        )

# 그룹 할 때 Person_tendency에도 내용 추가
class Group_tendencyCreateAPI(generics.GenericAPIView):
    serializer_class = Group_tendencySerializer

    def post(self, request):
        def post(self, request):
            request.data['it'] = 0
            request.data['sport'] = 0
            request.data['politics'] = 0
            request.data['economy'] = 0
            request.data['life'] = 0
            request.data['society'] = 0
            request.data['group_tendency'] = ""

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            group_tendency = serializer.save()
            return Response(
                {
                    "user_id": group_tendency.group_id,
                    "user_tendency": group_tendency.group_tendency,
                    "it": group_tendency.it,
                    "politics": group_tendency.politics,
                    "economy": group_tendency.economy,
                    "sport": group_tendency.sport,
                    "society": group_tendency.society,
                    "life": group_tendency.life
                }
            )


# Project 수정
class Project_updateAPI(generics.GenericAPIView):
    def post(self, request):
        result = Classifier.Grade(request.data['project_topic'])
        maximum = max(result, key=result.get)
        request.data['project_tendency'] = maximum
        request.data['updated_at'] = timezone.now()
        queryset = Project.objects.filter(project_id=request.data['project_id'])
        queryset.update(
            project_topic = request.data['project_topic'],
            project_tendency = request.data['project_tendency'],
            updated_at = request.data['updated_at'],
        )
        return Response(
            "update success"
        )

# Project 삭제
class Project_deleteAPI(generics.GenericAPIView):
    def post(self, request):
        queryset = Project.objects.filter(project_id = request.data['project_id'])
        queryset.delete()
        return Response(
            "delete success"
        )

# 개인 페이지 index
class Person_tendencyUpdateAPI(generics.GenericAPIView):
    def post(self, request):
        result = Classifier.Grade(request.data['project_topic'])
        user_tendency = Person_tendency.objects.filter(user_id = request.data['user_id']).values('it', 'politics', 'society', 'economy', 'life', 'sport')
        request.data["it"] = result['it'] + user_tendency[0]['it']
        request.data["sport"] = result['sport'] + user_tendency[0]['sport']
        request.data["society"] = result['society'] + user_tendency[0]['society']
        request.data["economy"] = result['economy'] + user_tendency[0]['economy']
        request.data["life"] = result['life'] + user_tendency[0]['life']
        request.data["politics"] = result['politics'] + user_tendency[0]['politics']

        maximum = max(user_tendency[0], key=lambda k: user_tendency[0][k])
        request.data['user_tendency'] = maximum

        queryset = Person_tendency.objects.filter(user_id = request.data['user_id'])
        queryset.update(
            it = request.data['it'],
            economy = request.data['economy'],
            sport = request.data['sport'],
            politics = request.data['politics'],
            life = request.data['life'],
            society = request.data['society'],
            user_tendency = request.data['user_tendency']
        )
        return Response(
            "update success"
        )

# 프로젝트 생성 시 그룹 성향도 수정
class Group_tendencyUpdateAPI(generics.GenericAPIView):
    def post(self, request):
        result = Classifier.Grade(request.data['project_topic'])
        group_tendency = Person_tendency.objects.filter(group_id = request.data['group_id']).values('it', 'politics', 'society', 'economy', 'life', 'sport')
        request.data["it"] = result['it'] + group_tendency[0]['it']
        request.data["sport"] = result['sport'] + group_tendency[0]['sport']
        request.data["society"] = result['society'] + group_tendency[0]['society']
        request.data["economy"] = result['economy'] + group_tendency[0]['economy']
        request.data["life"] = result['life'] + group_tendency[0]['life']
        request.data["politics"] = result['politics'] + group_tendency[0]['politics']

        maximum = max(group_tendency[0], key=lambda k: group_tendency[0][k])
        request.data['group_tendency'] = maximum

        queryset = Person_tendency.objects.filter(group_id = request.data['group_id'])
        queryset.update(
            it = request.data['it'],
            economy = request.data['economy'],
            sport = request.data['sport'],
            politics = request.data['politics'],
            life = request.data['life'],
            society = request.data['society'],
            user_tendency = request.data['group_tendency']
        )
        return Response(
            "update success"
        )

# 개인 페이지 index
class Page_indexAPI(generics.GenericAPIView):
    def post(self, request):
            user_tendency = Person_tendency.objects.filter(user_id = request.data['user_id']).values('user_tendency', 'it', 'sport', 'society', 'politics', 'life', 'economy')
            user_feed = Idea.objects.filter(user_id = request.data['user_id']).values("idea_cont", "project_id", "idea_id", "updated_at").order_by("-updated_at")
            temp = []
            temp.append(user_tendency[0])
            test = []

            for a in user_feed:
                project_data = Project.objects.filter(project_id = a['project_id']).values("project_topic", "project_intro", "project_likes", "project_hits")
                a["project"] = project_data[0]
                test.append(a)

            User_detail = User.objects.filter(user_id = request.data["user_id"]).values("user_name", "user_id", "user_email","user_img", "user_bgimg", "user_gender")

            current_day = timezone.now()
            project = Project.objects.filter(user_id = request.data["user_id"]).values('updated_at')
            count = {}
            for i in range(8):
                count[(current_day + timezone.timedelta(days=-i-1)).strftime("%m/%d/%Y")] = {"project_count":0, "idea_count" :0}

            for a in project:
                x = (current_day-a['updated_at']).days
                count[(current_day + timezone.timedelta(days=-x-1)).strftime("%m/%d/%Y")]["project_count"] += 1

            idea = Idea.objects.filter(user_id = request.data["user_id"]).values("updated_at")
            for b in idea:
                x = (current_day-b['updated_at']).days
                count[(current_day + timezone.timedelta(days=-x-1)).strftime("%m/%d/%Y")]["idea_count"] +=1

            return Response(
                {
                    "User_detail" : User_detail[0],
                    "User_tendency" : temp,
                    "User_feed" : test,
                    "User_log" : count
                }
            )

# 하나의 프로젝트 상세 페이지
class Project_detailAPI(generics.GenericAPIView):
    def post(self, request):
        print(Project.objects.filter(project_id = request.data['project_id']).exists())
        if(Project.objects.filter(project_id = request.data['project_id']).exists()):
            project = Project.objects.filter(project_id = request.data["project_id"]).values("user_id", "group_id", "project_topic", "project_img", "project_tendency", "project_likes", "project_hits", "project_intro")

            if(project[0]['group_id'] == 0):
                creater_name = User.objects.filter(user_id = project[0]["user_id"]).values('user_name')[0]["user_name"]
            else:
                creater_name = Group.objects.filter(group_id=project[0]["group_id"]).values('group_name')[0]["group_name"]
            project_category = Project_category.objects.filter(project_id = request.data["project_id"]).values("economy", "it", "society", "politics", "sport", "life")
            similar_project = Project.objects.filter(project_tendency=project[0]["project_tendency"]).exclude(project_id=request.data["project_id"]).values("project_topic", "project_img", "project_id", "user_id", "group_id")
            return Response(
                {
                    "project" : project[0],
                    'creater_name' : creater_name,
                    "project_category" : project_category[0],
                    "similar_projects" : similar_project
                }
            )
        else:
            return Response(
                "The project does not exist."
            )

# 프로젝트 생성 시 프로젝트 카테고리
class Project_categoryAPI(generics.GenericAPIView):
    serializer_class = Project_categorySerializer

    def post(self, request):
        result = Classifier.Grade(request.data['project_topic'])
        request.data["it"] = 0
        request.data["sport"] = 0
        request.data["economy"] = 0
        request.data["society"] = 0
        request.data["politics"] = 0
        request.data["life"] = 0

        for key in result.keys():
            if(result.get(key) >= 30):
                request.data[key] = result.get(key)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project_category = serializer.save()
        return Response(
            {
                "project_id": project_category.project_id_id,
                "it": project_category.it,
                "economy": project_category.economy,
                "society": project_category.society,
                "politics": project_category.politics,
                "sport": project_category.sport,
                "life": project_category.life,
            }
        )

# 개인페이지, 개인 프로필 사진 수정
class UserImg_updateAPI(generics.GenericAPIView):
    def post(self, request):
        if(request.data['user_bgimg']==0):
            queryset = User.objects.filter(user_id=request.data['user_id'])
            queryset.update(
                user_img = request.data['user_img']
            )
            return Response(
                "update success"
            )
        elif(request.data['user_img'] == 0):
            queryset = User.objects.filter(user_id=request.data['user_id'])
            queryset.update(
                user_bgimg=request.data['user_bgimg']
            )
            return Response(
                "update success"
            )

# 그룹페이지, 그룹 프로필 사진 수정
class GroupImg_updateAPI(generics.GenericAPIView):
    def post(self, request):
        if(request.data['group_bgimg']==0):
            queryset = Group.objects.filter(group_id=request.data['group_id'])
            queryset.update(
                group_img = request.data['group_img']
            )
            return Response(
                "update success"
            )
        elif(request.data['group_img'] == 0):
            queryset = Group.objects.filter(group_id=request.data['group_id'])
            queryset.update(
                group_bgimg=request.data['group_bgimg']
            )
            return Response(
                "update success"
            )

# 아이디어 포크 히스토리 저장(퍼오기 부분)
class Idea_forkHistoryAPI(generics.GenericAPIView):
    serializer_class = Idea_forkHistorySerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        idea_fork = serializer.save()
        return Response(
            {
                "user_id" : idea_fork.user_id,
                "idea_id" : idea_fork.idea_id
            }
        )

# 아이디어 포크 아이디어 저장(퍼오기 부분)
class Idea_forkCreateAPI(generics.GenericAPIView):
    serializer_class = Idea_createSerializer
    def post(self, request):
        idea = Idea.objects.filter(idea_id = request.data['idea_id']).values('idea_cont', 'idea_senti')
        request.data['idea_cont'] = idea[0]['idea_cont']
        request.data['idea_senti'] = idea[0]['idea_senti']
        request.data["updated_at"] = timezone.now()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        idea = serializer.save()
        return Response(
            {
                "idea_id" : idea.idea_id,
                "project_id" : idea.project_id,
                "idea_cont" : idea.idea_cont,
                "idea_senti" : idea.idea_senti,
            }
        )

# 아이디어 키워드 저장
class Idea_keywordCreateAPI(generics.GenericAPIView):
    serializer_class = Idea_keywordCreateSerializer
    def post(self, request):
        hannanum = Hannanum()
        test = hannanum.nouns(request.data['idea_cont'])
        del request.data['idea_cont']
        for i in range(len(test)):
            if(Idea_keyword.objects.filter(idea_keyword = test[i]).exists()):
                break
            else:
                request.data['idea_keyword'] = test[i]
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        return Response(
            test
        )

# 아이디어 키워드 리스트 저장
class Idea_keywordListCreateAPI(generics.GenericAPIView):
    serializer_class = Idea_keywordListCreateSerializer
    def post(self, request):
        test = request.data['idea_cont']
        del request.data['idea_cont']
        for a in test:
            keyword_list_id = Idea_keyword.objects.filter(idea_keyword = a).values("idea_keyword_id")
            request.data['idea_keyword_id'] = keyword_list_id[0]['idea_keyword_id']
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(
            "ok"
        )

# 프로젝트 좋아요 생성
class Project_likeCreateAPI(generics.GenericAPIView):
    serializer_class = Project_likeSerializer
    def post(self, request):
        if (Project_like.objects.filter(user_id=request.data['user_id']).filter(project_id=request.data['project_id']).exists() == False):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            queryset = Project.objects.filter(project_id=request.data['project_id'])
            project_like = Project.objects.filter(project_id=request.data['project_id']).values("project_likes")
            queryset.update(
                project_likes=project_like[0]['project_likes'] + 1
            )
            return Response(
                "upload success"
            )
        else:
            return Response(
                "already exist"
            )

# 프로젝트 조회수 생성
class Project_hitCreateAPI(generics.GenericAPIView):
    serializer_class = Project_hitSerializer
    def post(self, request):
        if (Project_hit.objects.filter(user_id=request.data['user_id']).filter(project_id=request.data['project_id']).exists() == False):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            queryset = Project.objects.filter(project_id=request.data['project_id'])
            project_hit = Project.objects.filter(project_id=request.data['project_id']).values("project_hits")
            queryset.update(
                project_hits=project_hit[0]['project_hits'] + 1
            )
            return Response(
                "upload success"
            )
        else:
            return Response(
                "already exist"
            )

# 전체 아이디어 로드 (BrainStorming)
class Idea_loadAPI(generics.GenericAPIView):
    def post(self, request):
        Ideas = Idea.objects.filter(project_id = request.data['project_id']).values("idea_id", "user_id", "parent_id", "idea_cont", "is_forked", "idea_color")
        for a in Ideas:
            Ideas_location = Idea_loc.objects.filter(idea_id= a["idea_id"]).values("idea_x", "idea_y", "idea_width", "idea_height")
            print(Ideas_location[0])
            a.update(Ideas_location[0])
            Ideas_child = Idea_child.objects.filter(idea_id = a['idea_id']).values("child_id")
            a["child_id"] = []
            for b in Ideas_child:
                a["child_id"].append(b['child_id'])
        return Response(
            Ideas
        )

# 자식 아이디어 생성
class Idea_childCreateAPI(generics.GenericAPIView):
    serializer_class = Idea_childSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            "upload success"
        )

# Trend 부분 검색할 때 로그 생성
class Search_logCreateAPI(generics.GenericAPIView):
    serializer_class = Search_logCreateSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            "upload success"
        )

# Trend 부분 검색 결과(성별, 연령별)
class Search_logViewAPI(generics.GenericAPIView):
    def post(self, request):
        keyword_log = Keyword_log.objects.filter(keyword = request.data['keyword']).values("user_id")
        gender = {"Male" : 0, "Female" : 0}
        for a in keyword_log:
            user_gender = User.objects.filter(user_id = a["user_id"]).values("user_gender")[0]['user_gender']
            if(user_gender == "male"):
                gender["Male"] += 1
            else:
                gender["Female"] += 1

        age = {"10대" : 0, "20대" : 0, "30대" : 0, "40대" : 0, "50대" : 0, "60대 이상" : 0}
        for b in keyword_log:
            user_age = User.objects.filter(user_id = b["user_id"]).values("user_birth")[0]['user_birth']
            diff = timezone.now().date() - user_age
            if(diff.days < 7300):
                age["10대"] += 1
            elif(7300 <= diff.days < 10950):
                age["20대"] += 1
            elif (10950 <= diff.days < 14600):
                age["30대"] += 1
            elif (14600 <= diff.days < 18250):
                age["40대"] += 1
            elif (18250 <= diff.days < 21900):
                age["50대"] += 1
            else:
                age["60대 이상"] += 1

        return Response(
            {
                "Search_gender" : gender,
                "Search_age" : age
            }
        )

# 프로젝트 PDF 이미지 저장
class Project_PDFAPI(generics.GenericAPIView):
    def post(self, request):
        queryset = Project.objects.filter(project_id = request.data['project_id'])
        queryset.update(
            project_img = request.data['project_img']
        )
        return Response(
            "update success"
        )