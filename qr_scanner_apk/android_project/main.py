
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.utils import platform
from kivy.logger import Logger
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image

class QRScannerApp(App):
    def build(self):
        self.request_android_permissions()
        
        self.layout = BoxLayout(orientation='vertical')
        
        # Camera widget
        # index=0 is usually the back camera on Android if available, or force with specific index if needed.
        # But '0' is standard for default.
        self.camera = Camera(play=True, index=0, resolution=(640, 480))
        
        # Label to display results
        self.result_label = Label(
            text="Scanning for QR codes...",
            size_hint_y=None, 
            height='100dp',
            font_size='20sp'
        )
        
        self.layout.add_widget(self.camera)
        self.layout.add_widget(self.result_label)
        
        # Schedule the detection loop
        Clock.schedule_interval(self.detect_code, 1.0 / 30.0)  # Check at 30 FPS
        
        return self.layout

    def request_android_permissions(self):
        """
        Request CAMERA permission on Android.
        """
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA])

    def detect_code(self, dt):
        """
        Grab frame from Kivy Camera, convert to format for pyzbar, and detect.
        """
        if not self.camera.texture:
            return

        try:
            # Get the texture and pixels
            texture = self.camera.texture
            size = texture.size
            pixels = texture.pixels  # Returns bytes
            
            # Create PIL image
            # Kivy texture is typically RGBA
            pil_image = Image.frombytes(mode='RGBA', size=size, data=pixels)
            
            # Convert to grayscale for detection
            gray_image = pil_image.convert('L')
            
            # Detect codes
            decoded_objects = decode(gray_image)
            
            if decoded_objects:
                # Use the first detected code
                obj = decoded_objects[0]
                data = obj.data.decode('utf-8', errors='replace')
                dtype = obj.type
                
                # Update label (Do not open URL, just show it)
                self.result_label.text = f"Detected {dtype}:\n{data}"
            else:
                # Optional: Reset text if nothing found, or keep last found?
                # Keeping "Scanning..." to show it's active when nothing is there.
                # If we want to persist the last code, we'd remove this else block.
                # But "Scanning..." gives feedback that it's working.
                # Let's keep the last detected text for a bit or reset? 
                # User asked to "show the url (if available)". 
                # If we immediately reset to "Scanning...", it might flicker too fast to read if detection is intermittent.
                # Let's compromise: don't reset immediately, or user 'Scanning...' is fine.
                # I'll stick to simple "Scanning..." when nothing is in view for now to act as a "no signal" indicator.
                pass 
                
        except Exception as e:
            Logger.exception(f"QRDetect: {e}")

if __name__ == '__main__':
    QRScannerApp().run()
