import pytest
from rest_framework import status


@pytest.mark.django_db
def test_ad_create(client, user, category, access_token):
    data = {
        'author_id': user.pk,
        'category_id': category.pk,
        'name': 'Стол из дуба',
        'price': 200,
        'address': 'draft',
    }
    expected_data = {
        'id': 1,
        'is_published': False,
        'name': 'Стол из дуба',
        'price': 200,
        'description': None,
        'image': None,
        'author_id': user.pk,
        'category_id': category.pk,
        'address': 'draft',
    }
    response = client.post('/ad/', data=data, HTTP_AUTHORIZATION='Bearer ' + access_token)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == expected_data

