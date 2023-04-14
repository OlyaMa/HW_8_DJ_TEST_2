import pytest
from rest_framework.test import APIClient
from model_bakery import baker
from students.models import Student, Course
from pprint import pprint




@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


@pytest.fixture
def course_factory(student_factory):
    def factory(*args, **kwargs):
        students_set = student_factory(_quantity=3)
        return baker.make(Course, students=students_set, *args, **kwargs, make_m2m=True)
    return factory

# проверка получения 1го курса (retrieve-логика)
@pytest.mark.django_db
def test_get_one_course(client, course_factory, student_factory):
    courses = course_factory(_quantity=10)
    response = client.get(f'/api/v1/courses/{courses[0].id}/')
    assert response.status_code == 200


# проверка получения списка курсов (list-логика)
@pytest.mark.django_db
def test_get_course_list(client, student_factory, course_factory):
    courses = course_factory(_quantity=5)
    # for i in courses:
    #     pprint(i.__dict__)
    response = client.get('/api/v1/courses/')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(courses)
    for i, m in enumerate(data):
        assert m['name'] == courses[i].name


# проверка фильтрации списка курсов по id
@pytest.mark.django_db
def test_course_filter_id(client, student_factory, course_factory):
    courses = course_factory(_quantity=10)
    response = client.get('/api/v1/courses/', data={'id': courses[1].id})
    assert response.status_code == 200


# проверка фильтрации списка курсов по name
@pytest.mark.django_db
def test_course_filter_name(client, student_factory, course_factory):
    courses = course_factory(_quantity=10)
    response = client.get('/api/v1/courses/', data={'name': courses[1].name})
    assert response.status_code == 200



# тест успешного создания курса
@pytest.mark.django_db
def test_course_create(client):
    count = Course.objects.count()
    response = client.post('/api/v1/courses/', data={'name': 'course 1', 'students': []})
    assert response.status_code == 201
    assert Course.objects.count() == count + 1


# тест успешного обновления курса
@pytest.mark.django_db
def test_course_update(client, course_factory):
    courses = course_factory(_quantity=10)
    response = client.patch(f'/api/v1/courses/{courses[5].id}/', data={'name': 'Python'})
    assert response.status_code == 200


# тест успешного удаления курса
@pytest.mark.django_db
def test_course_delete(client, course_factory):
    courses = course_factory(_quantity=10)
    # for i in courses:
    #     pprint(i.__dict__)
    num = courses[3].id
    response = client.delete(f'/api/v1/courses/{num}/')
    resp = client.get(f'/api/v1/courses/{num}/')
    assert response.status_code == 204
    assert resp.status_code == 404
