import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from habits.models import Habit


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="testuser",
        password="TestPassword123!",
    )


@pytest.fixture
def other_user(db):
    return get_user_model().objects.create_user(
        username="otheruser",
        password="TestPassword123!",
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def habit_data():
    return {
        "place": "Home",
        "time": "12:00",
        "action": "Drink water",
        "duration": 60,
        "periodicity": 1,
    }


@pytest.fixture
def habit(user, habit_data):
    return Habit.objects.create(user=user, **habit_data)


@pytest.mark.django_db
def test_registration(client):
    response = client.post(
        "/api/users/register/",
        {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 201
    assert get_user_model().objects.filter(username="newuser").exists()
    assert "password" not in response.data


@pytest.mark.django_db
def test_jwt_login(client, user):
    response = client.post(
        "/api/users/login/",
        {
            "username": "testuser",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_unauthorized_access(client):
    response = client.get("/api/habits/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_habit(auth_client, user, habit_data):
    response = auth_client.post(
        "/api/habits/",
        habit_data,
    )

    assert response.status_code == 201
    assert Habit.objects.filter(user=user).count() == 1
    assert response.data["user"] == user.id


@pytest.mark.django_db
def test_list_own_habits(auth_client, habit, other_user):
    Habit.objects.create(
        user=other_user,
        place="Office",
        time="13:00",
        action="Exercise",
        duration=60,
    )

    response = auth_client.get("/api/habits/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == habit.id


@pytest.mark.django_db
def test_update_habit(auth_client, habit):
    response = auth_client.patch(
        f"/api/habits/{habit.id}/",
        {"action": "Read a book"},
    )

    assert response.status_code == 200
    habit.refresh_from_db()
    assert habit.action == "Read a book"


@pytest.mark.django_db
def test_delete_habit(auth_client, habit):
    response = auth_client.delete(f"/api/habits/{habit.id}/")

    assert response.status_code == 204
    assert not Habit.objects.filter(id=habit.id).exists()


@pytest.mark.django_db
def test_cannot_modify_other_user_habit(auth_client, other_user, habit_data):
    other_habit = Habit.objects.create(
        user=other_user,
        **habit_data,
    )

    response = auth_client.patch(
        f"/api/habits/{other_habit.id}/",
        {"action": "Changed"},
    )

    assert response.status_code == 404

    response = auth_client.delete(f"/api/habits/{other_habit.id}/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_public_habits(client, habit, other_user, habit_data):
    habit.is_public = True
    habit.save()

    Habit.objects.create(
        user=other_user,
        is_public=False,
        **habit_data,
    )

    response = client.get("/api/habits/public/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == habit.id


@pytest.mark.django_db
def test_pagination(auth_client, user, habit_data):
    for i in range(7):
        Habit.objects.create(
            user=user,
            **{**habit_data, "action": f"Habit {i}"},
        )

    response = auth_client.get("/api/habits/")

    assert response.status_code == 200
    assert response.data["count"] == 7
    assert len(response.data["results"]) == 5

    response = auth_client.get("/api/habits/?limit=5&offset=5")

    assert len(response.data["results"]) == 2


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field,value",
    [
        ("duration", 121),
        ("periodicity", 8),
        ("periodicity", 0),
    ],
)
def test_invalid_habit_data(auth_client, habit_data, field, value):
    response = auth_client.post(
        "/api/habits/",
        {**habit_data, field: value},
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_invalid_related_habit(auth_client, habit, habit_data):
    response = auth_client.post(
        "/api/habits/",
        {**habit_data, "related_habit": habit.id},
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_pleasant_habit_with_reward(auth_client, habit_data):
    response = auth_client.post(
        "/api/habits/",
        {
            **habit_data,
            "is_pleasant": True,
            "reward": "Chocolate",
        },
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_cannot_update_related_pleasant_habit(auth_client, user, habit_data):
    pleasant = Habit.objects.create(
        user=user,
        **{
            **habit_data,
            "action": "Watch a movie",
            "is_pleasant": True,
        },
    )

    Habit.objects.create(
        user=user,
        **{
            **habit_data,
            "action": "Exercise",
            "related_habit": pleasant,
        },
    )

    response = auth_client.patch(
        f"/api/habits/{pleasant.id}/",
        {"is_pleasant": False},
    )

    assert response.status_code == 400
    assert "is_pleasant" in response.data

    pleasant.refresh_from_db()
    assert pleasant.is_pleasant is True
