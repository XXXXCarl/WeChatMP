from django.contrib import admin
from django.contrib import messages
from django.http import HttpRequest

from .models import MissingFamilyPost, User, UserProfile, Comment, LikePost, CollectPost, ForwardPost, Feedback, \
    Volunteer, \
    Verification, EnterpriseVerification, CelebrityVerification, MissingPersonVerification, PostsVerification, \
    Notification

admin.site.site_header = 'AI宝贝网站管理后台'  # 设置header
admin.site.site_title = 'AI宝贝网站管理后台'  # 设置title
admin.site.index_title = 'AI宝贝网站管理后台'
admin.site.register(MissingFamilyPost)
admin.site.register(User)
# admin.site.register(UserProfile)
admin.site.register(Comment)
admin.site.register(LikePost)
admin.site.register(CollectPost)
admin.site.register(ForwardPost)
admin.site.register(Feedback)
admin.site.register(Volunteer)
admin.site.register(Verification)
admin.site.register(EnterpriseVerification)
admin.site.register(CelebrityVerification)
admin.site.register(MissingPersonVerification)


@admin.register(PostsVerification)
class PostsVerificationAdmin(admin.ModelAdmin):
    list_display = ('post', 'status', 'reason', 'user', 'created_at')
    list_filter = ('status',)
    search_fields = ('post__name', 'user__username')

    def get_readonly_fields(self, request, obj=None):
        # 设置只读字段，避免在审核后编辑
        if obj and obj.status != 'pending':
            return ['post', 'status', 'reason', 'user', 'created_at']
        return []

    def save_model(self, request, obj, form, change):
        # 保存审核记录时，自动更新相关帖子的审核状态
        # obj PostsVerification对象
        if obj.status == 'approved':
            obj.post.verification_status = 'approved'
            obj.post.save()
        elif obj.status == 'rejected':
            obj.post.verification_status = 'rejected'
            obj.post.rejection_reason = obj.reason
            obj.post.save()

            message = 'Your post \'%s\' has been rejected.' % obj.post.name
            Notification.objects.create(user=obj.user, message=message)

        super().save_model(request, obj, form, change)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user']  # 只显示用户字段

