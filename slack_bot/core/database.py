import time
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Type

from bson import ObjectId
from pydantic import GetCoreSchemaHandler, BaseModel, Field, AnyUrl
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from slack_bot.core.config import settings


class PyObjectId:
    @classmethod
    def __get_pydantic_core_schema__(
            cls, source: type, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.with_info_after_validator_function(
            cls.validate, core_schema.str_schema()
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls, schema: core_schema.CoreSchema, handler: GetCoreSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string"}

    @classmethod
    def validate(cls, value: str) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError(f"Invalid ObjectId: {value}")
        return ObjectId(value)

    def __getattr__(self, item):
        return getattr(self.__dict__['value'], item)

    def __init__(self, value: str = None):
        if value is None:
            self.value = ObjectId()
        else:
            self.value = self.validate(value)

    def __str__(self):
        return str(self.value)


class MongoBaseModel(BaseModel):
    id: str = Field(default_factory=lambda: str(PyObjectId()))

    class Config:
        arbitrary_types_allowed = True

    def to_mongo(self) -> Dict[str, Any]:
        def model_to_dict(model: BaseModel) -> Dict[str, Any]:
            doc = {}
            for name, value in model._iter():
                key = model.__fields__[name].alias or name

                if isinstance(value, BaseModel):
                    doc[key] = model_to_dict(value)
                elif isinstance(value, list) and all(isinstance(i, BaseModel) for i in value):
                    doc[key] = [model_to_dict(item) for item in value]
                elif value and isinstance(value, Enum):
                    doc[key] = value.value
                elif value and isinstance(value, AnyUrl):
                    doc[key] = str(value)
                else:
                    doc[key] = value

            return doc

        result = model_to_dict(self)
        return result

    @classmethod
    def from_mongo(cls, data: Dict[str, Any]):
        def restore_enums(inst: Any, model_cls: Type[BaseModel]) -> None:
            for name, field in model_cls.__fields__.items():
                value = getattr(inst, name)
                if field and isinstance(field.annotation, type) and issubclass(field.annotation, Enum):
                    setattr(inst, name, field.annotation(value))
                elif isinstance(value, BaseModel):
                    restore_enums(value, value.__class__)
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, BaseModel):
                            restore_enums(item, item.__class__)
                        elif isinstance(field.annotation, type) and issubclass(field.annotation, Enum):
                            value[i] = field.annotation(item)
                elif isinstance(value, dict):
                    for k, v in value.items():
                        if isinstance(v, BaseModel):
                            restore_enums(v, v.__class__)
                        elif isinstance(field.annotation, type) and issubclass(field.annotation, Enum):
                            value[k] = field.annotation(v)

        if data is None:
            return None
        instance = cls(**data)
        restore_enums(instance, instance.__class__)
        return instance


def update_snowflake_token():
    while True:
        try:
            time.sleep(50 * 60)
            settings.set_snowflake_connection()
        except Exception as e:
            print(e)
            time.sleep(60 * 30)
