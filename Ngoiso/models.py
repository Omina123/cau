from django.db import models

from datetime import date
class Outstation(models.Model):
    name = models.CharField(max_length=100)
    parish = models.CharField(max_length=50, choices=[('NGOISA', 'NGOISa Parish')])

    def __str__(self):
        return self.name

class Jumuiya(models.Model):
    name = models.CharField(max_length=100)
    outstation = models.ForeignKey(Outstation, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
class Member(models.Model):
    parish = models.CharField(max_length=50, choices=[('NGOISA', 'NGOISA Parish')])
    outstation = models.ForeignKey(Outstation, on_delete=models.SET_NULL, null=True)
    jumuiya = models.ForeignKey(Jumuiya, on_delete=models.SET_NULL, null=True)
    group = models.CharField(max_length=50, choices=[('CMA', 'CMA'), ('CWA', 'CWA'), ('YOUTH', 'Youth'), ('PMC', 'PMC')])
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    def __str__(self):
        return self.full_name
    
class Zaka(models.Model):

    YEAR_CHOICES = [
        ('A', 'Year A'),
        ('B', 'Year B'),
        ('C', 'Year C'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    year = models.CharField(max_length=1, choices=YEAR_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_recorded = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.member.full_name} - Zaka {self.year}"
class SpecialContribution(models.Model):

    CONTRIBUTION_TYPE = [
        ('NOEL', 'Noel'),
        ('CHRISTMAS', 'Christmas'),
        ('PASAKA', 'Pasaka'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    contribution_type = models.CharField(max_length=20, choices=CONTRIBUTION_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_recorded = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.member.full_name} - {self.contribution_type}"  
class Mavuno(models.Model):

    PRODUCE_CHOICES = [
        ('MAIZE', 'Maize'),
        ('BEANS', 'Beans'),
        ('WHEAT', 'Wheat'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    produce_type = models.CharField(max_length=20, choices=PRODUCE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date_recorded = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.member.full_name} - {self.produce_type}"                                   


class Sadaka(models.Model):
    outstation = models.ForeignKey('Outstation', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_recorded = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.outstation.name} - KES {self.amount} on {self.date_recorded}"