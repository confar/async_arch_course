import random

import factory
from auth_utils.sid import create_sid

from app.core.user_account.models import (
    LibraryUser,
    User,
    UserPhone,
    UserProfile,
    UserSession,
    UserSubscribes,
)
from tests.factories import DBLBaseModelFactory


class UserFactory(DBLBaseModelFactory):
    id = factory.Sequence(lambda n: n + 1)
    first_name = factory.Faker("first_name", locale="ru_RU")
    last_name = factory.Faker("last_name", locale="ru_RU")
    login = factory.LazyAttribute(lambda o: f"{o.last_name}_{o.first_name}")
    email = factory.LazyAttribute(lambda o: f"{o.first_name}@test.com")

    profile = factory.RelatedFactory("app.core.user_account.factories.UserProfileFactory", factory_related_name="user")
    phone = factory.RelatedFactory("app.core.user_account.factories.UserPhoneFactory", factory_related_name="user")
    session = factory.RelatedFactory("app.core.user_account.factories.UserSessionFactory", factory_related_name="user")

    class Meta:
        model = User


class UserSessionFactory(DBLBaseModelFactory):
    user = factory.SubFactory(UserFactory, session=None)
    user_id = factory.LazyAttribute(lambda obj: obj.user.id)

    @factory.lazy_attribute
    def sid(self) -> str:
        from settings.config import get_settings

        settings = get_settings()
        sid = create_sid(secret_key=settings.SECRET_KEY)

        return sid

    class Meta:
        model = UserSession


class UserProfileFactory(DBLBaseModelFactory):
    user = factory.SubFactory(UserFactory, profile=None)
    user_id = factory.LazyAttribute(lambda obj: obj.user.id)
    birthday = factory.Faker("date_between", start_date="-40y", end_date="-8y")
    avatar_picture_extension = factory.LazyAttribute(lambda _: random.choice(["jpg", None]))
    nickname = factory.Faker("user_name", locale="ru_RU")

    class Meta:
        model = UserProfile


class UserPhoneFactory(DBLBaseModelFactory):
    user = factory.SubFactory(UserFactory, phone=None)
    user_id = factory.LazyAttribute(lambda obj: obj.user.id)
    country_code = factory.Faker("country_code")
    number = factory.Faker("msisdn", locale="ru_RU")
    is_verified = factory.Faker("pybool")
    inverted_msisdn = factory.LazyAttribute(lambda o: o.number[::-1])

    class Meta:
        model = UserPhone


class LibraryUserFactory(DBLBaseModelFactory):
    library_id = factory.Faker("random_int")
    user_id = factory.Faker("random_int")
    is_blocked = 0

    class Meta:
        model = LibraryUser


class UserSubscribesFactory(DBLBaseModelFactory):
    user_id = factory.Faker("random_int")
    service_id = factory.Faker("random_int")

    class Meta:
        model = UserSubscribes


class ProfileBodyFactory(factory.DictFactory):
    telegram = factory.Faker("text", max_nb_chars=50)
    city_name = factory.Faker("text", max_nb_chars=50)
    address = factory.Faker("text", max_nb_chars=50)
    nickname = factory.Faker("text", max_nb_chars=50)
