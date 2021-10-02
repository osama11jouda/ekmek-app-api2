import traceback

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_uploads import configure_uploads, patch_request_class
from marshmallow import ValidationError


from libs.image_helper import IMAGE_SET
from models.blocklist_model import BlockListModel
from models.user_model import UserModel
from resources.address import (UserAddress, AddressList, )
from resources.admin import (UsersList, AddingBalance, AddingAdmin, DeletingAdmin, AddingDelivery, DeletingDelivery,
                             AdminsList, DeliveriesList)
from resources.image import (UserAvatar, DeleteAvatarImage, ItemImage, DeleteItemImage)
from resources.item import (RegisterItem, UpdateItem, DeleteItem, ItemList)
from resources.order import (OrderIsPacked, OrdersList, OrderIsShipped, OrderIsDelivered, Order, UpdateOrder,
                             DeleteOrder, UserOrders, OrderPayment)
from resources.user import (UserRegister, UserLogin, RefreshToken, UserLogout1, UserLogout2, User)

app = Flask(__name__)
load_dotenv('.env', verbose=True)
app.config.from_object('default_config.py')
app.config.from_envvar('APPLICATION_SETTINGS', silent=True)

patch_request_class(app, 10 * 1024 * 1024)
configure_uploads(app, IMAGE_SET)
api = Api(app)
jwt = JWTManager(app)


@app.errorhandler(ValidationError)
def handle_validation_error(err):
    traceback.print_exc()
    return jsonify(err.messages)


@jwt.additional_claims_loader
def handle_additional_claims(identity):
    if identity == 1:
        return {'is_admin': True}
    user = UserModel.find_user_by_id(identity)
    if user.is_admin:
        return {'is_admin': True}
    return {'is_admin': False}


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(_, jwt_payload):
    jti = jwt_payload["jti"]
    token = BlockListModel.find_jti(jti)
    return token is not None


# user routes
api.add_resource(UserRegister, '/user/register')  # post --ok
api.add_resource(UserLogin, '/user/login')  # post  --ok
api.add_resource(RefreshToken, '/user/refresh')  # get  --ok
api.add_resource(UserLogout1, '/user/token/logout')  # get invoke access token  --ok
api.add_resource(UserLogout2, '/user/refresh/logout')  # get invoke refresh token  --ok
api.add_resource(UserAddress, '/user/address')  # post for adding address & get for getting user address  --ok  --ok
api.add_resource(User, '/user')  # for getting user data & updating user data (get , put) --ok  --ok
api.add_resource(UserAvatar, '/user/avatar')  # post  --ok
api.add_resource(DeleteAvatarImage, '/user/avatar/delete/<string:path>')  # delete  --ok

api.add_resource(ItemList, '/user/items')  # get  --ok
api.add_resource(Order, '/user/order')  # post  --ok
api.add_resource(UpdateOrder, '/user/order/update/<int:order_id>')  # put  --ok
api.add_resource(DeleteOrder, '/user/order/delete/<int:order_id>')  # delete  --ok
api.add_resource(OrderPayment, '/user/order/payment/<int:order_id>')  # post  --ok
api.add_resource(UserOrders, '/user/orders')  # get  --ok

# admin routes
api.add_resource(RegisterItem, '/admin/item/register')  # post  --ok
api.add_resource(UpdateItem, '/admin/item/update/<int:item_id>')  # put  --ok
api.add_resource(DeleteItem, '/admin/item/delete/<int:item_id>')  # delete  --ok
api.add_resource(ItemImage, '/admin/item/image/<int:item_id>')  # post  --ok
api.add_resource(DeleteItemImage, '/admin/image/delete/<int:item_id>/<string:img_name>')  # delete  --ok

api.add_resource(AddingBalance, '/admin/balance/add/<int:user_id>')  # post --ok

api.add_resource(AddingAdmin, '/admin/add_admin/<int:user_id>')  # get --ok
api.add_resource(DeletingAdmin, '/admin/delete_admin/<int:user_id>')  # delete --ok
api.add_resource(AdminsList, '/admin/admin_list')  # get --ok

api.add_resource(AddingDelivery, '/admin/delivery/add')  # post  --ok
api.add_resource(DeletingDelivery, '/admin/delivery/delete/<int:delivery_id>')  # get  --ok
api.add_resource(DeliveriesList, '/admin/deliveries')  # get  --ok

api.add_resource(UsersList, '/admin/users')  # get  --ok
api.add_resource(AddressList, '/admin/users/addresses')  # get  --ok

api.add_resource(OrdersList, '/admin/orders')  # get
api.add_resource(OrderIsPacked, '/admin/order/packed/<int:order_id>')  # get
api.add_resource(OrderIsShipped, '/admin/order/shipped/<int:order_id>')  # get
api.add_resource(OrderIsDelivered, '/admin/order/delivered/<int:order_id>')  # get


if __name__ == '__main__':

    app.run(port=5000)
