from hmac import compare_digest

from flask import request
from flask_jwt_extended import jwt_required, get_jwt, create_access_token, create_refresh_token, get_jwt_identity
from flask_restful import Resource

from models.blocklist_model import BlockListModel
from models.user_model import UserModel
from schemas.user_schema import UserSchema

USER_ALREADY_REGISTER = "FAIL: User Already Register"
WRONG_CREDENTIAL = "The Email Address Or The Password Are Not Correct"
USER_NOT_FOUND = "User Not Found"
USER_LOGGED_OUT = "User Logged Out Successfully"

user_schema = UserSchema()


class UserRegister(Resource):
    # registering new user & posting access and refresh token keys
    @classmethod
    def post(cls):
        try:
            data = request.get_json()
            user_data = user_schema.load(data)
            user = UserModel.find_user_by_phone(user_data.phone)
            if not user:
                user_data.save_user()
                access_token = create_access_token(identity=user_data.id, fresh=True)
                refresh_token = create_refresh_token(user_data.id)
                return {
                           'access_token': access_token,
                           'refresh_token': refresh_token,
                       }, 201
            return {'msg': USER_ALREADY_REGISTER}, 400
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}


class UserLogin(Resource):
    # logging user in & posting access and refresh token keys
    @classmethod
    def post(cls):
        try:
            data = request.get_json()
            user_data = user_schema.load(data, partial=('full_name',))
            user = UserModel.find_user_by_phone(user_data.phone)
            if user:
                if compare_digest(user.password, user_data.password):
                    access_token = create_access_token(identity=user.id, fresh=True)
                    refresh_token = create_refresh_token(user.id)
                    return {
                        'access_token': access_token,
                        'refresh_token': refresh_token
                    }
                return {'msg': WRONG_CREDENTIAL}, 400
            return {'msg': USER_NOT_FOUND}, 404
        except Exception as e:
            return {'msg': str(e)}, 500


class RefreshToken(Resource):
    # posting new access token key
    @classmethod
    @jwt_required(refresh=True)
    def get(cls):
        try:
            user_id = get_jwt_identity()
            access_token = create_access_token(identity=user_id, fresh=False)
            return {
                'access_token': access_token,
            }
        except Exception as e:
            return {'msg': str(e)}, 500


class UserLogout1(Resource):
    # invoking user access token key
    @jwt_required()
    def get(self):
        try:
            jti = get_jwt()["jti"]
            invoked_jti = BlockListModel(jti=jti)
            invoked_jti.save_jti()
            return {"msg": "Access token revoked"}, 200
        except Exception as e:
            return {'msg': str(e)}, 400


class UserLogout2(Resource):
    # invoking user refresh token key
    @jwt_required(refresh=True)
    def get(self):
        try:
            jti = get_jwt()["jti"]
            invoked_jti = BlockListModel(jti=jti)
            invoked_jti.save_jti()
            return {"msg": "refresh token revoked"}, 200
        except Exception as e:
            return {'msg': str(e)}, 400


class User(Resource):
    # posting user profile
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            user_id = get_jwt_identity()
            user = UserModel.find_user_by_id(user_id)
            if user:
                return user_schema.dump(user), 200
            return {'msg': USER_NOT_FOUND}, 404
        except Exception as e:
            return {'msg': str(e)}, 500

    # updating user profile
    @classmethod
    @jwt_required()
    def put(cls):
        try:
            data = request.get_json()
            user_data = user_schema.load(data, partial=('email', 'full_name', 'phone', 'password'))
            user_id = get_jwt_identity()
            user = UserModel.find_user_by_id(user_id)
            if user:
                if user_data.email:
                    user.email = user_data.email
                if user_data.full_name:
                    user.full_name = user_data.full_name
                if user_data.phone:
                    user.phone = user_data.phone
                user.save_user()
                return user_schema.dump(user), 200
            return {'msg': USER_NOT_FOUND}, 404
        except Exception as e:
            return {'msg': str(e)}, 500


