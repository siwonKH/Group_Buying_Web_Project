import json
import hashlib
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django import views
from django.contrib.auth import logout
from .models import User, Stat, Post
from django.views.generic.list import ListView


class PostsView(ListView):
    model = Post
    paginate_by = 8
    context_object_name = 'posts'
    template_name = 'post-page.html'
    ordering = ['post_id']


def user_session(user=1):
    if user == 1:
        data = {
            'name_in': "로그인",
            'url': "login",
            'banner': "로그인",
            'banner_url': "login",
        }
        return data
    else:
        data = {
            'name_in': str(user.id) + " " + user.name,  # 무시해도 됨 (처리하기 귀찮)
            'url': "mypage",
            'name_out': "로그아웃",
            'write': "글쓰기",
            'banner': "로그아웃",
            'banner_url': "logout",
            'title_error': "",
            'exist': 0,
        }
        return data


class Home(views.View):
    def post(self, request):
        pass

    @staticmethod
    def get(request):
        user_pk = request.session.get('user')
        if user_pk:
            user = User.objects.get(id=user_pk)
            data = user_session(user)
            return render(request, 'index.html', data)
        data = user_session()
        return render(request, 'index.html', data)


class PostPage(views.View):
    def post(self, request):
        pass

    @staticmethod
    def get(request):
        return render(request, 'post-page.html')


class MyPage(views.View):
    def post(self, request):
        pass

    @staticmethod
    def get(request):
        user_pk = request.session.get('user')
        if not user_pk:
            return redirect('/login')
        user = User.objects.get(id=user_pk)
        data = user_session(user)
        stat = Stat.objects.get(id=user.id)
        my_signed_post = stat.my_signed_post
        my_signed_amount = stat.my_signed_amount

        if my_signed_post is not None and not my_signed_post == "" and not my_signed_post == ",":
            # 데이터베이스 데이터 문자열화
            my_signed_post_list = my_signed_post.split(',')
            my_signed_amount_list = my_signed_amount.split(',')
        # 데이터 베이스에 있는 값이 비었다면 빈 리스트 선언
        else:
            my_signed_post_list = []
            my_signed_amount_list = []

        print(my_signed_post_list)
        print(my_signed_amount_list)

        # 마지막으로 하던곳 ----------------------------------------------------------------------------------------------

        return render(request, 'cart.html', data)


class Login(views.View):
    @staticmethod
    def post(request):
        user_id = request.POST['user_id']

        if User.objects.filter(id=user_id).exists():
            user = User.objects.get(id=user_id)
            password = str(request.POST['password'])
            salted_password = str(user.salt) + password
            hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()

            if User.objects.filter(id=user_id, password=hashed_password).exists():
                request.session['user'] = user.id  # 세션에 유저 아이디 저장
                return redirect('/home')
            else:
                data = {'error': "아이디 또는 비밀번호가 다릅니다", 'user': user_id}
                return render(request, 'login.html', data)

        else:
            data = {'error': "아이디 또는 비밀번호가 다릅니다", 'user': user_id}
            return render(request, 'login.html', data)

    @staticmethod
    def get(request):
        user_pk = request.session.get('user')
        if user_pk:
            # 여기 왜 왔어~ 로그인 했으면 홈으로 돌아가~
            return redirect('/home')

        return render(request, 'login.html')


class LogOut(views.View):
    def post(self, request):
        pass

    # 로그아웃
    @staticmethod
    def get(request):
        logout(request)
        return redirect('/home')


