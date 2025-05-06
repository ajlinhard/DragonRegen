import os
import json
import yaml

class ConfigSys():

    def __init__(self, s_path_config=None):
        self.s_path_config = s_path_config
        self.d_config = {}

    def get_config(self, key:str, default=None):
        if self.d_config is None:
            if self.s_path_config.endswith('.json'):
                self.d_config = json.loads(self.s_path_config)
            elif self.s_path_config.endswith('.yml'):
                self.d_config = yaml.load(self.s_path_config)
        
        return self.d_config.get(key, default)
    
    def data_path(self):
        project_dir = os.getcwd()
        data_project_root = os.path.abspath(os.path.join(project_dir, "..", "..","gitData"))
        return self.get_config('ROOT_DATA_PATH', data_project_root)
            
