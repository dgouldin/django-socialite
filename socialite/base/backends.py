class BaseSocialObject(object):
    property_list = [
        'first_name',
        'last_name',
    ]
    properties = {}
    
    def __getattr__(self, attr):
        if attr not in self.property_list:
            raise AttributeError("%s is not a valid attribute" % attr)
        return self.properties.get(attr)
        # TODO: this is unpythonic, change this all

class BaseSocialBackend(object):
    def get_unique_id(self):
        raise NotImplementedError()

    def find_friends(self, attr):
        