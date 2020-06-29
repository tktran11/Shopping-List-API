from typing import List

from db import db


class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(80), nullable=False, unique=True
    )  # nullable forces non-null value
    price = db.Column(db.Float(precision=2), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey("shopping_lists.id"), nullable=False)
    shopping_list = db.relationship("ShoppingListModel")

    @classmethod
    def find_by_name(cls, name: str) -> "ItemModel":
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_priority(cls, priority: int) -> List["ItemModel"]:
        return cls.query.filter_by(priority=priority).all()

    @classmethod
    def find_all(cls) -> List["ItemModel"]:
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
