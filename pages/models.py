from django.db import models


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True, default='')
    company = models.CharField(max_length=150, blank=True, default='')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.full_name} — {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"


class FAQCategory(models.TextChoices):
    GENERAL = 'GENERAL', 'General & Operations'
    QUOTATIONS = 'QUOTATIONS', 'Quotations & Bulk RFQ'
    SHIPPING = 'SHIPPING', 'Shipping, Incoterms & Customs'
    TECHNICAL = 'TECHNICAL', 'Technical & Certifications'
    WARRANTY = 'WARRANTY', 'Warranties & Support'


class FAQ(models.Model):
    category = models.CharField(max_length=30, choices=FAQCategory.choices, default=FAQCategory.GENERAL)
    question = models.CharField(max_length=250)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'category', 'question']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question


class TeamDepartment(models.TextChoices):
    MANAGEMENT = 'MANAGEMENT', 'Executive Leadership'
    SALES = 'SALES', 'International Sales & RFQ'
    EXPORT = 'EXPORT', 'Export Logistics & Trade'
    TECHNICAL = 'TECHNICAL', 'Solar Technical & Engineering'
    SUPPORT = 'SUPPORT', 'Client Support & Quality Desk'


class TeamMember(models.Model):
    name = models.CharField(max_length=120)
    designation = models.CharField(max_length=150)
    department = models.CharField(max_length=30, choices=TeamDepartment.choices, default=TeamDepartment.SALES)
    photo = models.ImageField(upload_to='profiles/team/', blank=True, null=True)
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=40, blank=True, default='')
    bio = models.TextField()
    social_linkedin = models.URLField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'department', 'name']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

    def __str__(self):
        return f"{self.name} — {self.designation} ({self.get_department_display()})"
