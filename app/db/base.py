from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.modules.users import model as users_model  # noqa: F401
from app.modules.tables import model as tables_model  # noqa: F401
from app.modules.products import model as products_model  # noqa: F401
from app.modules.games import model as games_model  # noqa: F401
from app.modules.reservations import model as reservations_model  # noqa: F401
from app.modules.orders import model as orders_model  # noqa: F401
from app.modules.game_rentals import model as game_rentals_model  # noqa: F401
from app.modules.payments import model as payments_model  # noqa: F401
from app.modules.security.passwords import model as passwords_model  # noqa: F401
from app.logs.activity import model as activity_logs_model  # noqa: F401