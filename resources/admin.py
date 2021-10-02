from flask import request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask_restful import Resource

from models.delivery_model import DeliveryModel
from models.user_model import UserModel
from schemas.delivery_schema import DeliverySchema
from schemas.user_schema import UserSchema

user_schema = UserSchema()


class AddingBalance(Resource):
    # adding balance to user // admin privilege require
    @classmethod
    @jwt_required()
    def post(cls, user_id: int):
        try:
            data = request.get_json()
            claim = get_jwt()
            if not claim['is_admin']:
                return {'msg': 'you are not admin'}, 400
            user = UserModel.find_user_by_id(user_id)
            if not user:
                return {'msg': 'user not found'}, 404
            user.current_balance = user.current_balance + data['value']
            user.save_user()
            return {'msg': 'balance updated successfully'}, 200
        except Exception as e:
            return {'msg': str(e)}, 500


class AddingAdmin(Resource):
    # adding admin // admin privilege require
    @classmethod
    @jwt_required()
    def get(cls, user_id: int):
        try:
            claim = get_jwt()
            if not claim['is_admin']:
                return {'msg': 'fail: you are not admin'}, 400
            user = UserModel.find_user_by_id(user_id)
            if not user:
                return {'msg': 'fail: user not found'}, 404
            user.is_admin = True
            user.save_user()
            return {'msg': 'success: new admin created'}, 200
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}, 500


class DeletingAdmin(Resource):
    # deleting admin // admin privilege require
    @classmethod
    @jwt_required()
    def delete(cls, user_id: int):
        try:
            admin_id = get_jwt_identity()
            claim = get_jwt()
            if not claim['is_admin']:
                return {'msg': 'fail: you are not admin'}, 400
            user = UserModel.find_user_by_id(user_id)
            if not user:
                return {'msg': 'fail: user not found'}, 404
            if user.id == admin_id or user.id == 1:
                return {'msg': 'fail: admin can not remove'}, 400
            user.is_admin = False
            user.save_user()
            return {'msg': 'success: admin deleted'}, 200
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}, 500


delivery_schema = DeliverySchema()


class AddingDelivery(Resource):
    # adding delivery // admin privilege require
    @classmethod
    @jwt_required()
    def post(cls):
        try:
            claim = get_jwt()
            if not claim['is_admin']:
                return {'msg': 'fail: you are not admin'}, 400
            data = request.get_json()
            user = UserModel.find_user_by_id(data['user_id'])
            if not user:
                return {'msg': 'fail: user not found'}, 404
            delivery = delivery_schema.load(data)
            delivery.save_delivery()
            return delivery_schema.dump(delivery), 200
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}, 500


class DeletingDelivery(Resource):
    # deleting delivery  // admin privilege require
    @classmethod
    @jwt_required()
    def get(cls, delivery_id: int):
        try:
            claim = get_jwt()
            if not claim['is_admin']:
                return {'msg': 'fail: you are not admin'}, 400
            delivery = DeliveryModel.find_delivery_by_id(delivery_id)
            if not delivery:
                return {'msg': 'fail: delivery not found'}, 404
            delivery.delete_delivery()
            return {'msg': 'success: delivery deleted'}, 200
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}, 500


class UsersList(Resource):
    # posting users list  // admin privilege require
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            claim = get_jwt()
            if not claim['is_admin']:
                return {'msg': 'fail: user is not admin'}, 400
            return {'users': user_schema.dump(UserModel.find_all(), many=True)}, 200
        except Exception as e:
            return {'msg': str(e)}, 500


class AdminsList(Resource):
    # posting admins list  // admin privilege require
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            claim = get_jwt()
            if not claim['is_admin']:
                return {'msg': 'fail: user is not admin'}, 400
            return {'admins': user_schema.dump(UserModel.find_all_admins(), many=True)}, 200
        except Exception as e:
            return {'msg': str(e)}, 500


class DeliveriesList(Resource):
    # posting deliveries list  // admin privilege require
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            claim = get_jwt()
            if not claim['is_admin']:
                return {'msg': 'fail: user is not admin'}, 400
            return {'deliveries': delivery_schema.dump(DeliveryModel.find_all(), many=True)}, 200
        except Exception as e:
            return {'msg': str(e)}, 500
