from collections import Counter

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_restful import Resource

from models.item_model import ItemModel
from models.order_model import ItemInOrder, OrderModel
from models.user_model import UserModel
from schemas.order_schema import OrderSchema

order_schema = OrderSchema()


class Order(Resource):
    # making order
    @classmethod
    @jwt_required()
    def post(cls):
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            total_price = 0.0
            items = []
            item_id_quantity = Counter(data['items'])
            for _id, count in item_id_quantity.most_common():
                item = ItemModel.find_item_by_id(_id)
                total_price = total_price + item.price*count
                if not item:
                    return {'msg': 'fail: item not found'}, 404
                items.append(ItemInOrder(item_id=_id, quantity=count))
            order = OrderModel(items=items, user_id=user_id, total_price=total_price)
            order.save_order()
            return order_schema.dump(order), 200
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}


class UpdateOrder(Resource):
    # updating order
    @classmethod
    @jwt_required()
    def put(cls, order_id):
        try:
            order = OrderModel.find_order_by_id(order_id)
            if not order:
                return {'msg': 'fail: order not found'}, 404
            if order.payment_status:
                return {'msg': 'fail: order is completed'}, 400
            total_price = 0.0
            for item in order.items:
                item.delete_item_in_order()
            data = request.get_json()
            items = []
            item_id_quantity = Counter(data['items'])
            for _id, count in item_id_quantity.most_common():
                item = ItemModel.find_item_by_id(_id)
                if not item:
                    return {'msg': 'fail: item not found'}, 404
                total_price = total_price + item.price * count
                items.append(ItemInOrder(item_id=_id, quantity=count))
            order.items = items
            order.total_price = total_price
            order.save_order()
            return order_schema.dump(order), 200
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}


class DeleteOrder(Resource):
    # deleting order
    @classmethod
    @jwt_required()
    def delete(cls, order_id):
        try:
            order = OrderModel.find_order_by_id(order_id)
            if not order:
                return {'msg': 'fail: order not fond'}, 404
            if order.payment_status:
                return {'msg': 'fail: order is completed'}, 400
            for item in order.items:
                item.delete_item_in_order()
            order.delete_order()
            return {'msg': 'success: order deleted'}, 200
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}


class OrderPayment(Resource):
    # completing order payment
    @classmethod
    @jwt_required()
    def post(cls, order_id: int):
        try:
            user_id = get_jwt_identity()
            order = OrderModel.find_order_by_id(order_id)
            print(order)

            user = UserModel.find_user_by_id(user_id)
            if not order:
                return {'msg': 'fail: order not fond'}, 404
            try:
                if order.user_id != user.id:
                    return {'msg': 'fail: order not fond'}, 400
                if user.current_balance < order.total_price:
                    return {'msg': 'fail: not enough balance'}, 400
                if order.payment_status:
                    return {'msg': 'fail: already payed'}, 400
                user.current_balance = user.current_balance - order.total_price
                user.save_user()
                order.payment_status = True
                order.save_order()
                return {'msg': 'success: payment is completed'}, 200
            except Exception as e:
                return {'msg': f'fail: {str(e)}'}, 400
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}


class OrderIsPacked(Resource):
    # update order -- packaging  // admin privilege require
    @classmethod
    @jwt_required()
    def get(cls, order_id: int):
        try:
            claim = get_jwt()
            if not claim['is_admin']:
                return {'msg': 'fail: user is not admin'}, 400
            order = OrderModel.find_order_by_id(order_id)
            if not order:
                return {'msg': 'fail: order not fond'}, 404
            order.is_packed = True
            order.save_order()
            return {'msg': 'success: order is packed'}, 200
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}


class OrderIsShipped(Resource):
    # update order -- shipping  // admin privilege require
    @classmethod
    @jwt_required()
    def get(cls, order_id: int):
        try:
            claim = get_jwt()
            if not claim['is_admin']:
                return {'msg': 'fail: user is not admin'}, 400
            order = OrderModel.find_order_by_id(order_id)
            if not order:
                return {'msg': 'fail: order not fond'}, 404
            order.is_shipped = True
            order.save_order()
            return {'msg': 'success: order is shipped'}, 200
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}


class OrderIsDelivered(Resource):
    # update order -- delivering // admin privilege require
    @classmethod
    @jwt_required()
    def get(cls, order_id: int):
        try:
            claim = get_jwt()
            if not claim['is_admin']:
                return {'msg': 'fail: user is not admin'}, 400
            order = OrderModel.find_order_by_id(order_id)
            if not order:
                return {'msg': 'fail: order not fond'}, 404
            order.is_delivered = True
            order.save_order()
            return {'msg': 'success: order is delivered'}, 200
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}


class UserOrders(Resource):
    # posting user orders
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            user_id = get_jwt_identity()
            return {'orders': order_schema.dump(OrderModel.find_user_orders(user_id=user_id), many=True)}, 200
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}


class OrdersList(Resource):
    # posting users orders  // admin privilege require
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            claim = get_jwt()
            if not claim['is_admin']:
                return {'msg': 'fail: user is not admin'}, 400
            return {'orders': order_schema.dump(OrderModel.find_all(), many=True)}, 200
        except Exception as e:
            return {'msg': f'fail: {str(e)}'}
