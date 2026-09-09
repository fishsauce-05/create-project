from commands import maven, gradle, nestjs, nextjs

class Registry:
    def __init__(self):
        self.fields = {
            "Maven": maven.Maven,
            "Gradle": gradle.Gradle,
            "NestJS": nestjs.Nest,
            "NextJS": nextjs.Nextjs
        }
    
    def get_project_types(self):
        return list(self.fields.keys())
    
    def create(self, project_type):
        if project_type in self.fields:
            return self.fields[project_type]()
        else:
            raise ValueError("Invalid project type")
        
    