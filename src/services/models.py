from django.db import models
from django.utils.text import slugify
from django.core.validators import RegexValidator
from config.utils import generate_unique_slug


class Organisation(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    contact_no = models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\d{10,12}$', 'Enter a valid contact number')],
        db_index=True,
        null=True
    )
    email = models.EmailField(unique=True, db_index=True, null=True)
    slug = models.SlugField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = generate_unique_slug(self, base_slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"
    

class Institution(models.Model):
    org = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='institutions')
    name = models.CharField(max_length=200, db_index=True)
    label = models.CharField(max_length=50, unique=True)
    contact_no = models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\d{10,12}$', 'Enter a valid contact number')],
        db_index=True
    )
    email = models.EmailField(unique=True, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    incharge = models.OneToOneField('core.UserProfile', max_length=200, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = generate_unique_slug(self, base_slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.label}"
    

class Stop(models.Model):
    org = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=200)
    map_link = models.CharField(max_length=255, null=True)
    slug = models.SlugField(unique=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.org}-{self.name}")
            self.slug = generate_unique_slug(self, base_slug)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name}"


class Route(models.Model):
    org = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='routes')
    name = models.CharField(max_length=200)
    stops = models.ManyToManyField(Stop, related_name='stops')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.org}-{self.name}")
            self.slug = generate_unique_slug(self, base_slug)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name}"


class Registration(models.Model):
    org = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='registrations')
    name = models.CharField(max_length=200)
    instructions = models.TextField()
    stops = models.ManyToManyField(Stop, related_name='registration_stops')
    status = models.BooleanField(default=False)
    code = models.CharField(max_length=100, unique=True, null=True)
    slug = models.SlugField(unique=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.org}-{self.name}")
            self.slug = generate_unique_slug(self, base_slug)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.org}{self.name}"
    

class TimeSlot(models.Model):
    org = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='time_slots')
    name = models.CharField(max_length=50)  # Example: "Morning", "Afternoon", "Evening"
    start_time = models.TimeField()  # Example: 08:00 AM
    end_time = models.TimeField()    # Example: 11:00 AM
    slug = models.SlugField(unique=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.org}-{self.name}")
            self.slug = generate_unique_slug(self, base_slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"
    

class Bus(models.Model):
    org = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='buses')
    label = models.CharField(max_length=255)
    bus_no = models.CharField(max_length=15)
    time_slot = models.ForeignKey(TimeSlot, null=True, on_delete=models.SET_NULL, related_name='buses')
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True)
    driver = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.bus_no)
            self.slug = generate_unique_slug(self, base_slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.label} - {self.bus_no}"


class Ticket(models.Model):
    org = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='tickets')
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='tickets')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='tickets')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='tickets')
    recipt_id = models.CharField(max_length=255)
    student_id = models.CharField(max_length=100)
    student_name = models.CharField(max_length=200)
    student_email = models.EmailField()
    contact_no = models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\d{10,12}$', 'Enter a valid contact number')],
    )
    alternative_contact_no = models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\d{10,12}$', 'Enter a valid contact number')],
    )
    pickup_point = models.ForeignKey(Stop, on_delete=models.SET_NULL, null=True, related_name='ticket_pickups')
    drop_point = models.ForeignKey(Stop, on_delete=models.SET_NULL, null=True, related_name='ticket_drops')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.SET_NULL, null=True, related_name='tickets')
    status = models.BooleanField(default=False)  # Indicates if the ticket is confirmed or pending
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.org}-{self.student_name}-{self.bus.label}")
            self.slug = generate_unique_slug(self, base_slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket for {self.student_name} on {self.bus.label} ({self.time_slot.name})"

  