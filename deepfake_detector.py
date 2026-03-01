"""
Fake Analyzer - Deepfake Detection System
For AMD Slingshot Hackathon
"""
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import threading
import time
import datetime
import os
import json

class DeepfakeDetector:
    """Main class for the deepfake detection system"""
    
    def __init__(self):
        self.is_running = False
        self.current_risk = 0
        self.detection_history = []
        self.alert_showing = False
        
    def simple_face_detection(self, frame):
        """
        Simplified face detection - works without ML models
        Uses OpenCV's built-in face detector
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Load pre-trained face detector
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        return faces
    
    def analyze_face_quality(self, frame, faces):
        """
        Analyze face for signs of deepfake
        This is a SIMPLIFIED version for demo - uses heuristics
        """
        if len(faces) == 0:
            return 0, "No face detected"
        
        risk_score = 0
        reasons = []
        
        for (x, y, w, h) in faces:
            # Extract face region
            face_roi = frame[y:y+h, x:x+w]
            
            # Check 1: Blurriness (deepfakes often have blurry edges)
            gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
            
            if laplacian_var < 50:  # Too blurry
                risk_score += 30
                reasons.append("Unnatural blurring")
            
            # Check 2: Color uniformity (deepfakes have flat colors)
            if len(face_roi) > 0:
                std_dev = np.std(face_roi)
                if std_dev < 30:  # Too uniform
                    risk_score += 25
                    reasons.append("Color anomalies")
            
            # Check 3: Edge inconsistencies
            edges = cv2.Canny(gray_face, 100, 200)
            edge_ratio = np.sum(edges > 0) / edges.size
            
            if edge_ratio < 0.05:  # Too few edges
                risk_score += 20
                reasons.append("Missing facial details")
            elif edge_ratio > 0.3:  # Too many edges
                risk_score += 15
                reasons.append("Artificial sharpening")
        
        # Cap at 100
        risk_score = min(risk_score, 100)
        
        return risk_score, reasons
    
    def detect_from_webcam(self):
        """Main webcam detection loop"""
        self.is_running = True
        
        # Open webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("ERROR: Could not open webcam")
            return
        
        print("✅ Webcam opened successfully")
        print("🔍 Analyzing for deepfakes...")
        
        frame_count = 0
        
        while self.is_running:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect faces
            faces = self.simple_face_detection(frame)
            
            # Analyze every 10 frames (to save processing)
            if frame_count % 10 == 0:
                risk_score, reasons = self.analyze_face_quality(frame, faces)
                self.current_risk = risk_score
                
                # Add to history
                self.detection_history.append({
                    'timestamp': datetime.datetime.now().strftime("%H:%M:%S"),
                    'risk': risk_score,
                    'reasons': reasons
                })
                
                # Keep only last 50 records
                if len(self.detection_history) > 50:
                    self.detection_history.pop(0)
            
            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                # Color based on risk
                if self.current_risk > 70:
                    color = (0, 0, 255)  # Red - high risk
                elif self.current_risk > 40:
                    color = (0, 255, 255)  # Yellow - medium risk
                else:
                    color = (0, 255, 0)  # Green - low risk
                
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                # Add risk label
                label = f"Risk: {self.current_risk}%"
                cv2.putText(frame, label, (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Add status text
            status = f"Fake Analyzer - Risk Level: {self.current_risk}%"
            cv2.putText(frame, status, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show alert if high risk
            if self.current_risk > 70 and not self.alert_showing:
                self.show_alert_popup(self.current_risk, reasons)
                self.alert_showing = True
            elif self.current_risk <= 70:
                self.alert_showing = False
            
            # Display frame
            cv2.imshow('Risk Analyzer - Deepfake Detection', frame)
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
    def show_alert_popup(self, risk, reasons):
        """Show an alert popup when deepfake detected"""
        print("\n" + "="*50)
        print("🚨 DEEPFAKE ALERT! 🚨")
        print("="*50)
        print(f"Risk Level: {risk}%")
        print(f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}")
        print("\nIndicators detected:")
        for r in reasons:
            print(f"  • {r}")
        print("\n⚠️  This may be AI-generated content!")
        print("="*50 + "\n")
        
    def run(self):
        """Start the detector"""
        print("\n" + "="*50)
        print("🚀 FAKE ANALYZER - Deepfake Detector")
        print("="*50)
        print("\nInstructions:")
        print("• Webcam will open automatically")
        print("• Green box = Low risk")
        print("• Yellow box = Medium risk")
        print("• Red box = High risk (deepfake likely)")
        print("• Press 'q' to quit")
        print("\nStarting in 3 seconds...")
        
        time.sleep(3)
        
        # Run in separate thread so UI doesn't freeze
        detection_thread = threading.Thread(target=self.detect_from_webcam)
        detection_thread.daemon = True
        detection_thread.start()
        
        # Keep main thread alive
        try:
            while detection_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            self.is_running = False
            print("\n👋 Shutting down...")

# ========== RUN THE APP ==========
if __name__ == "__main__":
    detector = DeepfakeDetector()
    detector.run()
