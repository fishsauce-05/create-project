from create.cmd import Maven, Gradle, Nest, Nextjs
from create.template import Android

class Registry:
    def __init__(self):
        self.fields = {
            "Maven": Maven,
            "Gradle": Gradle,
            "NestJS": Nest,
            "NextJS": Nextjs,
            "Android": Android
        }
    
    def get_project_types(self):
        return list(self.fields.keys())
    
    def create(self, project_type):
        if project_type in self.fields:
            return self.fields[project_type]()
        else:
            raise ValueError("Invalid project type")
        
    