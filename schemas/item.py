from ma import ma
from models.item import ItemModel
from models.shopping_list import ShoppingListModel


class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItemModel
        load_only = {
            "shopping_lists",
        }
        dump_only = {
            "id",
        }
        include_fk = True  # include foreign keys

        load_instance = True