class Write(views.View):
    @staticmethod
    def post(request):
        user_pk = request.session.get('user')
        # 로그인 했니?
        if user_pk:
            user = User.objects.get(id=user_pk)
        # 안했으면 로그인 해
        else:
            return redirect('/login')

        # 폼에서 받은 정보 가져오기
        title = request.POST['title']
        price = request.POST['price']
        link = request.POST['link']
        content = request.POST['message']
        content = str(content)

        # 오류 개수를 세고 오류 메시지 저장
        err_cnt = 0
        try:
            title = str(title)
            if len(str(title)) > 50:
                request.session['title_error'] = "50자 이하로 작성해주세요"
                request.session.save()
                err_cnt += 1
            title = title.strip()
            if title == "":
                request.session['title_error'] = "제품명을 입력해주세요"
                request.session.save()
                err_cnt += 1
            request.session['title'] = title
        except:
            request.session['title_error'] = "제품명을 바르게 입력해주세요"
            request.session.save()
            err_cnt += 1
        try:
            price = str(price).replace(',', "")
            price = int(price)
            if price > 1000000000:
                request.session['price_error'] = "수가 너무 큽니다"
                request.session.save()
                err_cnt += 1
            if price == 0:
                request.session['price_error'] = "가격을 입력해주세요"
                request.session.save()
                err_cnt += 1
            price = format(price, ',')
            request.session['price'] = price
        except:
            request.session['price_error'] = "가격을 숫자로 입력해주세요"
            request.session.save()
            err_cnt += 1
        try:
            image = request.FILES['image']
        except:
            request.session['image_error'] = "이미지를 선택해 주세요"
            request.session.save()
            err_cnt += 1
        try:
            post_end = request.POST['end_date']
            if post_end is None:
                request.session['date_error'] = "마감일을 선택해주세요"
                request.session.save()
                err_cnt += 1
            if post_end < datetime.today().strftime("%Y-%m-%d"):
                request.session['date_error'] = "마감일을 바르게 선택해주세요"
                request.session.save()
                err_cnt += 1
        except:
            request.session['date_error'] = "마감일을 선택해주세요"
            request.session.save()
            err_cnt += 1
        try:
            link = str(link)
            link = link.strip()
            if link == "":
                request.session['link_error'] = "제품 주소를 입력해주세요"
                request.session.save()
                err_cnt += 1
            request.session['link'] = link
        except:
            err_cnt += 1
            request.session['link_error'] = "제품 주소를 바르게 입력해주세요"
            request.session.save()
        # 오류가 0보다 크다면 리다이렉트
        if err_cnt > 0:
            return redirect('/write')

        # str_content = content
        content = content.replace('\n', '<br>')
        content = "<html><p>" + content + "</p></html>"

        # 세션에 저장
        request.session['title'] = title
        request.session['price'] = price
        request.session['link'] = link
        request.session['post_end'] = post_end  # 무시가능
        # request.session['content'] = str_content
        request.session.save()

        # 데이터베이스에 저장
        post = Post()
        post.image = image  # 무시해도 됨. 위에서 알아서 처리함
        post.id = user.id
        post.name = user.name
        post.title = title
        post.price = price
        try:
            post.shop_link = link
        except:
            post.shop_link = ""
        try:
            post.content = content
        except:
            post.content = ""
        post.post_end = post_end
        post.save()

        # 임시 세션 날리기
        request.session['title'] = ""
        request.session['price'] = ""
        request.session['link'] = ""
        request.session['post_end'] = ""
        request.session['content'] = ""

        return redirect('/post')

    @staticmethod
    def get(request):
        user_pk = request.session.get('user')
        # 로그인 했니?
        if user_pk:
            # 했어? 유저 정보 내놔
            user = User.objects.get(id=user_pk)
            data = user_session(user)
        else:  # 안했어? 로그인이나 해
            return redirect('/login')

        # html 에 전송할 데이터를 세션에서 불러옴
        data['title'] = request.session.get('title')
        data['price'] = request.session.get('price')
        data['link'] = request.session.get('link')
        data['post_end'] = request.session.get('post_end')
        data['image'] = request.session.get('image')
        if not request.session.get('title_error') is None:
            data['title_error'] = request.session.get('title_error')
        if not request.session.get('price_error') is None:
            data['price_error'] = request.session.get('price_error')
        if not request.session.get('image_error') is None:
            data['image_error'] = request.session.get('image_error')
        if not request.session.get('date_error') is None:
            data['date_error'] = request.session.get('date_error')
        if not request.session.get('link_error') is None:
            data['link_error'] = request.session.get('link_error')
        request.session.save()

        # 오류 메시지 세션 삭제하기
        try:
            del request.session['title_error']
        except:
            pass
        try:
            del request.session['price_error']
        except:
            pass
        try:
            del request.session['image_error']
        except:
            pass
        try:
            del request.session['date_error']
        except:
            pass
        try:
            del request.session['link_error']
        except:
            pass
        return render(request, 'new-post.html', data)


# Currently not using
# * Never using
# wtf
def sign(request):
    signed_value = request.POST['msg']
    print(signed_value)
    print("fgsjkdlgffdakljfdjbhfdjskdfhbdjbhjdsakjbdlddlsflsalsdad")
    pass


class Content(views.View):
    @staticmethod
    def post(request):
        # 로그인 되어있다면 유저정보 가져오기
        user_pk = request.session.get('user')
        if user_pk:
            user = User.objects.get(id=user_pk)
        else:
            return redirect('/login')

        # POST 값 받아오기
        signed_value = request.POST['signed_value']
        post_id = request.POST['post_id']
        try:
            if int(signed_value) < 0:
                return redirect('/content'+"?id="+post_id)
        except:
            return redirect('/home')

        # 유저 데이터베이스에서 정보 불러오기
        stat = Stat.objects.get(id=user.id)
        my_signed_post = stat.my_signed_post
        my_signed_amount = stat.my_signed_amount

        if my_signed_post is not None and not my_signed_post == "" and not my_signed_post == ",":
            # 데이터베이스 데이터 문자열화
            my_signed_post_list = my_signed_post.split(',')
            my_signed_amount_list = my_signed_amount.split(',')
        # 데이터 베이스에 있는 값이 비었다면 빈 리스트 선언
        else:
            my_signed_post_list = []
            my_signed_amount_list = []

        # 이미 신청했었다면
        if str(post_id) in my_signed_post_list:
            i = my_signed_post_list.index(str(post_id))
            my_signed_amount_list[i] = signed_value

            # 만약 신청한 값이 0이라면 리스트 삭제
            if int(signed_value) == 0:
                del my_signed_post_list[i]
                del my_signed_amount_list[i]
        else:
            my_signed_post_list.append(str(post_id))
            my_signed_amount_list.append(str(signed_value))

        # 리스트를 문자열로 변환
        my_signed_post = ",".join(my_signed_post_list)
        my_signed_amount = ",".join(my_signed_amount_list)

        # 문자열 데이터베이스에 저장
        stat.my_signed_post = my_signed_post
        stat.my_signed_amount = my_signed_amount
        stat.save()
