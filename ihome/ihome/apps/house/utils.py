from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.status import HTTP_504_GATEWAY_TIMEOUT
from django.db import DatabaseError
import logging

logger = logging.getLogger('django')


def my_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, DatabaseError):
            response = Response({'erno': '4004', 'errmsg': '数据库无了'}, status=HTTP_504_GATEWAY_TIMEOUT)
        else:
            response = Response({'errno': '4004', 'errmsg': '网络连接超时'}, status=404)
            logger.error(exc)

    return response
