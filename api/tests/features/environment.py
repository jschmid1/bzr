import os
from server import app
from api.database.db import db_session, db_path
from api.database.models import BaseGood, Producable
from seed import seed_users, seed_basegoods, seed_producables, create_links, fill_inventory, adding_seasons, adding_map, add_basegood_to_inv


BEHAVE_DEBUG_ON_ERROR = False

if 'development' in db_path or 'production' in db_path:
    raise ContextError("USE DB_ENV=testing;behave...")


def before_scenario(context, scenario):
    seed_basegoods()
    seed_producables()
    context.old_price = BaseGood.query.get(1).price
    context.old_pr_price = Producable.query.get(1).price

def setup_debug_on_error(userdata):
    global BEHAVE_DEBUG_ON_ERROR
    BEHAVE_DEBUG_ON_ERROR = userdata.getbool("BEHAVE_DEBUG_ON_ERROR")


def before_all(context):
    context.client = app.test_client()
    setup_debug_on_error(context.config.userdata)


def after_step(context, step):
    if BEHAVE_DEBUG_ON_ERROR and step.status == "failed":
        import ipdb;ipdb.post_mortem(step.exc_traceback)


def after_all(context):
    os.remove(db_path)
