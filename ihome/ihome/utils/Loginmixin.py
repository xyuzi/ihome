from django.http import JsonResponse


def flag(fn):
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated:
            return fn(request, *args, **kwargs)
        else:
            return JsonResponse({
                'errno': '4101',
                'errmsg': '没有登录'
            })

    return inner


class LoginMixin(object):
    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super().as_view(*args, **kwargs)
        return flag(view)
