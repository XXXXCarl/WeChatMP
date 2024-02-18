from django.shortcuts import render, HttpResponse, redirect
from display.models import MissingFamilyPost, Comment, User, LikePost, CollectPost, ForwardPost, UserProfile, Feedback, \
    Volunteer, MissingPersonVerification, CelebrityVerification, EnterpriseVerification, PostsVerification, Notification
from django.core import serializers
from django.http import JsonResponse, HttpResponseNotFound
from django.db.utils import IntegrityError
from django.core.paginator import Paginator
from django.contrib import auth
import json


def index(request):
    return render(request, 'index.html')


def paginate_data(data, page, page_size):
    total_items = len(data)
    total_pages = (total_items + page_size - 1) // page_size  # Calculate total pages

    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    paginated_data = data[start_index:end_index]

    return paginated_data, total_pages


def register(request):  # 用户注册函数
    if request.method == 'GET':
        return render(request, 'register.html')  # 返回一个注册的页面
    else:
        username = request.POST.get('username')  # 获取注册输入的信息
        password = request.POST.get('password')
        User.objects.create_user(username=username, password=password)  # 在User表创建用户记录
        return HttpResponse('注册成功')


def user_login(request):
    if request.method == 'POST':

        openid = request.POST.get('openid')
        icon = request.POST.get('icon')
        nickname = request.POST.get('nickname')
        phone_number = request.POST.get('phone_number')

        try:
            user = User.objects.get(openid=openid)
            user.icon = icon
            user.nickname = nickname
            user.telephone = phone_number
        except User.DoesNotExist:
            User.objects.create(openid=openid, icon=icon, nickname=nickname, telephone=phone_number)

        return HttpResponse('登陆成功')


def displayMissingFamilyPostList(request):
    if request.method == 'GET':
        page = request.GET.get('page')
        page_size = request.GET.get('pagesize')

        try:
            posts = MissingFamilyPost.objects.all()
            paginator = Paginator(posts, page_size)
            page_data = paginator.get_page(page)
            data = serializers.serialize('json', page_data, fields=('name', 'imgUrl', 'missing_date', 'likeNum'))

        except MissingFamilyPost.DoesNotExist:
            error_code = 1
            response_data = {
                'error_code': error_code,
                'data': {}
            }
            return JsonResponse(response_data, safe=False)

        error_code = 0
        response_data = {
            'error_code': error_code,
            'data': data
        }
        return JsonResponse(response_data, safe=False)
    return JsonResponse({})


def displayMissingFamilyPostInfo(request):
    if request.method == 'GET':
        id = request.GET.get('id')

        try:
            post_info = MissingFamilyPost.objects.get(id=id)
        except MissingFamilyPost.DoesNotExist:
            error_code = 1
            response_data = {
                'error_code': error_code,
                'data': {}
            }
            return JsonResponse(response_data)

        data = list(MissingFamilyPost.objects.filter(id=id).values(
            'name',
            'sex',
            'missing_date',
            'birth_date',
            'detail_info',
            'imgUrl',
            'missing_place',
            'phone_number',
            'likeNum',
            'collectNum',
            'forwardNum',
            'release_date'))

        error_code = 0
        response_data = {
            'error_code': error_code,
            'data': data}
        return JsonResponse(response_data, safe=False)

    return JsonResponse({})


def postRelease(request):
    if request.method == 'POST':
        openid = request.POST.get('openid')
        name = request.POST.get('name')
        sex = request.POST.get('sex')
        birth_date = request.POST.get('birth_date')
        missing_date = request.POST.get('missing_date')
        missing_place = request.POST.get('missing_place')
        detail_info = request.POST.get('detail_info')
        phone_number = request.POST.get('phone_number')
        imgUrl = request.FILES.get('imgUrl')

        try:
            post = MissingFamilyPost.objects.create(
                name=name,
                sex=sex,
                birth_date=birth_date,
                missing_date=missing_date,
                missing_place=missing_place,
                detail_info=detail_info,
                phone_number=phone_number,
                imgUrl=imgUrl)

            user = User.objects.get(openid=openid)

            PostsVerification.objects.create(post=post, user=user, status='pending')

        except IntegrityError:
            error_code = 1
            response_data = {
                'error_code': error_code,
                'data': {}
            }
            return JsonResponse(response_data, safe=False)

        data = list(MissingFamilyPost.objects.filter(name=name, phone_number=phone_number).values(
            'name',
            'sex',
            'missing_date',
            'birth_date',
            'detail_info',
            'imgUrl',
            'missing_place',
            'phone_number'))

        error_code = 0
        response_data = {
            'error_code': error_code,
            'data': data}
        return JsonResponse(response_data, safe=False)

    return JsonResponse({})


