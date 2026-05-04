from django.db import models
from django.utils import timezone

class Field(models.Model):
    name = models.CharField("ชื่อสนาม", max_length=100)
    description = models.TextField("รายละเอียด / ขนาดสนาม", blank=True)
    price_per_hour = models.DecimalField("ราคาต่อชั่วโมง (บาท)", max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอชำระเงิน'),
        ('paid', 'ชำระเงินแล้ว'),
        ('cancelled', 'ยกเลิก'),
    ]

    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='bookings', verbose_name="สนาม")
    customer_name = models.CharField("ชื่อลูกค้า/ผู้จอง", max_length=100)
    customer_phone = models.CharField("เบอร์โทรศัพท์", max_length=20)
    booking_date = models.DateField("วันที่จอง")
    start_time = models.TimeField("เวลาเริ่มต้น")
    end_time = models.TimeField("เวลาสิ้นสุด")
    total_price = models.DecimalField("ยอดเงินรวม (บาท)", max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField("สถานะการชำระเงิน", max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.field.name} ({self.booking_date})"

class Tournament(models.Model):
    name = models.CharField("ชื่อรายการแข่งขัน", max_length=150)
    description = models.TextField("รายละเอียดรายการแข่ง", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TournamentGroup(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='groups', verbose_name="รายการแข่งขัน")
    name = models.CharField("ชื่อสาย / กลุ่มการแข่ง", max_length=100, help_text="เช่น สาย A, สาย B")

    def __str__(self):
        return f"{self.tournament.name} - {self.name}"

class Team(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams', verbose_name="รายการแข่งขัน")
    name = models.CharField("ชื่อทีม", max_length=100)
    logo = models.ImageField("โลโก้ทีม / รูปทีม", upload_to='team_logos/', blank=True, null=True)
    main_players = models.TextField("รายชื่อผู้เล่นตัวจริง", blank=True, help_text="ใส่ชื่อสมาชิกคั่นด้วยจุลภาค")
    sub_players = models.TextField("รายชื่อผู้เล่นตัวสำรอง", blank=True, help_text="ใส่ชื่อตัวสำรองคั่นด้วยจุลภาค")
    description = models.TextField("รายละเอียดอื่นๆ", blank=True)

    def __str__(self):
        return f"{self.name} ({self.tournament.name})"

class Match(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'รอแข่งขัน'),
        ('live', 'กำลังแข่งขัน'),
        ('completed', 'แข่งขันเสร็จสิ้น'),
        ('cancelled', 'ยกเลิกการแข่ง'),
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches', verbose_name="รายการแข่งขัน", blank=True, null=True)
    group = models.ForeignKey(TournamentGroup, on_delete=models.CASCADE, related_name='matches', verbose_name="สายการแข่ง", blank=True, null=True)
    title = models.CharField("ชื่องานแข่งขัน/แมตช์", max_length=150)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='matches', verbose_name="สนาม")
    team_a = models.CharField("ทีม A", max_length=100)
    team_b = models.CharField("ทีม B", max_length=100)
    match_date = models.DateField("วันที่แข่งขัน")
    start_time = models.TimeField("เวลาแข่งขัน")
    end_time = models.TimeField("เวลาสิ้นสุดการแข่ง")
    
    # Scores
    score_a = models.IntegerField("คะแนนทีม A", default=0)
    score_b = models.IntegerField("คะแนนทีม B", default=0)
    
    status = models.CharField("สถานะการแข่ง", max_length=20, choices=STATUS_CHOICES, default='scheduled')

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} ({self.match_date})"

class FinancialRecord(models.Model):
    TYPE_CHOICES = [
        ('income', 'รายรับ'),
        ('expense', 'รายจ่าย'),
    ]
    
    date = models.DateField("วันที่", default=timezone.now)
    record_type = models.CharField("ประเภทรายการ", max_length=10, choices=TYPE_CHOICES, default='income')
    category = models.CharField("หมวดหมู่", max_length=100, help_text="เช่น ค่าจองสนาม, ค่าบำรุงรักษา, ค่าไฟฟ้า")
    description = models.TextField("รายละเอียดรายการ", blank=True)
    amount = models.DecimalField("จำนวนเงิน (บาท)", max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"[{self.get_record_type_display()}] {self.category} - {self.amount}"
