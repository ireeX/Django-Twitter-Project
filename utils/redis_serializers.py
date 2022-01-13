from django.core import serializers
from utils.json_encoder import JSONEncoder
from django.core.serializers.json import Deserializer


class DjangoModelSerializer:

    @classmethod
    def serialize(cls, instance):
        # The `serializer.serialize()` needs a QuerySet
        # or a list of ORM objects as input.
        # This is why `[instance]` is used as input.
        return serializers.serialize('json', [instance], cls=JSONEncoder)

    @classmethod
    def deserialize(cls, serialized_data):
        # `.object` is used to get
        return list(serializers.deserialize('json', serialized_data))[0].object