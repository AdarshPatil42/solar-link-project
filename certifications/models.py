from django.db import models
from django.utils.text import slugify


class StandardCategory(models.TextChoices):
    QUALITY = 'QUALITY', 'Quality Standards'
    ELECTRICAL = 'ELECTRICAL', 'Electrical Safety'
    TESTING = 'TESTING', 'Product Testing'
    ENVIRONMENTAL = 'ENVIRONMENTAL', 'Environmental Compliance'
    INTERNATIONAL = 'INTERNATIONAL', 'International Standards'


class ComplianceStandard(models.Model):
    name = models.CharField(max_length=150, unique=True, help_text='e.g., IEC 61215, UL 1741, CE EMC/LVD, ISO 9001')
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    category = models.CharField(max_length=30, choices=StandardCategory.choices, default=StandardCategory.INTERNATIONAL)
    issuing_body = models.CharField(max_length=150, help_text='e.g., TÜV Rheinland, UL Solutions, Intertek, ISO')
    description = models.TextField(help_text='Detailed scope and testing requirements governed by this standard.')
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Compliance Standard'
        verbose_name_plural = 'Compliance Standards'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Certification(models.Model):
    certificate_number = models.CharField(max_length=100, unique=True, help_text='Official Certificate or Registration ID')
    title = models.CharField(max_length=200, help_text='Official Certificate Title')
    standard = models.ForeignKey(ComplianceStandard, on_delete=models.CASCADE, related_name='certifications')
    issuing_organization = models.CharField(max_length=150, help_text='Notified Testing Body (e.g., TÜV Rheinland Germany)')
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    products = models.ManyToManyField('catalog.Product', related_name='certifications', blank=True)
    document_file = models.FileField(upload_to='certifications/certificates/', blank=True, null=True)
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date']
        verbose_name = 'Product Certification'
        verbose_name_plural = 'Product Certifications'

    def __str__(self):
        return f"{self.certificate_number} - {self.standard.name}"


class LabReport(models.Model):
    class ReportStatus(models.TextChoices):
        VERIFIED = 'VERIFIED', 'Verified / Passed'
        EXCEEDS = 'EXCEEDS', 'Exceeds Standard'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'

    report_number = models.CharField(max_length=100, unique=True)
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='lab_reports')
    testing_laboratory = models.CharField(max_length=150, help_text='e.g., TÜV Rheinland Solar Lab, PVEL, UL Test Lab')
    test_date = models.DateField()
    test_type = models.CharField(max_length=150, help_text='e.g., PID Resistance Test, Hail 25mm Impact, Salt Mist Corrosion Class 6')
    result = models.CharField(max_length=200, help_text='e.g., Passed - Power degradation < 1.1%')
    status = models.CharField(max_length=30, choices=ReportStatus.choices, default=ReportStatus.VERIFIED)
    document_file = models.FileField(upload_to='certifications/reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-test_date']
        verbose_name = 'Laboratory Test Report'
        verbose_name_plural = 'Laboratory Test Reports'

    def __str__(self):
        return f"Report {self.report_number}: {self.test_type} ({self.product.name})"


class Warranty(models.Model):
    product = models.OneToOneField('catalog.Product', on_delete=models.CASCADE, related_name='warranty')
    product_warranty_years = models.PositiveIntegerField(default=12, help_text='Material & Workmanship Warranty in Years')
    performance_warranty_years = models.PositiveIntegerField(default=25, help_text='Linear Power Output Warranty in Years')
    coverage_details = models.TextField(help_text='Detailed warranty provisions, replacement, or repair guarantees.')
    exclusions = models.TextField(blank=True, default='', help_text='Acts of nature, improper installation, unapproved alterations.')
    operating_conditions = models.TextField(blank=True, default='', help_text='Recommended operating temperature, humidity, and maintenance.')
    document_file = models.FileField(upload_to='certifications/warranties/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Warranty Term'
        verbose_name_plural = 'Warranty Terms'

    def __str__(self):
        return f"Warranty: {self.product.name} ({self.product_warranty_years}y product / {self.performance_warranty_years}y perf)"
