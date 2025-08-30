from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password
from shortuuidfield import ShortUUIDField


# Create your models here.


class UserStatusChoices(models.IntegerChoices):
    """
    用户的账号状态
    """
    ACTIVED = 1  # 激活
    UNACTIVE = 0  # 未激活
    LOCKED = -1  # 锁定


class OAUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user_object(self, real_name, email, password, **extra_fields):
        """ 生成用户实例对象 """
        if not real_name:
            raise ValueError("请输入真实的姓名!")
        email = self.normalize_email(email)
        user = self.model(real_name=real_name, email=email, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, real_name, email, password, **extra_fields):
        """ 基于 _create_user_object 生成的用户实例, 保存到数据库中 """
        user = self._create_user_object(real_name, email, password, **extra_fields)
        user.save(using=self._db)
        return user

    async def _acreate_user(self, real_name, email, password, **extra_fields):
        """ 异步将用户实例保存到数据库中 """
        user = self._create_user_object(real_name, email, password, **extra_fields)
        await user.asave(using=self._db)
        return user

    def create_user(self, real_name, email=None, password=None, **extra_fields):
        """ 创建普通用户 """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(real_name, email, password, **extra_fields)

    create_user.alters_data = True

    async def acreate_user(self, real_name, email=None, password=None, **extra_fields):
        """ 异步创建普通用户 """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return await self._acreate_user(real_name, email, password, **extra_fields)

    acreate_user.alters_data = True

    def create_superuser(self, real_name, email=None, password=None, **extra_fields):
        """ 创建超级用户 """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", UserStatusChoices.ACTIVED)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(real_name, email, password, **extra_fields)

    create_superuser.alters_data = True

    async def acreate_superuser(
            self, real_name, email=None, password=None, **extra_fields
    ):
        """ 异步创建超级用户 """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", UserStatusChoices.ACTIVED)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return await self._acreate_user(real_name, email, password, **extra_fields)

    acreate_superuser.alters_data = True


class OAUser(AbstractBaseUser, PermissionsMixin):
    """
    自定义用户模型
    """
    # GENDER_CHOICES = [
    #     ('M', '男'),
    #     ('F', '女'),
    #     ('-', '未知'),
    # ]
    uid = ShortUUIDField(primary_key=True)
    real_name = models.CharField(max_length=150, unique=False)
    # gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='-')
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=11, blank=True, unique=False)
    is_staff = models.BooleanField(default=True)
    status = models.IntegerField(choices=UserStatusChoices, default=UserStatusChoices.UNACTIVE)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    department = models.ForeignKey(
        'OADepartment', null=True, on_delete=models.SET_NULL,
        related_name='department_staffs', related_query_name='department_staffs',
    )

    objects = OAUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"  # 以 email 作为鉴权
    # REQUIRED_FIELDS: 必传的字段   其中不能重复 EMAIL_FIELD 以及 USERNAME_FIELD 的字段
    REQUIRED_FIELDS = ["real_name", "password"]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.real_name

    def get_short_name(self):
        return self.real_name

    # class Meta:
    #     ordering = ['date_joined']


class OADepartment(models.Model):
    """
    企业部门模型
    """
    name = models.CharField(max_length=50)
    intro = models.CharField(max_length=200)
    leader = models.OneToOneField(
        OAUser, null=True, on_delete=models.SET_NULL,
        related_name="leader_department", related_query_name="leader_department"
    )
    manager = models.ForeignKey(
        OAUser, null=True, on_delete=models.SET_NULL,
        related_name="manager_departments", related_query_name="manager_departments"
    )
