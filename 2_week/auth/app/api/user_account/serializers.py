from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field, root_validator

from app.api.base_schemas import BaseResponse, Missing, MissingType
from app.core.user_account.enums import ProfilePublicity


class UserBalance(BaseModel):
    """Схема вывода краткого вида баланса пользователя."""

    real: float = Field(description="Общее количество реальных денег")
    bonus: float = Field(description="Общее количество бонусных денег")
    total: float = Field(description="Сумма реальных денег и бонусов")
    currency: str = Field(default="RUB", description="Буквенное сокращение валюты, к которой приведен баланс")
    last_pay_method: Optional[int] = Field(None, description="ID последнего способа оплаты")
    price_discount_ttl: Optional[int] = Field(
        None,
        description="Время (в секундах) до истечения самой ранней скидки пользователей",
    )

    class Config:
        orm_mode = True


class UserSerializer(BaseModel):
    """Общие данные зарегистрированного юзера."""

    id: int = Field(description="ID пользователя")
    is_anon: bool = Field(description="Является ли пользователь анонимом")
    login: str = Field(description="Логин юзера")
    first_name: Optional[str] = Field(None, description="Имя")
    middle_name: Optional[str] = Field(None, description="Отчество")
    last_name: Optional[str] = Field(None, description="Фамилия")
    email: Optional[str] = Field(None, description="Электронная почта")
    account_month_lifetime: Optional[int] = Field(None, description="Время жизни аккаунта в месяцах")
    is_password_null: Optional[bool] = Field(None, description="Статус заполненности пароля")

    class Config:
        orm_mode = True


class UserProfileSerializer(BaseModel):
    """Данные о профиле юзера."""

    age: Optional[int] = Field(None, description="Возраст пользователя")
    nickname: Optional[str] = Field(None, description="Отображаемое имя пользователя")
    country_id: Optional[int] = Field(None, description="Айди страны пользователя")
    city_name: Optional[str] = Field(None, description="Название страны пользователя")
    telegram: Optional[str] = Field(None, description="Телеграм аккаунт пользователя")
    address: Optional[str] = Field(None, description="Адрес пользователя")
    ui_lang: Optional[str] = Field(None, description="Код языка интерфейса")
    is_email_confirmed: Optional[bool] = Field(None, description="Статус подтверждения почты")
    is_avatar_uploaded: Optional[bool] = Field(None, description="Статус наличия загруженного аватара")
    is_safemode_enabled: Optional[bool] = Field(None, description="Защита от порно, не показывать порнокниги")
    is_cookie_agreement_accepted: Optional[bool] = Field(None, description="Согласился ли юзер на хранение кук")
    profile_privacy: Optional[ProfilePublicity] = Field(None, description="Статус приватности аккаунта")

    class Config:
        orm_mode = True


class UserPhoneSerializer(BaseModel):
    number: str = Field(..., description="Номер телефона")
    country_code: str = Field(..., description="Страна номера телефона")
    is_verified: bool = Field(..., description="Подтвержден или нет")

    class Config:
        orm_mode = True


class UserGroupSerializer(BaseModel):
    id: int = Field(..., description="Айди группы")
    name: str = Field(..., description="Название группы")
    is_reader: bool = Field(..., description="Могут ли читать книги из магазина")

    class Config:
        orm_mode = True


class UserAccount(UserSerializer):
    profile: UserProfileSerializer
    phone: Optional[UserPhoneSerializer]
    groups: List[UserGroupSerializer]

    class Config:
        orm_mode = True


class UserAccountSerializer(BaseModel):
    data: UserAccount


class UserAccountResponseSerializer(BaseResponse):
    payload: UserAccountSerializer


class UserProfileWriteSerializer(BaseModel):
    address: Union[Optional[str], MissingType] = Field(Missing, description="Адрес пользователя")
    city_name: Union[Optional[str], MissingType] = Field(Missing, description="Город пользователя")
    telegram: Union[Optional[str], MissingType] = Field(Missing, description="Телеграм логин пользователя")
    skype: Union[Optional[str], MissingType] = Field(Missing, description="Скайп логин пользователя")
    nickname: Union[Optional[str], MissingType] = Field(Missing, description="Публичное имя пользователя")

    class Config:
        arbitrary_types_allowed = True

    @root_validator
    def at_least_one_field_present(cls, field_values: dict[str, Any]) -> dict[str, Any]:
        if all(isinstance(value, MissingType) for value in field_values.values()):
            raise ValueError("one of serializer fields must have a value")
        return field_values
