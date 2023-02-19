import json
from django.core.serializers import serialize
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from users.models import User


class UserDetailView(generic.DetailView):
    model = User

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        return JsonResponse({'id': user.pk, 'name': user.name})


class UserListView(generic.ListView):
    model = User
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        user_list = self.queryset
        return JsonResponse([{'id': user.pk,
                              'name': user.name,
                              } for user in user_list], safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class UserCreateView(generic.CreateView):
    model = User
    fields = ['name']

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        user = User.objects.create(**data)
        result = serialize(User, user)
        return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class UserUpdateView(generic.UpdateView):
    model = User
    fields = ['name']

    def patch(self, request, *args, **kwargs):
        data = json.loads(request.body)
        user = User.objects.get(id=kwargs['pk'])
        user.name = data['name']
        user.save()
        result = serialize(User, user)
        return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class UserDeleteView(generic.DeleteView):
    model = User
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return JsonResponse({'status': 'ok'}, status=200)
