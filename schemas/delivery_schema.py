from ma import ma
from models.delivery_model import DeliveryModel
from schemas.order_schema import OrderSchema
from schemas.user_schema import UserSchema


class DeliverySchema(ma.SQLAlchemyAutoSchema):
    orders = ma.Nested(OrderSchema, many=True)
    user = ma.Nested(UserSchema)

    class Meta:
        model = DeliveryModel
        dump_only = ('id',)
        include_fk = True
        load_instance = True
