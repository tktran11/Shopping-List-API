from ma import ma
from models.shopping_list import ShoppingListModel
from schemas.item import ItemSchema


class ShoppingListSchema(ma.SQLAlchemyAutoSchema):
    item = ma.Nested(ItemSchema, many=True)

    class Meta:
        model = ShoppingListModel
        dump_only = {
            "id",
        }
        include_fk = True  # include foreign keys

        load_instance = True