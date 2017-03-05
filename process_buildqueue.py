import datetime
import time
from api.database.db import init_db, db_session
from api.logger.logger import log
from api.database.models import User, Producable, Inventory, BuildQueue


def process_buildqueue():
    while(1):
        prs = Producable.query.all()
        for pr in prs:
            log.debug("Checking buildqueue for {}".format(pr.name))
            queue = BuildQueue.query.filter(BuildQueue.active == True).filter(BuildQueue.producable_id == pr.id)
            itm = queue.first()
            if not itm:
                # add a 'done' callback that compares time_done and datetime.now
                log.info("Getting BuildQueue items with criteria: Not active, Not Processed")
                all_possible_new = BuildQueue.query.filter(BuildQueue.active == False).filter(BuildQueue.processed == False).filter(BuildQueue.producable_id == pr.id)
                if len(all_possible_new.filter(BuildQueue.time_done > datetime.datetime.now()).all()) > 0:
                    log.info("Found items that have not been processed although they are done.")
                    log.info("Do something")
                apn = all_possible_new.all()
                if len(apn) >= 1:
                    apn[0].active = True
                    db_session.commit()
                    log.info("Setting item {} to active".format(apn[0].id))
                else:
                    log.info("No items in buildqueue for Producable {}".format(pr.name))
            if itm:
                log.info("#{} has an active flag".format(itm.id))
                now = datetime.datetime.now()
                if itm.time_done <= now:
                    inv = Inventory(basegood_id=None,
                                    producable_id=itm.producable_id,
                                    user_id=itm.user_id)
                    prod_name = Producable.query.get(itm.producable_id).name
                    user_name = User.query.get(itm.user_id).name
                    log.info("{} finished building.".format(prod_name))
                    log.info("Adding {} to {}'s inventory".format(prod_name, user_name))
                    itm.active = False
                    itm.processed = True
                    log.info("Marking #{} as processed and Non-active".format(itm.id))
                    db_session.add(inv)
                    db_session.commit()
                else:
                    d1_ts = time.mktime(now.timetuple())
                    d2_ts = time.mktime(itm.time_done.timetuple())
                    minutes_left = int(d2_ts-d1_ts) / 60
                    log.info("#{} is not ready yet. Takes {} minutes more.".format(itm.id, minutes_left))
            time.sleep(3)
process_buildqueue()
