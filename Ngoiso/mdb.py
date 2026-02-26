from django.db import models
from datetime import date
from django.core.validators import MinValueValidator


# ===============================
# OUTSTATION
# ===============================

class Outstation(models.Model):
    name = models.CharField(max_length=100)
    parish = models.CharField(
        max_length=50,
        choices=[('NGOISA', 'NGOISA PARISH')]
    )

    def __str__(self):
        return self.name


# ===============================
# JUMUIYA
# ===============================

class Jumuiya(models.Model):
    name = models.CharField(max_length=100)
    outstation = models.ForeignKey(Outstation, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# ===============================
# MEMBER
# ===============================

class Member(models.Model):
    parish = models.CharField(
        max_length=50,
        choices=[('NGOISA', 'NGOISA PARISH')]
    )

    outstation = models.ForeignKey(Outstation, on_delete=models.SET_NULL, null=True)
    jumuiya = models.ForeignKey(Jumuiya, on_delete=models.SET_NULL, null=True)

    group = models.CharField(
        max_length=50,
        choices=[
            ('CMA', 'CMA'),
            ('CWA', 'CWA'),
            ('YOUTH', 'Youth'),
            ('PMC', 'PMC')
        ]
    )

    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.full_name


# ===============================
# MONTHLY ZAKA (Minimum 100 KES)
# ===============================

class Zaka(models.Model):

    MONTH_CHOICES = [
        ('JAN', 'January'), ('FEB', 'February'), ('MAR', 'March'),
        ('APR', 'April'), ('MAY', 'May'), ('JUN', 'June'),
        ('JUL', 'July'), ('AUG', 'August'), ('SEP', 'September'),
        ('OCT', 'October'), ('NOV', 'November'), ('DEC', 'December'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    month = models.CharField(max_length=3, choices=MONTH_CHOICES)
    year = models.PositiveIntegerField(default=date.today().year)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(100)]
    )

    date_recorded = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.member.full_name} - {self.month} {self.year}"


# ===============================
# SPECIAL CONTRIBUTION
# ===============================

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


# ===============================
# MAVUNO (Crops + Animals + Money)
# ===============================

class Mavuno(models.Model):

    PRODUCE_CHOICES = [
        # Crops
        ('MAIZE', 'Maize'),
        ('BEANS', 'Beans'),
        ('WHEAT', 'Wheat'),
        ('MILLET', 'Millet'),

        # Animals
        ('COW', 'Ngombe'),
        ('GOAT', 'Mbuzi'),
        ('SHEEP', 'Kondoo'),
        ('CHICKEN', 'Chicken'),

        # Money
        ('MONEY', 'Money'),

        # Other
        ('OTHER', 'Other'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)

    produce_type = models.CharField(max_length=20, choices=PRODUCE_CHOICES)

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Use quantity for crops/animals or amount if MONEY"
    )

    date_recorded = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.member.full_name} - {self.produce_type}"


# ===============================
# JUMUIYA YEARLY CONTRIBUTION (20,000)
# ===============================

class JumuiyaContribution(models.Model):

    jumuiya = models.ForeignKey(Jumuiya, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(default=date.today().year)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=20000,
        validators=[MinValueValidator(20000)]
    )

    date_recorded = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.jumuiya.name} - {self.year}"


# ===============================
# SADAKA
# ===============================

class Sadaka(models.Model):
    outstation = models.ForeignKey(Outstation, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_recorded = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.outstation.name} - KES {self.amount}"


# ===============================
# 🔥 NEW: PLEDGES MODEL
# ===============================

class Pledge(models.Model):

    PURPOSE_CHOICES = [
        ('BUILDING', 'Church Building'),
        ('PROJECT', 'Special Project'),
        ('DEVELOPMENT', 'Parish Development'),
        ('EVENT', 'Church Event'),
        ('OTHER', 'Other'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)

    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)

    pledged_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1)]
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    date_pledged = models.DateField(default=date.today)

    due_date = models.DateField(null=True, blank=True)

    def balance(self):
        return self.pledged_amount - self.amount_paid

    def __str__(self):
        return f"{self.member.full_name} - {self.purpose}"