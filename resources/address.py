import traceback

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_restful import Resource

from models.address_model import AddressModel
from schemas.address_schema import AddressSchema

address_schema = AddressSchema()
address_list = AddressSchema(many=True)


class UserAddress(Resource):

    # adding and updating user address
    @classmethod
    @jwt_required()
    def post(cls):
        user_id = get_jwt_identity()
        data = request.get_json()
        address = AddressModel.find_address_by_user(user_id)
        if not address:
            data['user_id'] = user_id
            user_address = address_schema.load(data)
            try:
                user_address.save_address()
                return {'msg': 'success: new address added'}, 201
            except Exception as e:
                traceback.print_exc()
                return {'msg': str(e)}
        if data['state']:
            address.state = data['state']
        if data['city']:
            address.city = data['city']
        if data['street']:
            address.street = data['street']
        if data['address_detail']:
            address.address_detail = data['address_detail']
        address.save_address()
        return {'msg': 'success: address updated'}, 200

    # posting user address
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            user_id = get_jwt_identity()
            return address_schema.dump(AddressModel.find_address_by_user(user_id)), 200
        except Exception as e:
            return{'msg': f'fail: {str(e)}'}, 500


class AddressList(Resource):
    # posting all users addresses // admin privilege require
    @classmethod
    @jwt_required()
    def get(cls):
        claim = get_jwt()
        if not claim['is_admin']:
            return {'msg': 'fail: user not admin'}, 400
        return {'address': address_list.dump(AddressModel.find_all())}
