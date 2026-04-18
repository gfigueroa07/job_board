from django.db import models

# This is just a super simple model with not connection to other models. In SQL its basically a standalone table with no foreign keys
class XaropItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name