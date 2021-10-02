from typing import List

from db import db


class DeliveryModel(db.Model):
    __tablename__ = "deliveries"

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship("UserModel")
    orders = db.relationship("OrderModel")

    @classmethod
    def find_all(cls) -> List["DeliveryModel"]:
        return cls.query.all()

    @classmethod
    def find_delivery_by_id(cls, _id: int) -> "DeliveryModel":
        return cls.query.filter_by(id=_id).first()

    def save_delivery(self):
        db.session.add(self)
        db.session.commit()

    def delete_delivery(self):
        db.session.delete(self)
        db.session.commit()
