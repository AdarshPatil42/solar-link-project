from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
import random


class EnquiryStatus(models.TextChoices):
    REQUESTED = 'REQUESTED', 'Enquiry Submitted'
    ASSIGNED = 'ASSIGNED', 'Sales Executive Assigned'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Requirements Reviewed'
    QUOTATION_PREPARED = 'QUOTATION_PREPARED', 'Quotation Prepared'
    QUOTATION_SENT = 'QUOTATION_SENT', 'Quotation Sent'
    NEGOTIATION = 'NEGOTIATION', 'Buyer Review & Negotiation'
    APPROVED = 'APPROVED', 'Order Confirmed (Won)'
    REJECTED = 'REJECTED', 'Rejected / Closed'
    CLOSED = 'CLOSED', 'Archived / Closed'


class ProjectType(models.TextChoices):
    COMMERCIAL = 'COMMERCIAL', 'Commercial & Industrial (C&I Rooftop)'
    UTILITY = 'UTILITY', 'Utility Scale Solar Farm (Ground Mount)'
    RESIDENTIAL = 'RESIDENTIAL', 'Residential / Housing Community'
    OFF_GRID = 'OFF_GRID', 'Off-Grid & Hybrid Microgrid'
    AGRICULTURE = 'AGRICULTURE', 'Agricultural Solar Pumping & Irrigation'
    DISTRIBUTION = 'DISTRIBUTION', 'Wholesale Resale / Regional Distribution'


class Enquiry(models.Model):
    enquiry_number = models.CharField(max_length=30, unique=True, editable=False)
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='enquiries')
    
    # Buyer Contact Details
    full_name = models.CharField(max_length=120)
    company_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    country = models.CharField(max_length=100)
    
    # Project Scope
    project_name = models.CharField(max_length=200)
    project_type = models.CharField(max_length=30, choices=ProjectType.choices, default=ProjectType.COMMERCIAL)
    required_capacity = models.CharField(max_length=100, help_text='e.g., 550 kWp, 5 MW, 10 Containers')
    project_location = models.CharField(max_length=200, help_text='City, State/Province, Country')
    expected_delivery_date = models.DateField(null=True, blank=True)
    shipping_destination = models.CharField(max_length=200, help_text='Destination Seaport or Final Delivery City')
    preferred_incoterm = models.CharField(max_length=20, default='CIF', help_text='e.g., FOB, CIF, DDP, EXW')
    
    message = models.TextField(help_text='Detailed specifications, technical constraints, or bill of quantities.')
    attachment = models.FileField(upload_to='enquiries/attachments/', blank=True, null=True, help_text='Tender doc, single-line diagram, or BoQ (PDF/Excel)')
    
    status = models.CharField(max_length=30, choices=EnquiryStatus.choices, default=EnquiryStatus.REQUESTED)
    assigned_sales_rep = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_enquiries')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project Enquiry'
        verbose_name_plural = 'Project Enquiries'

    def save(self, *args, **kwargs):
        if not self.enquiry_number:
            year = datetime.now().year
            # Generate unique sequence format: ENQ-2026-XXXXX
            random_digits = random.randint(10000, 99999)
            candidate = f"ENQ-{year}-{random_digits}"
            while Enquiry.objects.filter(enquiry_number=candidate).exists():
                random_digits = random.randint(10000, 99999)
                candidate = f"ENQ-{year}-{random_digits}"
            self.enquiry_number = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enquiry_number} — {self.project_name} ({self.company_name})"

    @property
    def timeline_step(self):
        """
        Returns index (1-7) for graphical progress timeline:
        1: Enquiry Submitted
        2: Sales Executive Assigned
        3: Requirements Reviewed
        4: Quotation Prepared
        5: Quotation Sent
        6: Buyer Response / Negotiation
        7: Closed / Won
        """
        status_map = {
            EnquiryStatus.REQUESTED: 1,
            EnquiryStatus.ASSIGNED: 2,
            EnquiryStatus.UNDER_REVIEW: 3,
            EnquiryStatus.QUOTATION_PREPARED: 4,
            EnquiryStatus.QUOTATION_SENT: 5,
            EnquiryStatus.NEGOTIATION: 6,
            EnquiryStatus.APPROVED: 7,
            EnquiryStatus.REJECTED: 7,
            EnquiryStatus.CLOSED: 7,
        }
        return status_map.get(self.status, 1)

    @property
    def application_type(self):
        return self.project_type

    @property
    def get_application_type_display(self):
        return self.get_project_type_display()

    @property
    def estimated_capacity(self):
        return self.required_capacity

    @property
    def target_delivery_date(self):
        return self.expected_delivery_date

    @property
    def description(self):
        return self.message

    @property
    def phone_number(self):
        return self.phone



class EnquiryItem(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='enquiry_lines')
    quantity = models.PositiveIntegerField(default=1)
    target_price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Optional target unit price in USD')
    notes = models.CharField(max_length=250, blank=True, default='')

    class Meta:
        verbose_name = 'Enquiry Item'
        verbose_name_plural = 'Enquiry Items'

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


class EnquiryStatusHistory(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name='status_history')
    from_status = models.CharField(max_length=30)
    to_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def created_at(self):
        return self.timestamp

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Enquiry Status Log'
        verbose_name_plural = 'Enquiry Status Logs'

    def __str__(self):
        return f"{self.enquiry.enquiry_number}: {self.from_status} -> {self.to_status} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"


class Quotation(models.Model):
    class QuotationStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SENT = 'SENT', 'Sent to Buyer'
        ACCEPTED = 'ACCEPTED', 'Accepted by Buyer'
        NEGOTIATING = 'NEGOTIATING', 'Buyer Requested Revision'
        DECLINED = 'DECLINED', 'Declined by Buyer'
        EXPIRED = 'EXPIRED', 'Expired'

    quote_number = models.CharField(max_length=30, unique=True, editable=False)
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name='quotations')
    sales_rep = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quotations')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='USD')
    incoterm = models.CharField(max_length=20, default='CIF')
    payment_terms = models.CharField(max_length=150, default='30% T/T Advance, 70% against Bill of Lading')
    valid_until = models.DateField()
    status = models.CharField(max_length=30, choices=QuotationStatus.choices, default=QuotationStatus.DRAFT)
    sales_rep_notes = models.TextField(blank=True, default='')
    buyer_feedback = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Commercial Quotation'
        verbose_name_plural = 'Commercial Quotations'

    def save(self, *args, **kwargs):
        if not self.quote_number:
            year = datetime.now().year
            rand = random.randint(10000, 99999)
            self.quote_number = f"QT-{year}-{rand}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quote_number} for {self.enquiry.enquiry_number} (${self.total_amount})"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    specifications_summary = models.CharField(max_length=250, blank=True, default='')

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.subtotal

    def __str__(self):
        return f"{self.quantity}x {self.product.name} @ ${self.unit_price}"
