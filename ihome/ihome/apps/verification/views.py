import json
import re
import random
import logging

from celery_tasks.msm.tasks import ccp_send_sms_code

logger = logging.getLogger('django')

from django.views import View
from django.http import HttpResponse, JsonResponse
from django_redis import get_redis_connection

from ihome.libs.captcha.captcha import captcha


class Verification(View):
    def get(self, request):
        cur = request.GET.get('cur')
        pre = request.GET.get('pre')
        redis_conn = get_redis_connection('verify_code')
        if not cur:
            return JsonResponse({
                'errno': '4002',
                'errmsg': 'Required parameter missing'
            })
        if pre:
            redis_conn.delete('img_%s' % pre)

        text, image = captcha.generate_captcha()
        logger.info('图片验证码%s' % text)

        redis_conn.setex('img_%s' % cur, 300, text)

        return HttpResponse(image,
                            content_type='image/jpg')


class Sms(View):
    def post(self, request):
        dict = json.loads(request.body.decode())
        mobile = dict.get('mobile')
        id = dict.get('id')
        text = dict.get('text')

        redis_conn = get_redis_connection('verify_code')
        if redis_conn.get('flag_%s' % mobile):
            logger.info('触发flag')
            return JsonResponse({
                'errno': '4002',
                'errmsg': 'Sending verification code too frequently'
            }, status=402)

        if not all([mobile, id, text]):
            return JsonResponse({
                'errno': '4002',
                'errmsg': 'Required parameter missing'
            }, status=402)

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({
                'errno': '4002',
                'errmsg': 'Incorrect format of mobile number'
            }, status=402)

        text_server = redis_conn.get('img_%s' % id)
        redis_conn.delete('img_%s' % id)
        if not text_server:
            return JsonResponse({
                'errno': '4002',
                'errmsg': 'Verification code expired'
            }, status=402)

        if text_server.decode().lower() != text.lower():
            return JsonResponse({
                'errno': '4002',
                'errmsg': 'Verification code mismatch'
            }, status=402)

        sms_code = random.randint(100000, 999999)
        logger.info('短信验证码%s' % sms_code)
        ccp_send_sms_code.delay(mobile, sms_code)
        p1 = redis_conn.pipeline()

        p1.setex('img_%s' % mobile, 300, sms_code)
        p1.setex('flag_%s' % mobile, 300, 1)

        p1.execute()
        return JsonResponse({
            "errno": '0',
            "errmsg": "Sent successfully"
        })
