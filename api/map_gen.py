from api.database.models import Map
from api.database.db import db_session


class MapGen(object):
    """
    Generate a Map
    """

    def __init__(self, season, items=[]):
        # Move to config
        self.prc = 100
        self.abs_res = 20000
        self.season_id = season.id
        self.items = items 

    def generate(self):
        for item in self.items:
            quota = self.prc / len(self.items)
            abs_num = (self.abs_res / 100) * quota
            # TODO: distribute the quota randomly and map it to absolute number
            map_o = Map(item_id=item.id,
                        season_id=self.season_id,
                        initial_ammount=abs_num,
                        ammount=abs_num)
            db_session.add(map_o)
        db_session.commit()
