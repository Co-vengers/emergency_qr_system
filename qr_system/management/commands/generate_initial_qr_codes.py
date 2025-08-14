# qr_system/management/commands/generate_initial_qr_codes.py
import io
import qrcode
import uuid
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.urls import reverse
from qr_system.models import QRCode

class Command(BaseCommand):
    help = 'Generate initial QR codes for the system'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of QR codes to generate')
        parser.add_argument('--base-url', type=str, default='http://localhost:8000', help='Base URL for QR codes')

    def handle(self, *args, **options):
        count = options['count']
        base_url = options['base_url']
        
        self.stdout.write(f"Generating {count} QR codes...")
        
        for i in range(count):
            # Generate unique code
            qr_code_data = str(uuid.uuid4())
            
            # Create QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            # Link to the scan URL
            qr.add_data(f"{base_url}{reverse('scan_qr', args=[qr_code_data])}")
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
            
            self.stdout.write(f"Generated QR code {i+1}/{count}: {qr_code_data}")
        
        self.stdout.write(self.style.SUCCESS(f"Successfully generated {count} QR codes!"))