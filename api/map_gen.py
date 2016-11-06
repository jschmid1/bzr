from api.database.models import BaseGood, Map
from api.database.db import db_session

class MapGen(object):

    def __init__(self, season, basegoods=[]):
        self.prc = 100
        self.abs_res = 20000
        self.season_id = season.id
        self.goods = basegoods 

    def generate(self):
        for good in self.goods:
            quota = self.prc / len(self.goods)
            abs_num = (self.abs_res / 100) * quota
            # TODO: distribute the quota randomly and map it to absolute numbers 
            map_o = Map(basegood_id=good.id, season_id=self.season_id, ammount=abs_num)
            db_session.add(map_o)
        db_session.commit()



