import datetime
import time
from api.database.db import init_db, db_session
from api.logger.logger import log
from api.database.models import User, Producable, Inventory, BuildQueue


init_db()
# While server process is running?
while 1:
    queue = BuildQueue.query.all()
    for itm in queue:
        now = datetime.datetime.now()
        if itm.time_done > now:
            inv = Inventory(basegood_id=None,
                            producable_id=itm.producable_id,
                            user_id=itm.user_id)
            prod_name = Producable.query.get(itm.producable_id).name
            user_name = User.query.get(itm.user_id).name
            log.info("{} finished building.".format(prod_name))
            log.info("Adding to {}'s inventory".format(user_name))
            db_session.delete(itm)
            log.info("Deleting #{} from buildqueue".format(itm.id))
            db_session.add(inv)
            db_session.commit()
    time.sleep(1)
