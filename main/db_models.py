from django.db import models

class room(models.Model):
    uuid = models.CharField(max_length=255, primary_key=True)
    hash = models.TextField()

    class Meta:
        db_table = 'sessions' 

    def __str__(self):
        return f"{self.uuid}: {self.hash}"
    
class analysis_data(models.Model):
    uuid = models.CharField(max_length=255, primary_key=True)
    p1_factors = models.TextField()
    p1_weights = models.TextField()
    p1_extra_factors = models.TextField()
    p2_inputs = models.TextField()
    p3_inputs = models.TextField()
    p4_inputs = models.TextField()
    p5_inputs = models.TextField()

    class Meta:
        db_table = 'analysis_data'