def commentControl(request):
    if request.method == 'POST':
        openid = request.POST.get('openid')
        try:
            user = User.objects.get(openid=openid)
        except User.DoesNotExist:
            return HttpResponse('留言失败')

        comment_content = request.POST.get('comment_content')  # 评论内容
        post_id = request.POST.get('post_id')  # 被评论帖子ID
        pid = request.POST.get('pid')  # 父评论ID
        author_id = user.id  # 评论者ID

        Comment.objects.create(content=comment_content,
                               pre_comment_id=pid,
                               post_id=post_id,
                               author_id=author_id)
        return HttpResponse('留言成功')

    comment = list(Comment.objects.values(
        'id',
        'content',
        'pre_comment_id',
        'post_id',
        'author_id',
        'time'))

    error_code = 0
    response_data = {
        'error_code': error_code,
        'data': comment
    }
    return JsonResponse(response_data, safe=False)


def postInteraction(request):
    if request.method == 'POST':
        postid = request.POST.get('postid')
        openid = request.POST.get('openid')
        isAddLike = request.POST.get('isAddLike')
        isCollect = request.POST.get('isCollect')
        isForward = request.POST.get('isForward')

        try:
            user = User.objects.get(openid=openid)
            post = MissingFamilyPost.objects.get(id=postid)

        except User.DoesNotExist | MissingFamilyPost.DoesNotExist:
            error_code = 1
            response_data = {
                'error_code': error_code,
                'error_message': '用户或帖子未找到',
                'data': {}
            }
            return JsonResponse(response_data, safe=False)

        if isAddLike == 'True':
            existing_like = LikePost.objects.filter(post=post, user=user).exists()
            if existing_like:
                error_code = 2
                response_data = {
                    'error_code': error_code,
                    'error_message': '用户已经点赞过该帖子',
                    'data': {}
                }
                return JsonResponse(response_data, safe=False)

            LikePost.objects.create(post=post, user=user)
            post.likeNum += 1
            post.save()

        if isCollect == 'True':
            existing_collect = CollectPost.objects.filter(post=post, user=user).exists()
            if existing_collect:
                error_code = 3
                response_data = {
                    'error_code': error_code,
                    'error_message': '用户已经收藏过该帖子',
                    'data': {}
                }
                return JsonResponse(response_data, safe=False)

            CollectPost.objects.create(post=post, user=user)
            post.collectNum += 1
            post.save()

        if isForward == 'True':
            ForwardPost.objects.create(post=post, user=user)
            post.forwardNum += 1
            post.save()

        success_code = 0
        response_data = {
            'success_code': success_code,
            'data': {}
        }
        return JsonResponse(response_data, safe=False)


def follow_or_unfollow_user(request):
    if request.method == 'POST':
        user_to_follow_openid = request.POST.get('user_to_follow_openid')
        current_user_openid = request.POST.get('current_user_openid')
        to_follow_or_unfollow = request.POST.get('to_follow_or_unfollow')

        try:
            user_to_follow = User.objects.get(openid=user_to_follow_openid)
            current_user = User.objects.get(openid=current_user_openid)
        except User.DoesNotExist:
            error_code = 1
            response_data = {
                'error_code': error_code,
                'error_message': '用户未找到',
                'data': {}
            }
            return JsonResponse(response_data, safe=False)

        user_to_follow_profile, created = UserProfile.objects.get_or_create(user=user_to_follow)
        current_user_profile, created = UserProfile.objects.get_or_create(user=current_user)

        if to_follow_or_unfollow == 'follow':
            if user_to_follow in current_user_profile.followees.all():
                error_code = 2
                response_data = {
                    'error_code': error_code,
                    'error_message': '已经关注过该用户',
                    'data': {}
                }
                return JsonResponse(response_data, safe=False)

            current_user_profile.followees.add(user_to_follow)
            user_to_follow_profile.followers.add(current_user)
            current_user_profile.save()
            user_to_follow_profile.save()

        elif to_follow_or_unfollow == 'unfollow':
            if user_to_follow not in current_user_profile.followees.all():
                error_code = 3
                response_data = {
                    'error_code': error_code,
                    'error_message': '未关注该用户',
                    'data': {}
                }
                return JsonResponse(response_data, safe=False)

            current_user_profile.followees.remove(user_to_follow)
            user_to_follow_profile.followers.remove(current_user)
            current_user_profile.save()
            user_to_follow_profile.save()

        success_code = 0
        response_data = {
            'success_code': success_code,
            'data': {}
        }
        return JsonResponse(response_data, safe=False)


