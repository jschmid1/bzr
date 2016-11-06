import sure
import os
import json
from api.server import app
from api.database.models import BaseGood, User, Producable
from api.database.db import db_session, db_path
from api.seed import seed_users, seed_basegoods, seed_producables, create_links, fill_inventory, adding_seasons, adding_map


def before_feature(context, feature):
    context.client = app.test_client()

