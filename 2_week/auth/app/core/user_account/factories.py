import random

import factory

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
