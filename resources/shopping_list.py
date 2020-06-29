from flask_restful import Resource

from models.shopping_list import ShoppingListModel
from schemas.shopping_list import ShoppingListSchema
from libs.strings import gettext

shopping_list_schema = ShoppingListSchema()
list_of_shopping_lists = ShoppingListSchema(many=True)


class ShoppingList(Resource):
    @classmethod
    def get(cls, name: str):
        shop_list = ShoppingListModel.find_by_name(name)
        if shop_list:
            return shopping_list_schema.dump(shop_list), 200

        return {"message": gettext("shop_list_not_found")}, 404

    @classmethod
    def post(cls, name: str):
        if ShoppingListModel.find_by_name(name):
            return {"message": gettext("shop_list_name_already_exists").format(name)}, 400

        shop_list = ShoppingListModel(name=name)
        try:
            shop_list.save_to_db()
        except:
            return {"message": gettext("shop_list_error_inserting")}, 500

        return shopping_list_schema.dump(shop_list), 201

    @classmethod
    def delete(cls, name: str):
        shop_list = ShoppingListModel.find_by_name(name)
        if shop_list:
            shop_list.delete_from_db()
            return {"message": gettext("shop_list_deleted")}, 200

        return {"message": gettext("shop_list_not_found")}, 404


class ListOfShoppingLists(Resource):
    @classmethod
    def get(cls):
        return {"shopping lists": list_of_shopping_lists.dump(ShoppingListModel.find_all())}, 200
