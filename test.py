import socceraction
from socceraction.data.statsbomb import StatsBombLoader
from socceraction.xthreat import ExpectedThreat

data = StatsBombLoader(getter="local", root="")    
xt_model = ExpectedThreat(l=16, w=12, eps=1e-05)
xt_model.fit(data.events())