"""
Zero-Error Medication Management System - Desktop GUI
Simple tkinter-based interface for testing the API
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import json
from pathlib import Path
from datetime import datetime
import threading
from PIL import Image, ImageTk
import io

# API Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Status colors
STATUS_COLORS = {
    'running': '#2ecc71',      # Green
    'error': '#e74c3c',        # Red
    'warning': '#f39c12',      # Orange
    'info': '#3498db'          # Blue
}

class MedicationManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Zero-Error Medication Management System")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Store selected files
        self.selected_files = {}
        self.workflow_id = None
        
        # Create main layout
        self.create_widgets()
        self.check_server_status()
        
    def create_widgets(self):
        """Create main UI components"""
        
        # ===== Top Status Bar =====
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.status_frame, text="Server Status:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(
            self.status_frame, 
            text="● Checking...", 
            foreground="orange",
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # ===== Notebook (Tabs) =====
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Analyze Prescription
        self.create_prescription_tab()
        
        # Tab 2: Verify Pill
        self.create_pill_tab()
        
        # Tab 3: Verify Intake
        self.create_intake_tab()
        
        # Tab 4: Complete Workflow
        self.create_complete_tab()
        
        # Tab 5: View Results
        self.create_results_tab()
        
    def create_prescription_tab(self):
        """Create Prescription Analysis Tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📋 Analyze Prescription")
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Input Parameters", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text="Patient ID:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.prescription_patient_id = ttk.Entry(input_frame, width=30)
        self.prescription_patient_id.insert(0, "PAT-001")
        self.prescription_patient_id.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(input_frame, text="Notes:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.prescription_notes = ttk.Entry(input_frame, width=30)
        self.prescription_notes.insert(0, "Sample prescription")
        self.prescription_notes.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # File selection
        file_frame = ttk.LabelFrame(frame, text="Select Prescription Image", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.prescription_file_label = ttk.Label(file_frame, text="No file selected", foreground="gray")
        self.prescription_file_label.pack(side=tk.LEFT, pady=10)
        
        ttk.Button(
            file_frame, 
            text="Browse Image", 
            command=lambda: self.select_file('prescription')
        ).pack(side=tk.RIGHT, padx=10)
        
        # Submit button
        ttk.Button(
            frame,
            text="▶ Analyze Prescription",
            command=self.analyze_prescription
        ).pack(pady=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Response", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.prescription_output = scrolledtext.ScrolledText(
            output_frame, 
            height=15, 
            width=80,
            font=("Courier", 9)
        )
        self.prescription_output.pack(fill=tk.BOTH, expand=True)
        
    def create_pill_tab(self):
        """Create Pill Verification Tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="💊 Verify Pill")
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Input Parameters", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text="Patient ID:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pill_patient_id = ttk.Entry(input_frame, width=30)
        self.pill_patient_id.insert(0, "PAT-001")
        self.pill_patient_id.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(input_frame, text="Medication ID:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pill_medication_id = ttk.Entry(input_frame, width=30)
        self.pill_medication_id.insert(0, "MED-001")
        self.pill_medication_id.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # File selection
        file_frame = ttk.LabelFrame(frame, text="Select Pill Image", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.pill_file_label = ttk.Label(file_frame, text="No file selected", foreground="gray")
        self.pill_file_label.pack(side=tk.LEFT, pady=10)
        
        ttk.Button(
            file_frame, 
            text="Browse Image", 
            command=lambda: self.select_file('pill')
        ).pack(side=tk.RIGHT, padx=10)
        
        # Submit button
        ttk.Button(
            frame,
            text="▶ Verify Pill",
            command=self.verify_pill
        ).pack(pady=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Response", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.pill_output = scrolledtext.ScrolledText(
            output_frame, 
            height=15, 
            width=80,
            font=("Courier", 9)
        )
        self.pill_output.pack(fill=tk.BOTH, expand=True)
        
    def create_intake_tab(self):
        """Create Intake Verification Tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🎬 Verify Intake")
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Input Parameters", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text="Patient ID:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.intake_patient_id = ttk.Entry(input_frame, width=30)
        self.intake_patient_id.insert(0, "PAT-001")
        self.intake_patient_id.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(input_frame, text="Medication ID:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.intake_medication_id = ttk.Entry(input_frame, width=30)
        self.intake_medication_id.insert(0, "MED-001")
        self.intake_medication_id.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # File selection
        file_frame = ttk.LabelFrame(frame, text="Select Intake Video", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.intake_file_label = ttk.Label(file_frame, text="No file selected", foreground="gray")
        self.intake_file_label.pack(side=tk.LEFT, pady=10)
        
        ttk.Button(
            file_frame, 
            text="Browse Video", 
            command=lambda: self.select_file('intake')
        ).pack(side=tk.RIGHT, padx=10)
        
        # Submit button
        ttk.Button(
            frame,
            text="▶ Verify Intake",
            command=self.verify_intake
        ).pack(pady=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Response", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.intake_output = scrolledtext.ScrolledText(
            output_frame, 
            height=15, 
            width=80,
            font=("Courier", 9)
        )
        self.intake_output.pack(fill=tk.BOTH, expand=True)
        
    def create_complete_tab(self):
        """Create Complete Workflow Tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="✅ Complete Workflow")
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Input Parameters", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text="Patient ID:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.complete_patient_id = ttk.Entry(input_frame, width=30)
        self.complete_patient_id.insert(0, "PAT-001")
        self.complete_patient_id.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(input_frame, text="Medication ID:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.complete_medication_id = ttk.Entry(input_frame, width=30)
        self.complete_medication_id.insert(0, "MED-001")
        self.complete_medication_id.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(input_frame, text="Notes:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.complete_notes = ttk.Entry(input_frame, width=30)
        self.complete_notes.insert(0, "Complete workflow test")
        self.complete_notes.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # File selections
        files_frame = ttk.LabelFrame(frame, text="Select Files", padding=10)
        files_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Prescription file
        ttk.Label(files_frame, text="Prescription Image:", font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.complete_prescription_label = ttk.Label(files_frame, text="No file selected", foreground="gray")
        self.complete_prescription_label.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Button(
            files_frame, 
            text="Browse", 
            command=lambda: self.select_complete_file('prescription')
        ).grid(row=0, column=2, padx=5)
        
        # Pill file
        ttk.Label(files_frame, text="Pill Image:", font=("Arial", 9)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.complete_pill_label = ttk.Label(files_frame, text="No file selected", foreground="gray")
        self.complete_pill_label.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Button(
            files_frame, 
            text="Browse", 
            command=lambda: self.select_complete_file('pill')
        ).grid(row=1, column=2, padx=5)
        
        # Intake file
        ttk.Label(files_frame, text="Intake Video:", font=("Arial", 9)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.complete_intake_label = ttk.Label(files_frame, text="No file selected", foreground="gray")
        self.complete_intake_label.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Button(
            files_frame, 
            text="Browse", 
            command=lambda: self.select_complete_file('intake')
        ).grid(row=2, column=2, padx=5)
        
        # Submit button
        ttk.Button(
            frame,
            text="▶ Run Complete Verification",
            command=self.complete_verification
        ).pack(pady=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Response", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.complete_output = scrolledtext.ScrolledText(
            output_frame, 
            height=15, 
            width=80,
            font=("Courier", 9)
        )
        self.complete_output.pack(fill=tk.BOTH, expand=True)
        
    def create_results_tab(self):
        """Create Results Viewing Tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📊 View Results")
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Get Results", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text="Workflow ID:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.result_workflow_id = ttk.Entry(input_frame, width=50)
        self.result_workflow_id.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Button(
            input_frame,
            text="Fetch Result",
            command=self.get_result
        ).grid(row=0, column=2, padx=10)
        
        ttk.Button(
            input_frame,
            text="Fetch Report",
            command=self.get_report
        ).grid(row=0, column=3, padx=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Result Data", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.result_output = scrolledtext.ScrolledText(
            output_frame, 
            height=20, 
            width=80,
            font=("Courier", 9)
        )
        self.result_output.pack(fill=tk.BOTH, expand=True)
        
    # ===== Helper Methods =====
    
    def select_file(self, file_type):
        """Select file for specific endpoint"""
        if file_type == 'prescription':
            filetypes = (("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
            file_path = filedialog.askopenfilename(filetypes=filetypes)
            if file_path:
                self.selected_files['prescription'] = file_path
                self.prescription_file_label.config(
                    text=Path(file_path).name,
                    foreground="green"
                )
        elif file_type == 'pill':
            filetypes = (("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
            file_path = filedialog.askopenfilename(filetypes=filetypes)
            if file_path:
                self.selected_files['pill'] = file_path
                self.pill_file_label.config(
                    text=Path(file_path).name,
                    foreground="green"
                )
        elif file_type == 'intake':
            filetypes = (("Video files", "*.mp4 *.avi *.mov"), ("All files", "*.*"))
            file_path = filedialog.askopenfilename(filetypes=filetypes)
            if file_path:
                self.selected_files['intake'] = file_path
                self.intake_file_label.config(
                    text=Path(file_path).name,
                    foreground="green"
                )
    
    def select_complete_file(self, file_type):
        """Select file for complete workflow"""
        if file_type == 'prescription':
            filetypes = (("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
            file_path = filedialog.askopenfilename(filetypes=filetypes)
            if file_path:
                self.selected_files['complete_prescription'] = file_path
                self.complete_prescription_label.config(
                    text=Path(file_path).name,
                    foreground="green"
                )
        elif file_type == 'pill':
            filetypes = (("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
            file_path = filedialog.askopenfilename(filetypes=filetypes)
            if file_path:
                self.selected_files['complete_pill'] = file_path
                self.complete_pill_label.config(
                    text=Path(file_path).name,
                    foreground="green"
                )
        elif file_type == 'intake':
            filetypes = (("Video files", "*.mp4 *.avi *.mov"), ("All files", "*.*"))
            file_path = filedialog.askopenfilename(filetypes=filetypes)
            if file_path:
                self.selected_files['complete_intake'] = file_path
                self.complete_intake_label.config(
                    text=Path(file_path).name,
                    foreground="green"
                )
    
    def check_server_status(self):
        """Check if server is running"""
        def check():
            try:
                response = requests.get(f"{API_BASE}/health", timeout=2)
                if response.status_code == 200:
                    self.status_label.config(text="● Server Running ✓", foreground="green")
                else:
                    self.status_label.config(text="● Server Error", foreground="red")
            except:
                self.status_label.config(text="● Server Offline", foreground="red")
        
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
    
    def analyze_prescription(self):
        """Send prescription analysis request"""
        if 'prescription' not in self.selected_files:
            messagebox.showerror("Error", "Please select a prescription image first!")
            return
        
        self.prescription_output.delete(1.0, tk.END)
        self.prescription_output.insert(tk.END, "Processing... ⏳\n")
        self.root.update()
        
        def send_request():
            try:
                with open(self.selected_files['prescription'], 'rb') as f:
                    files = {'file': (Path(self.selected_files['prescription']).name, f, 'image/jpeg')}
                    params = {
                        'patient_id': self.prescription_patient_id.get(),
                    }
                    data = {
                        'notes': self.prescription_notes.get() if self.prescription_notes.get() else ''
                    }
                    
                    response = requests.post(
                        f"{API_BASE}/analyze-prescription",
                        params=params,
                        files=files,
                        data=data,
                        timeout=30
                    )
                
                self.prescription_output.delete(1.0, tk.END)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    self.workflow_id = result.get('workflow_id')
                    self.prescription_output.insert(tk.END, json.dumps(result, indent=2))
                    messagebox.showinfo("Success", f"Workflow ID: {self.workflow_id}")
                else:
                    self.prescription_output.insert(tk.END, f"Error {response.status_code}\n{response.text}")
                    messagebox.showerror("Error", f"Server returned: {response.status_code}")
                    
            except Exception as e:
                self.prescription_output.delete(1.0, tk.END)
                self.prescription_output.insert(tk.END, f"Error: {str(e)}")
                messagebox.showerror("Error", str(e))
        
        thread = threading.Thread(target=send_request, daemon=True)
        thread.start()
    
    def verify_pill(self):
        """Send pill verification request"""
        if 'pill' not in self.selected_files:
            messagebox.showerror("Error", "Please select a pill image first!")
            return
        
        self.pill_output.delete(1.0, tk.END)
        self.pill_output.insert(tk.END, "Processing... ⏳\n")
        self.root.update()
        
        def send_request():
            try:
                with open(self.selected_files['pill'], 'rb') as f:
                    files = {'file': (Path(self.selected_files['pill']).name, f, 'image/jpeg')}
                    params = {
                        'patient_id': self.pill_patient_id.get(),
                        'medication_id': self.pill_medication_id.get()
                    }
                    
                    response = requests.post(
                        f"{API_BASE}/verify-pill",
                        params=params,
                        files=files,
                        timeout=30
                    )
                
                self.pill_output.delete(1.0, tk.END)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    self.workflow_id = result.get('workflow_id')
                    self.pill_output.insert(tk.END, json.dumps(result, indent=2))
                    messagebox.showinfo("Success", f"Workflow ID: {self.workflow_id}")
                else:
                    self.pill_output.insert(tk.END, f"Error {response.status_code}\n{response.text}")
                    messagebox.showerror("Error", f"Server returned: {response.status_code}")
                    
            except Exception as e:
                self.pill_output.delete(1.0, tk.END)
                self.pill_output.insert(tk.END, f"Error: {str(e)}")
                messagebox.showerror("Error", str(e))
        
        thread = threading.Thread(target=send_request, daemon=True)
        thread.start()
    
    def verify_intake(self):
        """Send intake verification request"""
        if 'intake' not in self.selected_files:
            messagebox.showerror("Error", "Please select an intake video first!")
            return
        
        self.intake_output.delete(1.0, tk.END)
        self.intake_output.insert(tk.END, "Processing... ⏳\n")
        self.root.update()
        
        def send_request():
            try:
                with open(self.selected_files['intake'], 'rb') as f:
                    files = {'file': (Path(self.selected_files['intake']).name, f, 'video/mp4')}
                    params = {
                        'patient_id': self.intake_patient_id.get(),
                        'medication_id': self.intake_medication_id.get()
                    }
                    
                    response = requests.post(
                        f"{API_BASE}/verify-intake",
                        params=params,
                        files=files,
                        timeout=30
                    )
                
                self.intake_output.delete(1.0, tk.END)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    self.workflow_id = result.get('workflow_id')
                    self.intake_output.insert(tk.END, json.dumps(result, indent=2))
                    messagebox.showinfo("Success", f"Workflow ID: {self.workflow_id}")
                else:
                    self.intake_output.insert(tk.END, f"Error {response.status_code}\n{response.text}")
                    messagebox.showerror("Error", f"Server returned: {response.status_code}")
                    
            except Exception as e:
                self.intake_output.delete(1.0, tk.END)
                self.intake_output.insert(tk.END, f"Error: {str(e)}")
                messagebox.showerror("Error", str(e))
        
        thread = threading.Thread(target=send_request, daemon=True)
        thread.start()
    
    def complete_verification(self):
        """Send complete workflow request"""
        if not all(k in self.selected_files for k in ['complete_prescription', 'complete_pill', 'complete_intake']):
            messagebox.showerror("Error", "Please select all three files (Prescription, Pill, Intake)!")
            return
        
        self.complete_output.delete(1.0, tk.END)
        self.complete_output.insert(tk.END, "Processing... ⏳\n")
        self.root.update()
        
        def send_request():
            try:
                files = {}
                with open(self.selected_files['complete_prescription'], 'rb') as f:
                    files['prescription'] = ('prescription.jpg', f.read(), 'image/jpeg')
                with open(self.selected_files['complete_pill'], 'rb') as f:
                    files['pill'] = ('pill.jpg', f.read(), 'image/jpeg')
                with open(self.selected_files['complete_intake'], 'rb') as f:
                    files['intake'] = ('intake.mp4', f.read(), 'video/mp4')
                
                params = {
                    'patient_id': self.complete_patient_id.get(),
                    'medication_id': self.complete_medication_id.get()
                }
                
                data = {
                    'notes': self.complete_notes.get() if self.complete_notes.get() else ''
                }
                
                response = requests.post(
                    f"{API_BASE}/complete-verification",
                    params=params,
                    files=files,
                    data=data,
                    timeout=60
                )
                
                self.complete_output.delete(1.0, tk.END)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    self.workflow_id = result.get('workflow_id')
                    self.complete_output.insert(tk.END, json.dumps(result, indent=2))
                    messagebox.showinfo("Success", f"Workflow ID: {self.workflow_id}")
                else:
                    self.complete_output.insert(tk.END, f"Error {response.status_code}\n{response.text}")
                    messagebox.showerror("Error", f"Server returned: {response.status_code}")
                    
            except Exception as e:
                self.complete_output.delete(1.0, tk.END)
                self.complete_output.insert(tk.END, f"Error: {str(e)}")
                messagebox.showerror("Error", str(e))
        
        thread = threading.Thread(target=send_request, daemon=True)
        thread.start()
    
    def get_result(self):
        """Fetch result by workflow ID"""
        workflow_id = self.result_workflow_id.get() or self.workflow_id
        
        if not workflow_id:
            messagebox.showerror("Error", "Please enter a Workflow ID first!")
            return
        
        self.result_output.delete(1.0, tk.END)
        self.result_output.insert(tk.END, "Fetching... ⏳\n")
        self.root.update()
        
        def fetch():
            try:
                response = requests.get(f"{API_BASE}/result/{workflow_id}", timeout=10)
                self.result_output.delete(1.0, tk.END)
                
                if response.status_code == 200:
                    result = response.json()
                    self.result_output.insert(tk.END, json.dumps(result, indent=2))
                else:
                    self.result_output.insert(tk.END, f"Error {response.status_code}\n{response.text}")
                    
            except Exception as e:
                self.result_output.delete(1.0, tk.END)
                self.result_output.insert(tk.END, f"Error: {str(e)}")
        
        thread = threading.Thread(target=fetch, daemon=True)
        thread.start()
    
    def get_report(self):
        """Fetch report by workflow ID"""
        workflow_id = self.result_workflow_id.get() or self.workflow_id
        
        if not workflow_id:
            messagebox.showerror("Error", "Please enter a Workflow ID first!")
            return
        
        self.result_output.delete(1.0, tk.END)
        self.result_output.insert(tk.END, "Fetching... ⏳\n")
        self.root.update()
        
        def fetch():
            try:
                response = requests.get(f"{API_BASE}/report/{workflow_id}", timeout=10)
                self.result_output.delete(1.0, tk.END)
                
                if response.status_code == 200:
                    if 'application/pdf' in response.headers.get('content-type', ''):
                        self.result_output.insert(tk.END, "✓ PDF Report Retrieved Successfully!\n\n")
                        self.result_output.insert(tk.END, f"Saved to: report_{workflow_id}.pdf")
                        with open(f"report_{workflow_id}.pdf", "wb") as f:
                            f.write(response.content)
                    else:
                        result = response.json()
                        self.result_output.insert(tk.END, json.dumps(result, indent=2))
                else:
                    self.result_output.insert(tk.END, f"Error {response.status_code}\n{response.text}")
                    
            except Exception as e:
                self.result_output.delete(1.0, tk.END)
                self.result_output.insert(tk.END, f"Error: {str(e)}")
        
        thread = threading.Thread(target=fetch, daemon=True)
        thread.start()


def main():
    root = tk.Tk()
    app = MedicationManagementGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