def postQuery(request):
    if request.method == 'GET':
        openid = request.GET.get("openid")

        try:
            user = User.objects.get(openid=openid)
            posts = MissingFamilyPost.objects.filter(openid=openid)

            post_list = []
            for post in posts:
                post_data = {
                    'name': post.name,
                    'sex': post.get_sex_display(),
                    'missing_date': post.missing_date.strftime('%Y-%m-%d'),
                    'birth_date': post.birth_date.strftime('%Y-%m-%d'),
                    'detail_info': post.detail_info,
                    'imgUrl': post.imgUrl.url,
                    'missing_place': post.missing_place,
                    'release_date': post.release_date.strftime('%Y-%m-%d')
                }
                post_list.append(post_data)

            response_data = {
                'error_code': 0,
                'openid': user.openid,
                'message': '成功查找到用户%s发布的共%d条帖子' % (user.username, len(post_list)),
                'data': post_list,
            }
            return JsonResponse(response_data, safe=False)

        except User.DoesNotExist | MissingFamilyPost.DoesNotExist:
            error_code = 1
            response_data = {
                'error_code': error_code,
                'error_message': '用户或帖子未找到',
                'data': {},
            }
            return JsonResponse(response_data, safe=False)


def modify_personal_info(request):
    if request.method == 'POST':
        openid = request.POST.get("openid")
        icon = request.POST.get('icon')
        nickname = request.POST.get('nickname')
        phone_number = request.POST.get('phone_number')

        try:
            user = User.objects.get(openid=openid)
            if icon:
                user.icon = icon
            if nickname:
                user.nickname = nickname
            if phone_number:
                user.telephone = phone_number
            user.save()

            response_data = {
                'error_code': 0,
                'message': '个人信息修改成功',
                'data': {
                    'icon': user.icon.url,
                    'nickname': user.nickname,
                    'phone_number': user.telephone
                }
            }

        except User.DoesNotExist:
            error_code = 1
            response_data = {
                'error_code': error_code,
                'error_message': '用户未找到',
                'data': {},
            }
            return JsonResponse(response_data, safe=False)

        return JsonResponse(response_data, safe=False)

    return JsonResponse({'error_code': 2, 'error_message': '无效的请求', 'data': {}})


def submit_feedback(request):
    if request.method == 'POST':
        openid = request.POST.get("openid")
        content = request.POST.get('content')
        try:
            user = User.objects.get(openid=openid)
            Feedback.objects.create(user=user, content=content)

            response_data = {
                'error_code': 0,
                'message': '意见反馈提交成功',
                'data': content
            }

        except User.DoesNotExist:
            error_code = 1
            response_data = {
                'error_code': error_code,
                'error_message': '用户未找到',
                'data': {},
            }
            return JsonResponse(response_data, safe=False)

        return JsonResponse(response_data, safe=False)

    return JsonResponse({'error_code': 2, 'error_message': '无效的请求', 'data': {}})


def apply_volunteer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        college = request.POST.get('college')
        photo = request.POST.get('photo')
        sex = request.POST.get('sex')
        birthday = request.POST.get('birthday')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        reason = request.POST.get('reason')

        try:
            Volunteer.objects.create(name=name, college=college, photo=photo, sex=sex, birthday=birthday,
                                     address=address, phone_number=phone_number, reason=reason)
        except Volunteer.DoesNotExist:
            error_code = 1
            response_data = {
                'error_code': error_code,
                'error_message': '字段缺失',
                'data': {},
            }
            return JsonResponse(response_data, safe=False)

        error_code = 0
        response_data = {
            'error_code': error_code,
            'error_message': '提交成功',
            'data': {},
        }
        return JsonResponse(response_data, safe=False)

    return JsonResponse({}, safe=False)


