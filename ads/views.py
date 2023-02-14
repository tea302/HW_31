import json

from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from django.conf import settings

from ads.models import Category, Ad


def root(request):
    return JsonResponse({'status': 'ok'})


def serialize(model, values):
    if isinstance(values, model):
        values = [values]

    result = []

    for value in values:
        data = {}
        for field in model._meta.get_fields():
            if field.is_relation:
                continue
            if field.name == 'image':
                data[field.name] = getattr(value.image, 'url', None)
            else:
                data[field.name] = getattr(value, field.name)
        result.append(data)

        return result


class CategoryDetailView(generic.DetailView):
    model = Category

    def get(self, request, *args, **kwargs):
        category = self.get_object()
        return JsonResponse({'id': category.pk, 'name': category.name})


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


# @method_decorator(csrf_exempt, name='dispatch')
# class AdListCreateView(View):
#     def get(self, request):
#         ad_list = Ad.objects.all()
#         return JsonResponse([{'id': ad.pk,
#                               'name': ad.name,
#                               'author': ad.author,
#                               'price': ad.price,
#                               'description': ad.description,
#                               'address': ad.address,
#                               'is_published': ad.is_published,
#                               } for ad in ad_list], safe=False)
#
#     def post(self, request):
#         ad_data = json.loads(request.body)
#         new_ad = Ad.objects.create(**ad_data)
#         return JsonResponse({'id': new_ad.pk,
#                              'name': new_ad.name,
#                              'author': new_ad.author,
#                              'price': new_ad.price,
#                              'description': new_ad.description,
#                              'address': new_ad.address,
#                              'is_published': new_ad.is_published,
#                              })


class CategoryListView(generic.ListView):
    model = Category
    queryset = Category.objects.all()

    def get(self, request, *args, **kwargs):
        cat_list = self.queryset
        return JsonResponse([{'id': cat.pk,
                              'name': cat.name,
                              } for cat in cat_list], safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryCreateView(generic.CreateView):
    model = Category
    fields = ['name']

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        category = Category.objects.create(**data)
        result = serialize(Category, category)
        return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryUpdateView(generic.UpdateView):
    model = Category
    fields = ['name']

    def patch(self, request, *args, **kwargs):
        data = json.loads(request.body)
        category = Category.objects.get(id=kwargs['pk'])
        category.name = data['name']
        category.save()
        result = serialize(Category, category)
        return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryDeleteView(generic.DeleteView):
    model = Category
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return JsonResponse({'status': 'ok'}, status=200)


class AdListView(generic.ListView):
    model = Ad
    queryset = Ad.objects.all()

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        self.object_list = self.object_list.select_related('author_id').order_by('-price')
        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        ads = serialize(Ad, page_obj)

        response = {
            'items': ads,
            'num_pages': page_obj.paginator.num_pages,
            'total': page_obj.paginator.count
        }

        return JsonResponse(
            response,
            safe=False,
        )


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
