import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from habits.models import Habit


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="testuser",
        password="TestPassword123!",
    )


@pytest.fixture
def habit_data(user):
    return {
        "user": user,
        "place": "Home",
        "time": "12:00",
        "action": "Drink water",
        "duration": 60,
        "periodicity": 1,
    }


@pytest.mark.django_db
def test_create_habit(habit_data):
    habit = Habit.objects.create(**habit_data)
    assert habit.action == "Drink water"


@pytest.mark.django_db
@pytest.mark.parametrize("duration", [121, 180, 300])
def test_duration_validation(habit_data, duration):
    habit_data["duration"] = duration

    with pytest.raises(ValidationError):
        Habit.objects.create(**habit_data)


@pytest.mark.django_db
@pytest.mark.parametrize("periodicity", [0, 8, 14])
def test_periodicity_validation(habit_data, periodicity):
    habit_data["periodicity"] = periodicity

    with pytest.raises(ValidationError):
        Habit.objects.create(**habit_data)


@pytest.mark.django_db
def test_reward_and_related_habit(habit_data):
    pleasant = Habit.objects.create(
        **{
            **habit_data,
            "action": "Take a bath",
            "is_pleasant": True,
        }
    )

    habit_data["reward"] = "Chocolate"
    habit_data["related_habit"] = pleasant

    with pytest.raises(ValidationError):
        Habit.objects.create(**habit_data)


@pytest.mark.django_db
def test_pleasant_habit_cannot_have_reward(habit_data):
    habit_data["is_pleasant"] = True
    habit_data["reward"] = "Chocolate"

    with pytest.raises(ValidationError):
        Habit.objects.create(**habit_data)


@pytest.mark.django_db
def test_cannot_change_related_pleasant_habit(habit_data):
    pleasant = Habit.objects.create(
        **{
            **habit_data,
            "action": "Watch a movie",
            "is_pleasant": True,
        }
    )

    Habit.objects.create(
        **{
            **habit_data,
            "action": "Exercise",
            "related_habit": pleasant,
        }
    )

    pleasant.is_pleasant = False

    with pytest.raises(ValidationError):
        pleasant.save()
