import json
class Utils:
    def __init__(self, settings = False, options = False, card = False):
        self.options = options
        self.settings = settings
        self.card = card

    def hex2rgb(hex):
        return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

    def getColor(self,name):
        for color in self.settings['sources']['colors']:
            if (color['name'] == name):return self.hex2rgb(color['value'])

    def getColorName(self,i):
        self.self.settings['sources']['colors'][i]['name']

    def getValue(self,dict, path):
        keys = path.split('.')
        val = dict
        for key in keys:
            if key in val:
                val = val[key]
            else: return None
        return val
    
    def getSettingValue(self,path):
        if (path == 'sources.card'):
            return self.card.images
        else:
            return self.getValue(self.settings,path)

    def getOptionValue(self,path):
        return self.getValue(self.options,path)

    def json_pretty_print(json_data, indent=4):

        def iter_json(obj, level=1):
            if isinstance(obj, dict):
                indent_str = ' ' * (level * indent)
                pairs = []
                for key, value in obj.items():
                    pairs.append(f'"{key}": {iter_json(value, level+1)}')
                return '{{\n{}\n{}}}'.format(',\n'.join(pairs), indent_str)
            elif isinstance(obj, list):
                indent_str = ' ' * (level * indent)
                items = []
                for value in obj:
                    items.append(iter_json(value, level+1))
                return '[\n{}\n{}]'.format(',\n'.join(items), indent_str)
            else:
                return json.dumps(obj)
        
        return iter_json(json_data, level=1)
