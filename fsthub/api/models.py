from django.db import models

class FstProject(models.Model):
    directory = models.CharField(max_length=100,blank=False)
    author = models.CharField(max_length=200,blank=True,default='')
    year = models.IntegerField(blank=True,null=True)

    def __repr__(self):
        return f'<{type(self).__name__}: {self.directory}>'
    
    def __str__(self):
        return self.directory

class FstFile(models.Model):
    file_path = models.CharField(max_length=200)
    file = models.FileField(null=True,blank=True)
    project = models.ForeignKey(FstProject,on_delete=models.CASCADE)
    
    def __repr__(self):
        return f'<{type(self).__name__} {self.file_path}>'