# ------------------------------------------------------
        # 데이터베이스에서 게시글 정보 불러오기
        post = Post.objects.get(post_id=post_id)
        signed_ids = post.signed_id
        signed_amounts = post.signed_amount

        if signed_ids is not None and not signed_ids == "" and not signed_ids == ",":
            # 데이터베이스 데이터 문자열화
            signed_id_list = signed_ids.split(',')
            signed_amount_list = signed_amounts.split(',')
        else:
            signed_id_list = []
            signed_amount_list = []

        # 이미 신청했었다면 값만 바꾸기
        if str(user.id) in signed_id_list:
            i = signed_id_list.index(str(user.id))
            signed_amount_list[i] = str(signed_value)
            # 만약 신청한 값이 0이라면 리스트 삭제
            if int(signed_value) == 0:
                del signed_id_list[i]
                del signed_amount_list[i]
        else:
            signed_id_list.append(str(user.id))
            signed_amount_list.append(str(signed_value))

        # 리스트를 문자열로 변환
        signed_ids = ",".join(signed_id_list)
        signed_amounts = ",".join(signed_amount_list)

        # 문자열 데이터베이스에 저장
        post.signed_id = signed_ids
        post.signed_amount = signed_amounts
        post.save()
        if int(signed_value) < 1:
            string = "신청하지 않음"
        else:
            string = "신청한 개수: "
            string += str(signed_value) + "개"

        json_data = json.dumps({"msg": string, 'val': int(signed_value)})
        return HttpResponse(json_data, content_type="application/json")
        # return redirect('/content'+"?id="+post_id)

    @staticmethod
    def get(request):
        signed_amount = 0
        # 게시글 아이디 가져오고 없으면 게시글 페이지로
        post_id = request.GET['id']
        try:
            post = Post.objects.get(post_id=post_id)  # 게시글 테이블에서 정보 가져오기
        except:
            return redirect('/post')

        # 게시글 테이블에서 데이터 불러오기
        name = post.name
        title = post.title
        price = post.price
        image = post.image
        link = post.shop_link
        content = post.content
        # signed_ids = post.signed_id
        # signed_amounts = post.signed_amount
        post_date = post.post_date
        post_end = post.post_end

        # 로그인 되어있다면 유저정보 가져오기
        user_pk = request.session.get('user')
        if user_pk:
            # user = User.objects.get(id=user_pk)  # user 테이블에서 유저정보 가져오기
            user_id = int(user_pk)
            stat = Stat.objects.get(id=user_id)  # stat 테이블에서 사용자 게시글 현황 가져오기
            my_signed_posts = str(stat.my_signed_post)
            my_signed_amounts = str(stat.my_signed_amount)

            if my_signed_posts is not None and not my_signed_posts == "" and not my_signed_posts == ",":
                my_signed_post_list = my_signed_posts.split(',')
                my_signed_amount_list = my_signed_amounts.split(',')
            else:
                my_signed_post_list = []
                my_signed_amount_list = []

            if post_id in my_signed_post_list:
                string = "신청한 개수: "
                i = my_signed_post_list.index(post_id)
                signed_amount = my_signed_amount_list[i]
                string += str(signed_amount) + "개"
            else:
                string = "신청하지 않음"

        else:
            # user_id = 12345678  # 없는 아이디 의도적으로 만듦
            string = "로그인 하지 않음"


# 게시글 테이블에서 신청 정보 가져오는건 마이페이지로 이전 !!!!!!!!!!!!!!!!! important
        # string = "내가 신청한 수량: "
        # if signed_ids is not None and not signed_ids == "" and not signed_ids == ",":
        #     # 문자열들을 리스트로
        #     signed_id_list = signed_ids.split(',')
        #     signed_amount_list = signed_amounts.split(',')
        #
        #     # html 페이지에 보여줄 문자열 지정
        #     for i in signed_id_list:
        #         if str(user_id) == i:
        #             ind = signed_id_list.index(i)
        #             string += str(signed_amount_list[ind]) + "개"
        #             break
        # else:
        #     string += "신청하지 않음"

        data = {
            'post_id': post_id,
            'name': name,
            'title': title,
            'price': price,
            'image': image,
            'link': link,
            'content': content,
            'post_date': post_date,
            'post_end': post_end,
            'string': string,
            'val': signed_amount,
        }
        return render(request, 'single-product.html', data)
