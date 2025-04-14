
class Utm(object):
    def __init__(self):
        self.utm_source = None
        self.utm_medium = None
        self.utm_campaign = {"marketid": None, "product": None, "channel": None, "budgettype": None, "funnel": None,
                             "emailsource": None}
        self.utm_content = {}

        # self.utm_content = {"date": None, "templateid": None, "pod": None, "emailproduct": None,"cat": None, "subcat": None,
        #                     "ISC": None, "contentblockname": None}
