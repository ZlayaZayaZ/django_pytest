import random

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker
from django.urls import reverse

from students.models import Student, Course


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


# проверка получения одного курса (retrieve-логика)
@pytest.mark.django_db
def test_course_retrieve(client, course_factory):
    courses = course_factory(_quantity=5)
    ids = [course.id for course in courses]
    id = random.choice(ids)
    url = reverse('courses-detail', kwargs={'pk': id})
    response = client.get(url)
    db_course = Course.objects.get(pk=id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('name') == db_course.name


# проверка получения списка курсов (list-логика)
@pytest.mark.django_db
def test_courses_list(client, course_factory, student_factory):

    students = student_factory(_quantity=5)
    courses = course_factory(_quantity=5)

    url = reverse('courses-list')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == len(courses)
    for i, c in enumerate(data):
        assert c['name'] == courses[i].name


# проверка фильтрации списка курсов по id
@pytest.mark.django_db
def test_filtering_course_by_id(client, course_factory):

    courses = course_factory(_quantity=5)

    ids = [course.id for course in courses]
    id = random.choice(ids)

    url = reverse('courses-list')
    url_filter = url + f'?id={id}'
    response = client.get(url_filter)

    db_course = Course.objects.get(pk=id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['name'] == db_course.name


# проверка фильтрации списка курсов по name
@pytest.mark.django_db
def test_filtering_course_by_name(client, course_factory):
    courses = course_factory(_quantity=5)

    names = [course.name for course in courses]
    name = random.choice(names)

    url = reverse('courses-list')
    url_filter = url + f'?name={name}'
    response = client.get(url_filter)

    db_course = Course.objects.get(name=name)

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['id'] == db_course.id


# тест успешного создания курса
@pytest.mark.django_db
def test_create_courses(client):

    count = Course.objects.count()
    url = reverse('courses-list')
    data = {'name': 'django', }

    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert Course.objects.count() == count + 1
    assert response.data['name'] == data['name']


# тест успешного обновления курса
@pytest.mark.django_db
def test_update_courses(client, course_factory):

    courses = course_factory(_quantity=5)
    ids = [course.id for course in courses]
    id = random.choice(ids)
    url = reverse('courses-detail', kwargs={'pk': id})

    data = {'name': 'django', }

    response = client.put(url, data, format='json')

    db_course = Course.objects.get(pk=id)

    assert response.status_code == status.HTTP_200_OK
    assert db_course.name == data['name']


# тест успешного удаления курса
@pytest.mark.django_db
def test_delete_courses(client, course_factory):

    courses = course_factory(_quantity=5)
    count = Course.objects.count()
    ids = [course.id for course in courses]
    id = random.choice(ids)
    url = reverse('courses-detail', kwargs={'pk': id})

    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Course.objects.count() == count - 1


