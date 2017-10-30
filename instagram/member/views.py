from typing import NamedTuple

import requests
from django.contrib.auth import logout, get_user_model, login
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from django.conf import settings
from member.forms import SignupForm, SigninForm

# User model을 가져올 때는 이 함수를 써서 import 하는 것을 추천

User = get_user_model()


# Custom validation
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('post:post_list')
    else:
        form = SignupForm
    context = {
        'form': form,
    }
    return render(request, 'member/signup.html', context)


def signin(request):
    next_path = request.GET.get('next')
    if request.method == 'POST':
        form = SigninForm(request.POST)
        if form.is_valid():
            form.signin(request)
            if next_path:
                return redirect(next_path)
            return redirect('post:post_list')
    else:
        form = SigninForm
    context = {
        'form': form,
        'facebook_app_id': settings.FACEBOOK_APP_ID,
        'scope': settings.FACEBOOK_SCOPE,
    }
    return render(request, 'member/login.html', context)


def signout(request):
    logout(request)
    return redirect('post:post_list')


@login_required
def profile(request, user_pk):
    target_user = User.objects.get(pk=user_pk)
    context = {
        'target_user': target_user,
    }
    return render(request, 'member/profile.html', context)


def follow_toggle(request, user_pk):
    if request.method == 'POST':
        followee = User.objects.get(pk=user_pk)
        following = request.user
        following.follow_toggle(followee)
        return redirect('member:profile', user_pk=user_pk)


def facebook_login(request):
    class AccessTokenInfo(NamedTuple):
        access_token: str
        token_type: str
        expires_in: str

    class DebugTokenInfo(NamedTuple):
        app_id: str
        application: str
        expires_at: int
        is_valid: bool
        issued_at: int
        scopes: list
        type: str
        user_id: str

    class UserInfo:
        def __init__(self, data):
            self.id = data['id']
            self.email = data.get('email', '')
            self.url_picture = data['picture']['data']['url']

    app_id = settings.FACEBOOK_APP_ID
    app_secret_code = settings.FACEBOOK_APP_SECRET_CODE
    app_access_token = f'{app_id}|{app_secret_code}'
    code = request.GET.get('code')

    def get_access_token_info(code_value):
        # 사용자가 페이스북에 로그인하기 위한 링크에 있던 'redirect_url' GET 파라미터의 값과 동일한 값
        redirect_uri = '{scheme}://{host}{relative_url}'.format(
            scheme=request.scheme,
            host=request.META['HTTP_HOST'],
            relative_url=reverse('member:facebook_login'),
        )
        print('redirect_uri:', redirect_uri)

        # 액세스 토큰
        url_access_token = 'https://graph.facebook.com/v2.10/oauth/access_token'
        params_access_token = {
            'client_id': app_id,
            'redirect_uri': redirect_uri,
            'client_secret': app_secret_code,
            'code': code_value,
        }
        response = requests.get(url_access_token, params_access_token)
        return AccessTokenInfo(**response.json())

    def get_debug_token_info(token):
        url_debug_token = 'https://graph.facebook.com/debug_token'
        params_debug_token = {
            'input_token': token,
            'access_token': app_access_token,
        }
        response = requests.get(url_debug_token, params_debug_token)
        return DebugTokenInfo(**response.json()['data'])

    # 전달 받은 code 값으로 AccessTokenInfo namedtuple 반환
    access_token_info = get_access_token_info(code)
    # namedtuple에서 'access_token'키의 값을 가져옴
    access_token = access_token_info.access_token
    # DebugTokenInfo 가져오기
    debug_token_info = get_debug_token_info(access_token)

    # 유저 정보 가져오기
    user_info_fields = [
        'id',
        'name',
        'picture',
        'email',
    ]
    url_graph_user_info = 'https://graph.facebook.com/me'
    params_graph_user_info = {
        'fields': ','.join(user_info_fields),
        'access_token': access_token,
    }
    response = requests.get(url_graph_user_info, params_graph_user_info)
    result = response.json()
    user_info = UserInfo(data=result)

    # 페이스북으로 가입한 유저의 username
    # fb_<facebook_user_id>
    username = f'fb_{user_info.id}'
    # 위 username에 해당하는 User가 있는지 검사
    if User.objects.filter(username=username).exists():
        # 있으면 user에 해당 유저를 할당
        user = User.objects.get(username=username)
    else:
        user = User.objects.create_user(
            user_type=User.USER_TYPE_FACEBOOK,
            username=username,
            age=0
        )
    # user를 로그인 시키고 post_list 페이지로 이동
    login(request, user)
    return redirect('post:post_list')
