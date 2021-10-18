from ma import ma
from models.user_model import UserModel


class UserSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = UserModel
        load_only = ('password',)
        dump_only = ('id',)
        include_fk = True
        load_instance = True
