from django.core.serializers import serialize
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet

from ads.models import Ad, Selection, Category
from ads.permissions import IsOwner, IsStaff
from ads.serializers import AdSerializer, AdDetailSerializer, AdListSerializer, SelectionSerializer, \
    SelectionCreateSerializer, CategorySerializer


def root(request):
    return JsonResponse({'status': 'ok'})


def serialize(model, values):
    if isinstance(values, model):
        values = [values]
    else:
        list(values)


class CatViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class AdDetailView(generic.DetailView):
    model = Ad

    def get(self, request, *args, **kwargs):
        ad = self.get_object()
        return JsonResponse({'id': ad.pk,
                             'name': ad.name,
                             'author': ad.author,
                             'price': ad.price,
                             'description': ad.description,
                             'address': ad.address,
                             'is_published': ad.is_published,
                             })


@method_decorator(csrf_exempt, name='dispatch')
class AdUploadImageView(generic.UpdateView):
    model = Ad
    fields = ['image']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.image = request.FILES.get('image')
        self.object.save()

        result = serialize(self.model, self.object)

        return JsonResponse(result, safe=False)


class AdViewSet(ModelViewSet):
    default_serializer = AdSerializer
    queryset = Ad.objects.order_by('-price')
    serializers = {'retrieve': AdDetailSerializer,
                   'list': AdListSerializer,
                   }

    default_permission = [AllowAny]
    permissions = {'retrieve': [IsAuthenticated],
                   'update': [IsAuthenticated, IsOwner | IsStaff],
                   'partial_update': [IsAuthenticated, IsOwner | IsStaff],
                   'destroy': [IsAuthenticated, IsOwner | IsStaff],
                   }

    def get_permissions(self):
        return [permission() for permission in self.permissions.get(self.action, self.default_permission)]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.default_serializer)

    def list(self, request, *args, **kwargs):
        categories = request.GET.getlist('cat')
        if categories:
            self.queryset = self.queryset.filter(category_id__in=categories)
        text = request.GET.get('text')
        if text:
            self.queryset = self.queryset.filter(name__icontains=text)
        location = request.GET.get('location')
        if location:
            self.queryset = self.queryset.filter(author_id__location__name__icontains=location)
        price_from = request.GET.get('price_from')
        if price_from:
            self.queryset = self.queryset.filter(price__gte=text)
        price_to = request.GET.get('price_to')
        if price_to:
            self.queryset = self.queryset.filter(price__lte=text)

        return super().list(request, *args, **kwargs)


class SelectionViewSet(ModelViewSet):
    queryset = Selection.objects.all()

    default_permission = [AllowAny]
    permissions = {'create': [IsAuthenticated],
                   'update': [IsAuthenticated, IsOwner],
                   'partial_update': [IsAuthenticated, IsOwner],
                   'destroy': [IsAuthenticated, IsOwner],
                   }

    default_serializer = SelectionSerializer
    serializers = {'create': SelectionCreateSerializer}

    def get_permissions(self):
        return [permission() for permission in self.permissions.get(self.action, self.default_permission)]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.default_serializer)
