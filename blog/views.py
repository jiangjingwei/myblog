from django.shortcuts import render, HttpResponse, redirect
from blog.forms import RegisterForm
from PIL import Image, ImageDraw, ImageFont
import random
import os
import json
import string
from io import BytesIO
from myblog import settings
from django.contrib import auth
from django.http import JsonResponse
from blog.models import UserInfo


# Create your views here.


def index(request):
    if request.session.get('username'):

        return render(request, 'blog/index.html')
    else:
        return redirect('/login/')


def log_in(request):
    if request.is_ajax():
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        user = auth.authenticate(username=username, password=password)
        login_response = {'username': None, 'error': None}
        if user:
            auth.login(request, user)
            if json.loads(remember_me):
                request.session['username'] = user.username

            else:

                if request.session.get('username'):
                    del request.session['username']

            login_response['user'] = user.username
            return HttpResponse(json.dumps(login_response))

        else:
            login_response['error'] = '用户名密码错误'

            return HttpResponse(json.dumps(login_response))

    return render(request, 'blog/login.html')


def register(request):
    if request.is_ajax():
        form_obj = RegisterForm(request, request.POST)

        register_response = {'status': None, 'errors': None}
        if form_obj.is_valid():
            data = form_obj.cleaned_data
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            phone = data.get('phone')

            user = UserInfo.objects.create_user(username=username, password=password, email=email, telephone=phone)

            register_response['status'] = True

        else:
            print('验证失败', form_obj.errors)
            register_response['status'] = False
            register_response['errors'] = form_obj.errors

        return JsonResponse(register_response)

    register_form = RegisterForm(request)
    return render(request, 'blog/register.html', locals())


def get_captcha(request):
    img = Image.new('RGBA', (130, 44),
                    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw = ImageDraw.Draw(img)

    for i in range(300):
        draw.point(
            (random.randint(0, 130), random.randint(0, 130)),
            fill=(0, 0, 0)
        )

        if i > 290:
            draw.line(
                [
                    (random.randint(0, 130), random.randint(0, 130)),
                    (random.randint(0, 130), random.randint(0, 130)),
                ],

                fill=(220, 220, 220)
            )

    font_file_path = os.path.join(settings.BASE_DIR, 'blog/static/dist/fonts/hakuyoxingshu7000.TTF')
    font = ImageFont.truetype(font_file_path, 24)

    captcha_code = random.sample(string.digits + string.ascii_letters, 5)
    captcha_img_code = " ".join(captcha_code)

    # 在session保存验证码
    request.session['captcha_code'] = ''.join(captcha_code)

    draw.text((12, 10), captcha_img_code, font=font,
              fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    f = BytesIO()
    img.save(f, 'png')

    return HttpResponse(f.getvalue())


def home_page(request, user):
    print(request.user)
    return render(request, 'blog/home_page.html')


def home_edit(request, user):
    print(request.session.get('username'))

    return render(request, 'blog/home_edit.html', locals())
