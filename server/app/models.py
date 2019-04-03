from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser



class UserManager(BaseUserManager):
    def create_user(self, user_email, user_name, password=None):
        if not user_email:
            raise ValueError('Users must have an email address')

        user = self.model(
            user_email=self.normalize_email(user_email),
            user_name=user_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_email, user_name, password):
        user = self.create_user(
            user_email=user_email,
            user_name=user_name,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

# User model
class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    user_email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    user_name = models.CharField(verbose_name='user name', max_length=30)
    user_birth = models.DateField()
    user_gender = models.CharField(max_length=10)
    user_img = models.CharField(max_length=200)
    user_bgimg = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'user_email'
    REQUIRED_FIELDS = ['user_name']

    def __str__(self):
        return self.user_email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        db_table = 'User'


class Person_tendency(models.Model):
    user_id = models.IntegerField(User, unique=True)
    society = models.IntegerField(default=0)
    it = models.IntegerField(default=0)
    sport = models.IntegerField(default=0)
    life = models.IntegerField(default=0)
    politics = models.IntegerField(default=0)
    objects = models.Manager()
    class Meta:
        db_table = 'Person_tendency'

# follow model
class Follow(models.Model):
    follow_id = models.AutoField(primary_key=True)
    partner_id = models.IntegerField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        db_table = 'Follow'
        ordering = ['-created_at']

class Request(models.Model):
    request_id = models.AutoField(primary_key=True)
    send_id = models.ForeignKey(User, on_delete=models.CASCADE)
    receive_id = models.IntegerField()
    request_cont = models.CharField(max_length=200)
    is_accepted = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        db_table = 'Request'

# chat model
class Chat(models.Model):
    chat_id = models.AutoField(primary_key=True)
    chat_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        db_table = 'Chat'
        ordering = ['-created_at']

class Chat_cont(models.Model):
    chat_id = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_cont = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        db_table = 'Chat_cont'
        ordering = ['-created_at']

class Chat_entry(models.Model):
    chat_id = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    objects = models.Manager()
    class Meta:
        db_table = 'Chat_entry'

class Group(models.Model):
    group_id = models.AutoField(primary_key=True)
    group_img = models.CharField(max_length=200)
    group_intro = models.CharField(max_length=200)
    group_bgimg = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        db_table = 'Group'

class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    project_topic = models.CharField(max_length=100)
    project_img = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        db_table = 'Project'
        ordering = ['-created_at']

# group model
class Group_tendency(models.Model):
    group_id = models.IntegerField(Group, unique=True)
    group_tendency = models.CharField(max_length=100)
    society = models.IntegerField(default=0)
    it = models.IntegerField(default=0)
    sport = models.IntegerField(default=0)
    life = models.IntegerField(default=0)
    politics = models.IntegerField(default=0)
    objects = models.Manager()
    class Meta:
        db_table = 'Group_tendency'

class Group_entry(models.Model):
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    objects = models.Manager()
    class Meta:
        db_table = 'Group_entry'

# idea model
class Idea(models.Model):
    idea_id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_id = models.IntegerField(null=True)
    idea_cont = models.CharField(max_length=150)
    idea_senti = models.CharField(max_length=50)
    is_forked = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        db_table = 'Idea'
        ordering = ['-created_at']

class Idea_keyword(models.Model):
    idea_keyword_id = models.AutoField(primary_key=True)
    idea_keyword = models.CharField(max_length=200)
    objects = models.Manager()
    class Meta:
        db_table = 'Idea_keyword'

class Idea_keyword_list(models.Model):
    idea_id = models.ForeignKey(Idea, on_delete=models.CASCADE)
    idea_keyword_id = models.ForeignKey(Idea_keyword, on_delete=models.CASCADE)
    objects = models.Manager()
    class Meta:
        db_table = 'Idea_keyword_list'

class Idea_child(models.Model):
    idea_id = models.ForeignKey(Idea, on_delete=models.CASCADE)
    child_id = models.IntegerField()
    objects = models.Manager()
    class Meta:
        db_table = 'Idea_child'

class Idea_loc(models.Model):
    idea_id = models.IntegerField(unique=True)
    idea_x = models.FloatField()
    idea_y = models.FloatField()
    idea_width = models.FloatField()
    idea_height = models.FloatField()
    objects = models.Manager()
    class Meta:
        db_table = 'Idea_loc'

class Idea_file(models.Model):
    idea_id = models.ForeignKey(Idea, on_delete=models.CASCADE)
    idea_file = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        db_table = 'Idea_file'

class Idea_fork(models.Model):
    idea_id = models.ForeignKey(Idea, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    objects = models.Manager()
    class Meta:
        db_table = 'Idea_fork'

# notification model
class Notification(models.Model):
    notify_id = models.AutoField(primary_key=True)
    send_id = models.ForeignKey(User, on_delete=models.CASCADE)
    receive_id = models.IntegerField()
    notify_cont = models.CharField(max_length=200)
    read_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        db_table = 'Notification'

# project model
class Project_category(models.Model):
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    project_tag = models.CharField(max_length=50)
    objects = models.Manager()
    class Meta:
        db_table = 'Project_category'

class Project_like(models.Model):
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        db_table = 'Project_like'

class Project_hit(models.Model):
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    class Meta:
        db_table = 'Project_hit'