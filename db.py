from hashlib import sha384
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Extra
from tortoise import models, fields
from tortoise.signals import pre_save
from tortoise.contrib.pydantic import pydantic_model_creator


class Model(models.Model):
    class Meta:
        name = "Table"
        abstract = True

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.id}"


class Store(Model):
    Name = fields.CharField(max_length=50)
    CreatedAt = fields.DatetimeField(auto_now_add=True)


class User(Model):
    Name = fields.CharField(max_length=50)
    Admin = fields.BooleanField(default=True)
    Actif = fields.BooleanField(default=True)
    Currency = fields.CharField(max_length=10, default="$")
    Login = fields.DatetimeField(auto_now=True)

    Username = fields.CharField(max_length=30)
    Password = fields.CharField(max_length=300)
    StoreRef = fields.ForeignKeyField(
        "Table.User",
        related_name="StoreGroup",
        on_delete=fields.RESTRICT
    )


BaseUserSchema = pydantic_model_creator(User, exclude_readonly=True)


class UserSchema(BaseUserSchema):
    class Config:
        extra = Extra.allow


class UserUpdateSchema(BaseModel):
    Admin: Optional[bool]
    Actif: Optional[bool]


class LoginUserSchema(BaseModel):
    Username: str
    Password: str


@pre_save(Store)
async def PreSaveUser(model, obj, *args, **kwargs):
    if not obj.id:
        obj.Name = obj.Name + " " + uuid4().hex


@pre_save(User)
async def PreSaveUser(model, obj, *args, **kwargs):
    if not obj.id:
        obj.Password = sha384(bytes(obj.Password, "utf-8")).hexdigest()