def searchMissingFamilyPost(request):
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('pagesize', 10))
        search_text = request.GET.get('search_text')
        region = request.GET.get('region')

        try:
            posts = MissingFamilyPost.objects.all()

            if search_text:
                posts = posts.filter(name__icontains=search_text)

            if region:
                posts = posts.filter(missing_place__icontains=region)

            post_list = list(posts.values('name', 'imgUrl', 'missing_date', 'missing_place', 'likeNum'))
            paginated_data, total_pages = paginate_data(post_list, page, page_size)

            response_data = {
                'error_code': 0,
                'data': paginated_data,
                'total_pages': total_pages
            }

            return JsonResponse(response_data, safe=False)

        except MissingFamilyPost.DoesNotExist:
            error_code = 1
            response_data = {
                'error_code': error_code,
                'data': {},
                'total_pages': 0
            }
            return JsonResponse(response_data, safe=False)

    return JsonResponse({'error_code': 2, 'data': {}})


def apply_verification(request):
    if request.method == 'POST':
        applicant_type = request.POST.get('applicant_type')
        application_text = request.POST.get('application_text')
        image_description = request.FILES.get('image_description')

        if not (applicant_type and application_text):
            error_code = 1  # 缺少验证所需的字段。
            response_data = {
                'error_code': error_code,
                'data': {}
            }
            return JsonResponse(response_data, safe=False)

        if applicant_type == 'blue':  # EnterpriseVerification
            organization_name = request.POST.get('organization_name')
            organization_type = request.POST.get('organization_type')
            legal_representative = request.POST.get('legal_representative')
            id_number = request.POST.get('id_number')
            organization_intro = request.POST.get('organization_intro')

            if not (
                    organization_name and organization_type and legal_representative and id_number and organization_intro):
                error_code = 1  # 缺少验证所需的字段。
                response_data = {
                    'error_code': error_code,
                    'data': {}
                }
                return JsonResponse(response_data, safe=False)

            verification = EnterpriseVerification.objects.create(
                applicant_type=applicant_type,
                application_text=application_text,
                image_description=image_description,
                organization_name=organization_name,
                organization_type=organization_type,
                legal_representative=legal_representative,
                id_number=id_number,
                organization_intro=organization_intro
            )

        elif applicant_type == 'yellow':  # CelebrityVerification
            name = request.POST.get('name')

            if not name:
                error_code = 1  # 缺少验证所需的字段。
                response_data = {
                    'error_code': error_code,
                    'data': {}
                }
                return JsonResponse(response_data, safe=False)

            verification = CelebrityVerification.objects.create(
                applicant_type=applicant_type,
                application_text=application_text,
                image_description=image_description,
                name=name
            )

        elif applicant_type == 'pink':  # MissingPersonVerification
            parent_name = request.POST.get('parent_name')
            parent_id_number = request.POST.get('parent_id_number')
            child_name = request.POST.get('child_name')
            child_id_number = request.POST.get('child_id_number')

            if not (parent_name and parent_id_number and child_name and child_id_number):
                error_code = 1  # 缺少验证所需的字段。
                response_data = {
                    'error_code': error_code,
                    'data': {}
                }
                return JsonResponse(response_data, safe=False)

            verification = MissingPersonVerification.objects.create(
                applicant_type=applicant_type,
                application_text=application_text,
                image_description=image_description,
                parent_name=parent_name,
                parent_id_number=parent_id_number,
                child_name=child_name,
                child_id_number=child_id_number
            )

        else:
            error_code = 2  # invalid applicant_type
            response_data = {
                'error_code': error_code,
                'data': {}
            }
            return JsonResponse(response_data, safe=False)

        verification.save()
        error_code = 0  # invalid applicant_type
        response_data = {
            'error_code': error_code,
            'data': {}
        }
        return JsonResponse(response_data, safe=False)

    error_code = 3  # Invalid request method.
    response_data = {
        'error_code': error_code,
        'data': {}
    }
    return JsonResponse(response_data, safe=False)


def get_notifications(request):
    if request.method == 'GET':
        openid = request.GET.get("openid")

        try:
            user = User.objects.get(openid=openid)
            notifications = Notification.objects.filter(user=user, status='0')

            for notification in notifications:
                notification.status = '1'
                notification.save()

            notification_data = [{'message': notification.message, 'created_at': notification.created_at}
                                 for notification in notifications]

            error_code = 0
            response_data = {
                'error_code': error_code,
                'data': notification_data
            }

        except User.DoesNotExist | Notification.DoesNotExist:
            error_code = 1
            response_data = {
                'error_code': error_code,
                'error_message': '用户未找到',
                'data': {}
            }

        return JsonResponse(response_data, safe=False)

    return JsonResponse({}, safe=False)
