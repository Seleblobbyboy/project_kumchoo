from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Field, Booking, Match, FinancialRecord
from django.db.models import Sum
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Authentication Views

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
            return redirect('login')
            
    return render(request, 'stadium/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, "รหัสผ่านและยืนยันรหัสผ่านไม่ตรงกัน")
            return redirect('register')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "มีชื่อผู้ใช้นี้ในระบบแล้ว")
            return redirect('register')
            
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ")
        return redirect('login')
        
    return render(request, 'stadium/register.html')

def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        users = User.objects.filter(email=email)
        if users.exists():
            # Set temporary password
            user = users.first()
            new_pass = "Reset12345!"
            user.set_password(new_pass)
            user.save()
            messages.success(request, f"รีเซ็ตรหัสผ่านสำเร็จ รหัสผ่านใหม่ของคุณคือ: {new_pass}")
            return redirect('login')
        else:
            messages.error(request, "ไม่พบอีเมลนี้ในระบบ")
            return redirect('forgot_password')
            
    return render(request, 'stadium/forgot_password.html')

def logout_view(request):
    logout(request)
    return redirect('login')


# Main Application Views (Login Required)

@login_required
def dashboard(request):
    today = timezone.localdate()
    total_fields = Field.objects.count()
    today_bookings = Booking.objects.filter(booking_date=today)
    today_matches = Match.objects.filter(match_date=today)
    
    start_of_month = today.replace(day=1)
    booking_revenue = Booking.objects.filter(booking_date__gte=start_of_month, payment_status='paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    income_records = FinancialRecord.objects.filter(date__gte=start_of_month, record_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense_records = FinancialRecord.objects.filter(date__gte=start_of_month, record_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_income = booking_revenue + income_records
    net_profit = total_income - expense_records

    context = {
        'total_fields': total_fields,
        'today_bookings': today_bookings,
        'today_matches': today_matches,
        'booking_revenue': booking_revenue,
        'income_records': income_records,
        'expense_records': expense_records,
        'total_income': total_income,
        'net_profit': net_profit,
        'today': today,
    }
    return render(request, 'stadium/dashboard.html', context)

@login_required
def fields_schedule(request):
    fields = Field.objects.all()
    selected_field_id = request.GET.get('field_id')
    selected_date_str = request.GET.get('date', timezone.localdate().strftime('%Y-%m-%d'))
    
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = timezone.localdate()

    selected_field = None
    bookings = []
    matches = []

    if selected_field_id:
        try:
            selected_field = Field.objects.get(id=selected_field_id)
            bookings = Booking.objects.filter(field=selected_field, booking_date=selected_date).order_by('start_time')
            matches = Match.objects.filter(field=selected_field, match_date=selected_date).order_by('start_time')
        except Field.DoesNotExist:
            pass
    elif fields.exists():
        selected_field = fields.first()
        bookings = Booking.objects.filter(field=selected_field, booking_date=selected_date).order_by('start_time')
        matches = Match.objects.filter(field=selected_field, match_date=selected_date).order_by('start_time')

    context = {
        'fields': fields,
        'selected_field': selected_field,
        'selected_date': selected_date_str,
        'bookings': bookings,
        'matches': matches,
    }
    return render(request, 'stadium/fields_schedule.html', context)

@login_required
def bookings_list(request):
    if request.method == 'POST':
        field_id = request.POST.get('field_id')
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        booking_date = request.POST.get('booking_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        total_price = request.POST.get('total_price', 0)
        payment_status = request.POST.get('payment_status', 'pending')

        if field_id and customer_name and booking_date and start_time and end_time:
            field = Field.objects.get(id=field_id)
            booking = Booking.objects.create(
                field=field,
                customer_name=customer_name,
                customer_phone=customer_phone,
                booking_date=booking_date,
                start_time=start_time,
                end_time=end_time,
                total_price=total_price,
                payment_status=payment_status
            )
            if payment_status == 'paid':
                FinancialRecord.objects.create(
                    date=booking_date,
                    record_type='income',
                    category='ค่าจองสนาม',
                    description=f'จองสนาม {field.name} โดย {customer_name}',
                    amount=total_price
                )
            return redirect('bookings_list')

    status = request.GET.get('status')
    bookings = Booking.objects.all().order_by('-booking_date', '-start_time')
    if status:
        bookings = bookings.filter(payment_status=status)

    fields = Field.objects.all()
    context = {
        'bookings': bookings,
        'fields': fields,
        'status_filter': status,
    }
    return render(request, 'stadium/bookings_list.html', context)

@login_required
def update_booking_status(request, booking_id):
    if request.method == 'POST':
        status = request.POST.get('payment_status')
        try:
            booking = Booking.objects.get(id=booking_id)
            if status == 'paid' and booking.payment_status != 'paid':
                FinancialRecord.objects.create(
                    date=booking.booking_date,
                    record_type='income',
                    category='ค่าจองสนาม',
                    description=f'จองสนาม {booking.field.name} โดย {booking.customer_name}',
                    amount=booking.total_price
                )
            booking.payment_status = status
            booking.save()
        except Booking.DoesNotExist:
            pass
    return redirect('bookings_list')

@login_required
def matches_list(request):
    if request.method == 'POST':
        match_id = request.POST.get('match_id')
        title = request.POST.get('title')
        field_id = request.POST.get('field_id')
        team_a = request.POST.get('team_a')
        team_b = request.POST.get('team_b')
        match_date = request.POST.get('match_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        score_a = request.POST.get('score_a', 0)
        score_b = request.POST.get('score_b', 0)
        status = request.POST.get('status', 'scheduled')

        if title and field_id and team_a and team_b and match_date:
            field = Field.objects.get(id=field_id)
            if match_id:
                try:
                    match = Match.objects.get(id=match_id)
                    match.title = title
                    match.field = field
                    match.team_a = team_a
                    match.team_b = team_b
                    match.match_date = match_date
                    match.start_time = start_time
                    match.end_time = end_time
                    match.score_a = score_a
                    match.score_b = score_b
                    match.status = status
                    match.save()
                except Match.DoesNotExist:
                    pass
            else:
                Match.objects.create(
                    title=title,
                    field=field,
                    team_a=team_a,
                    team_b=team_b,
                    match_date=match_date,
                    start_time=start_time,
                    end_time=end_time,
                    score_a=score_a,
                    score_b=score_b,
                    status=status
                )
            return redirect('matches_list')

    matches = Match.objects.all().order_by('-match_date', '-start_time')
    fields = Field.objects.all()
    context = {
        'matches': matches,
        'fields': fields,
    }
    return render(request, 'stadium/matches_list.html', context)

@login_required
def finances_list(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        record_type = request.POST.get('record_type')
        category = request.POST.get('category')
        description = request.POST.get('description', '')
        amount = request.POST.get('amount', 0)

        if date and record_type and category and amount:
            FinancialRecord.objects.create(
                date=date,
                record_type=record_type,
                category=category,
                description=description,
                amount=amount
            )
            return redirect('finances_list')

    records = FinancialRecord.objects.all().order_by('-date')
    context = {
        'records': records,
    }
    return render(request, 'stadium/finances_list.html', context)
