from django.db import models


class IncotermCode(models.TextChoices):
    EXW = 'EXW', 'EXW — Ex Works'
    FOB = 'FOB', 'FOB — Free On Board'
    CFR = 'CFR', 'CFR — Cost and Freight'
    CIF = 'CIF', 'CIF — Cost, Insurance and Freight'
    DAP = 'DAP', 'DAP — Delivered At Place'
    DDP = 'DDP', 'DDP — Delivered Duty Paid'


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=5, unique=True, help_text='ISO 2-letter Country Code (e.g. AE, SA, DE, AU)')
    region = models.CharField(max_length=80, help_text='e.g., Middle East & GCC, Europe, Africa, Asia-Pacific')
    flag_emoji = models.CharField(max_length=10, blank=True, default='🌐')
    primary_ports = models.CharField(max_length=200, blank=True, default='', help_text='Major container ports (e.g., Jebel Ali, Dammam, Hamburg)')
    customs_notes = models.TextField(blank=True, default='', help_text='Special customs clearance certificates or importer requirements.')
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Export Country'
        verbose_name_plural = 'Export Countries'

    def __str__(self):
        return f"{self.flag_emoji} {self.name} ({self.code})"


class ShippingTerm(models.Model):
    incoterm = models.CharField(max_length=10, choices=IncotermCode.choices, unique=True)
    title = models.CharField(max_length=150, help_text='Descriptive title of the trade term')
    buyer_responsibility = models.TextField(help_text='Clear breakdown of obligations, costs, and clearance borne by the buyer.')
    seller_responsibility = models.TextField(help_text='Clear breakdown of exporter obligations (freight, packaging, port handling).')
    risk_transfer_point = models.CharField(max_length=200, help_text='Exact physical juncture where risk of damage transfers to buyer.')
    standard_ports_of_origin = models.CharField(max_length=200, default='Shanghai, Ningbo, Hamburg, Rotterdam, Jebel Ali')
    estimated_transit_days = models.CharField(max_length=100, default='15 - 30 calendar days (Ocean Container)')
    minimum_order = models.CharField(max_length=150, default='1x 20ft Container (approx. 280-320 kW) or 20 Inverter Units')
    packaging_standard = models.TextField(default='Export heavy-duty reinforced wooden crates, moisture barrier vacuum film, corner edge protectors, tilt sensors.')
    is_recommended = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'incoterm']
        verbose_name = 'Shipping Term & Incoterm'
        verbose_name_plural = 'Shipping Terms & Incoterms'

    def __str__(self):
        return f"{self.incoterm} — {self.title}"


class ExportDocument(models.Model):
    name = models.CharField(max_length=150, unique=True, help_text='e.g., Commercial Invoice, Packing List, Certificate of Origin (Form A)')
    code = models.CharField(max_length=50, blank=True, default='')
    purpose = models.TextField(help_text='Purpose of the document in customs clearance and international trade compliance.')
    issuing_party = models.CharField(max_length=150, help_text='e.g., Exporter, Chamber of Commerce, Shipping Carrier, Notified Lab')
    is_mandatory = models.BooleanField(default=True)
    sample_template = models.FileField(upload_to='exports/templates/', blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Export Document'
        verbose_name_plural = 'Export Documents'

    def __str__(self):
        return f"{self.name} ({'Mandatory' if self.is_mandatory else 'Optional'})"
