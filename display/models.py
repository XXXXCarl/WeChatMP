from django.db import models
from django.contrib.auth.models import AbstractUser
from WeChatMP import settings


# Create your models here.

class MissingFamilyPost(models.Model):
    gender = ((1, '男'), (0, '女'))

    name = models.CharField(max_length=128, verbose_name="失踪人姓名")
    sex = models.PositiveSmallIntegerField(verbose_name="性别", choices=gender, default=1)
    missing_date = models.DateField(auto_now=False, auto_now_add=False, verbose_name="失踪日期")
    birth_date = models.DateField(auto_now=False, auto_now_add=False, verbose_name="出生日期")
    detail_info = models.TextField(verbose_name="详细信息", blank=True)
    imgUrl = models.ImageField(upload_to='upload/', verbose_name="失踪人照片")
    missing_place = models.CharField(max_length=128, verbose_name="失踪地点")
    phone_number = models.CharField(max_length=128, verbose_name="联系电话")

    openid = models.CharField(max_length=128, verbose_name="用户ID")
    likeNum = models.PositiveIntegerField(verbose_name="点赞数", default=0)
    collectNum = models.PositiveIntegerField(verbose_name="收藏数", default=0)
    forwardNum = models.PositiveIntegerField(verbose_name="转发数", default=0)
    release_date = models.DateField(auto_now_add=True, verbose_name="发布日期")
    timestamp = models.DateTimeField(auto_now=True, verbose_name="上传时间")

    verification_status = models.CharField(max_length=20, choices=[('pending', '待审核'), ('approved', '已通过'),
                                                                   ('rejected', '已驳回')], default='pending')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "寻亲贴"


class User(AbstractUser):
    openid = models.CharField(max_length=128, verbose_name="用户ID")
    icon = models.ImageField(upload_to='icon', default='/icon/default.jpg/', verbose_name='用户头像')
    telephone = models.CharField(max_length=11, verbose_name='手机号码')
    nickname = models.CharField(max_length=128, verbose_name="用户昵称")

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name_plural = "用户"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="followers",
                                       verbose_name="关注我的")  # 关注用户的其他用户
    followees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="followees",
                                       verbose_name="我关注的")  # 用户关注的其他用户

    def __str__(self):
        return self.user

    class Meta:
        verbose_name_plural = "用户关注"


class Comment(models.Model):
    post = models.ForeignKey(MissingFamilyPost, on_delete=models.DO_NOTHING, verbose_name="被评论文章")
    content = models.TextField(verbose_name="评论内容")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="评论者")
    time = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    pre_comment = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, verbose_name="父评论ID")

    def __str__(self):
        return "来自" + author + "的评论"

    class Meta:
        verbose_name_plural = "寻亲贴用户评论"


class LikePost(models.Model):
    post = models.ForeignKey(MissingFamilyPost, on_delete=models.DO_NOTHING, verbose_name="被点赞帖子")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="点赞者")

    def __str__(self):
        return "来自" + str(self.user) + "对" + str(self.post) + "的点赞"

    class Meta:
        verbose_name_plural = "寻亲贴点赞"


class CollectPost(models.Model):
    post = models.ForeignKey(MissingFamilyPost, on_delete=models.DO_NOTHING, verbose_name="被收藏帖子")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="收藏者")

    def __str__(self):
        return "来自" + str(self.user) + "对" + str(self.post) + "的收藏"

    class Meta:
        verbose_name_plural = "寻亲贴收藏"


class ForwardPost(models.Model):
    post = models.ForeignKey(MissingFamilyPost, on_delete=models.DO_NOTHING, verbose_name="被转发帖子")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="转发者")

    def __str__(self):
        return "来自" + str(self.user) + "对" + str(self.post) + "的转发"

    class Meta:
        verbose_name = "寻亲贴转发"


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    content = models.TextField(verbose_name="反馈内容")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="反馈时间")

    def __str__(self):
        return "来自" + str(self.user) + "的反馈"

    class Meta:
        verbose_name_plural = "用户反馈"


class Volunteer(models.Model):
    gender = ((1, '男'), (0, '女'))

    photo = models.ImageField(upload_to='volunteer', default='/volunteer/default.jpg/', verbose_name='志愿者照片',
                              blank=False)
    name = models.CharField(max_length=128, verbose_name="志愿者姓名", blank=False)
    sex = models.PositiveSmallIntegerField(verbose_name="性别", choices=gender, blank=False)
    college = models.CharField(max_length=128, verbose_name="学校", blank=False)
    birthday = models.DateField(auto_now=False, auto_now_add=False, verbose_name="出生日期", blank=False)
    address = models.CharField(max_length=128, verbose_name="家庭住址", blank=False)
    phone_number = models.CharField(max_length=128, verbose_name="联系电话", blank=False)
    reason = models.TextField(verbose_name="申请原因", blank=False)

    is_passed = models.BooleanField(verbose_name="审核是否通过", default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "志愿者申请"


class Verification(models.Model):
    VERIFICATION_TYPES = (
        ('blue', '蓝V - 企业/机构认证'),
        ('yellow', '黄V - 个人名誉认证'),
        ('pink', '粉V - 寻亲人认证'),
    )

    applicant_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES, verbose_name="申请类型")
    application_text = models.TextField(verbose_name="申请说明")
    image_description = models.ImageField(upload_to='verification/', verbose_name="图片说明")

    def __str__(self):
        return self.applicant_type

    class Meta:
        verbose_name_plural = "认证-父模型"


class EnterpriseVerification(Verification):
    organization_name = models.CharField(max_length=128, verbose_name="组织名称")
    organization_type = models.CharField(max_length=128, verbose_name="组织性质")
    legal_representative = models.CharField(max_length=128, verbose_name="法人姓名")
    id_number = models.CharField(max_length=18, verbose_name="法人身份证号")
    organization_intro = models.TextField(verbose_name="机构简介")

    def __str__(self):
        return self.organization_name

    class Meta:
        verbose_name_plural = "蓝V - 企业/机构认证"


class CelebrityVerification(Verification):
    name = models.CharField(max_length=128, verbose_name="姓名")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "黄V - 个人名誉认证"


class MissingPersonVerification(Verification):
    parent_name = models.CharField(max_length=128, verbose_name="家长姓名")
    parent_id_number = models.CharField(max_length=18, verbose_name="身份证号")
    child_name = models.CharField(max_length=128, verbose_name="孩子姓名")
    child_id_number = models.CharField(max_length=18, verbose_name="身份证号")

    def __str__(self):
        return "家长：" + str(self.parent_name) + " 丢失儿童：" + str(self.child_name)

    class Meta:
        verbose_name_plural = "粉V - 寻亲人认证"


class PostsVerification(models.Model):
    post = models.ForeignKey(MissingFamilyPost, on_delete=models.CASCADE)
    status = models.CharField(max_length=20,
                              choices=[('pending', '待审核'), ('approved', '已通过'), ('rejected', '已驳回')],
                              default='pending', verbose_name="审核状态")
    reason = models.TextField(blank=True, null=True, verbose_name="驳回理由")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="发帖用户")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return self.post.name

    class Meta:
        verbose_name_plural = "寻亲贴发布审核"


class Notification(models.Model):
    STATUS_TYPES = (
        ('0', 'not read'),
        ('1', 'has been read'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="通知用户")
    message = models.TextField(verbose_name="通知信息", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    status = models.CharField(max_length=20, choices=STATUS_TYPES, default='0', verbose_name="查看状态")  # 消息是否被查看

    def __str__(self):
        return self.message

    class Meta:
        verbose_name_plural = "通知信息"
