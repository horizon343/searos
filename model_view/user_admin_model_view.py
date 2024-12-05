from db.models.user_model import User
from sqladmin import ModelView


class UserAdmin(ModelView, model=User):
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = False

    name = "users"
    name_plural = "users"
    icon = "fa-solid fa-user"
    category = "accounts"

    column_list = [User.id, User.name]
    column_searchable_list = [User.name]
    column_sortable_list = [User.id, User.name]

    column_details_list = [User.id, User.name]

    page_size = 50
    page_size_options = [25, 50, 100, 200, 500, 1000]
