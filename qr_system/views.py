import qrcode
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import reverse
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.db import transaction
from django.conf import settings

from .models import User, QRCode, EmergencyInfo
from .forms import CustomUserCreationForm, EmergencyInfoForm

def home(request):
    """Home page view"""
    return render(request, 'qr_system/home.html')

def scan_qr(request, qr_code_data):
    """Handle QR code scanning"""
    try:
        qr_code = QRCode.objects.get(qr_code_data=qr_code_data)
        
        # If QR code is assigned to a user, show their profile
        if qr_code.is_assigned:
            return redirect('profile_view', qr_code_data=qr_code_data)
        else:
            # QR code is not assigned, redirect to registration
            return redirect('register', qr_code_data=qr_code_data)
    except QRCode.DoesNotExist:
        # QR code not found in the system
        messages.error(request, "Invalid QR code. This code is not registered in our system.")
        return redirect('home')

def profile_view(request, qr_code_data):
    """Public profile view for a QR code"""
    qr_code = get_object_or_404(QRCode, qr_code_data=qr_code_data)
    
    if not qr_code.is_assigned:
        # If QR is not assigned, redirect to registration
        return redirect('register', qr_code_data=qr_code_data)
    
    # Get emergency info
    try:
        emergency_info = EmergencyInfo.objects.get(user=qr_code.assigned_to)
        emergency_contacts = emergency_info.get_emergency_contacts_list()
        
        # Check if current user is the owner of this profile
        is_owner = request.user.is_authenticated and request.user == qr_code.assigned_to
        
        return render(request, 'qr_system/profile_view.html', {
            'emergency_info': emergency_info,
            'emergency_contacts': emergency_contacts,
            'is_owner': is_owner,
            'qr_code': qr_code,
        })
    except EmergencyInfo.DoesNotExist:
        if request.user.is_authenticated and request.user == qr_code.assigned_to:
            # If the authenticated user owns this QR but hasn't created info yet
            messages.info(request, "Please complete your emergency information.")
            return redirect('create_emergency_info')
        else:
            # If someone else is viewing an incomplete profile
            messages.info(request, "This profile hasn't been completed yet.")
            return redirect('home')

def register(request, qr_code_data=None):
    """User registration view"""
    # Verify QR code exists and is unassigned
    if qr_code_data:
        try:
            qr_code = QRCode.objects.get(qr_code_data=qr_code_data)
            if qr_code.is_assigned:
                messages.error(request, "This QR code is already registered.")
                return redirect('profile_view', qr_code_data=qr_code_data)
        except QRCode.DoesNotExist:
            messages.error(request, "Invalid QR code.")
            return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                
                # If registration was initiated by scanning a QR code, assign it
                if qr_code_data:
                    qr_code = QRCode.objects.get(qr_code_data=qr_code_data)
                    qr_code.assigned_to = user
                    qr_code.save()
                
                # Log in the user
                login(request, user)
                
                # Redirect to create emergency info
                messages.success(request, "Registration successful! Please complete your emergency information.")
                return redirect('create_emergency_info')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'qr_system/register.html', {
        'form': form,
        'qr_code_data': qr_code_data,
    })

@login_required
def create_emergency_info(request):
    """Create or update emergency information"""
    # Check if user already has emergency info
    try:
        emergency_info = EmergencyInfo.objects.get(user=request.user)
        return redirect('update_emergency_info')
    except EmergencyInfo.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = EmergencyInfoForm(request.POST)
        if form.is_valid():
            emergency_info = form.save(commit=False)
            emergency_info.user = request.user
            emergency_info.save()
            
            messages.success(request, "Emergency information saved successfully!")
            
            # Redirect to the user's profile
            try:
                qr_code = QRCode.objects.get(assigned_to=request.user)
                return redirect('profile_view', qr_code_data=qr_code.qr_code_data)
            except QRCode.DoesNotExist:
                # If no QR code assigned yet, redirect to dashboard
                return redirect('dashboard')
    else:
        form = EmergencyInfoForm()
    
    return render(request, 'qr_system/emergency_info_form.html', {'form': form, 'is_new': True})

@login_required
def update_emergency_info(request):
    """Update emergency information"""
    try:
        emergency_info = EmergencyInfo.objects.get(user=request.user)
    except EmergencyInfo.DoesNotExist:
        return redirect('create_emergency_info')
    
    if request.method == 'POST':
        form = EmergencyInfoForm(request.POST, instance=emergency_info)
        if form.is_valid():
            form.save()
            messages.success(request, "Emergency information updated successfully!")
            
            # Redirect to the user's profile
            try:
                qr_code = QRCode.objects.get(assigned_to=request.user)
                return redirect('profile_view', qr_code_data=qr_code.qr_code_data)
            except QRCode.DoesNotExist:
                # If no QR code assigned yet, redirect to dashboard
                return redirect('dashboard')
    else:
        form = EmergencyInfoForm(instance=emergency_info)
    
    return render(request, 'qr_system/emergency_info_form.html', {'form': form, 'is_new': False})

@login_required
def dashboard(request):
    """User dashboard view"""
    # Get user's QR codes
    qr_codes = QRCode.objects.filter(assigned_to=request.user)
    
    # Check if user has emergency info
    has_emergency_info = EmergencyInfo.objects.filter(user=request.user).exists()
    
    return render(request, 'qr_system/dashboard.html', {
        'qr_codes': qr_codes,
        'has_emergency_info': has_emergency_info,
    })

@login_required
def claim_qr_code(request):
    """Claim an unassigned QR code"""
    if request.method == 'POST':
        qr_code_data = request.POST.get('qr_code_data')
        
        try:
            qr_code = QRCode.objects.get(qr_code_data=qr_code_data)
            
            if qr_code.is_assigned:
                messages.error(request, "This QR code is already claimed by someone else.")
            else:
                qr_code.assigned_to = request.user
                qr_code.save()
                messages.success(request, "QR code claimed successfully!")
                
                # Redirect to the user's profile if they have emergency info
                if EmergencyInfo.objects.filter(user=request.user).exists():
                    return redirect('profile_view', qr_code_data=qr_code.qr_code_data)
                else:
                    return redirect('create_emergency_info')
                
        except QRCode.DoesNotExist:
            messages.error(request, "Invalid QR code.")
    
    return redirect('dashboard')

def generate_qr_codes(request):
    """Admin function to generate QR codes"""
    # This should be restricted to admin users in production
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == 'POST':
        count = int(request.POST.get('count', 1))
        
        # Generate QR codes
        for i in range(count):
            # Generate unique code
            import uuid
            qr_code_data = str(uuid.uuid4())
            
            # Create QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f"{request.build_absolute_uri(reverse('scan_qr', args=[qr_code_data]))}")
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to BytesIO
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            
            # Create QR code record
            qr_code = QRCode(qr_code_data=qr_code_data)
            qr_code.qr_image.save(f"qr_{qr_code_data}.png", ContentFile(buffer.read()), save=False)
            qr_code.save()
        
        messages.success(request, f"Successfully generated {count} QR codes!")
        
    return render(request, 'qr_system/generate_qr_codes.html')