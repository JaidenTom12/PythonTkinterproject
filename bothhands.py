import cv2
import mediapipe as mp
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import time

class CameraWhiteboard:
    def __init__(self, root):
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # Allow detection of two hands
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Setup camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Initialize drawing variables
        self.canvas = np.ones((480, 640, 3), dtype=np.uint8) * 255
        self.right_last_point = None  # For drawing with right hand
        self.left_last_point = None   # For erasing with left hand
        self.color = (0, 0, 0)
        self.thickness = 2
        
        # Setup UI
        self.root = root
        self.root.title("Camera Whiteboard")
        self.root.geometry("1000x600")
        
        # Create frames
        self.camera_frame = ctk.CTkFrame(self.root)
        self.camera_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.canvas_frame = ctk.CTkFrame(self.root)
        self.canvas_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.controls_frame = ctk.CTkFrame(self.root)
        self.controls_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        
        # Create labels for camera and canvas
        self.camera_label = ctk.CTkLabel(self.camera_frame, text="")
        self.camera_label.pack(fill="both", expand=True)
        
        self.canvas_label = ctk.CTkLabel(self.canvas_frame, text="")
        self.canvas_label.pack(fill="both", expand=True)
        
        # Create controls
        self.clear_button = ctk.CTkButton(self.controls_frame, text="Clear Canvas", command=self.clear_canvas)
        self.clear_button.pack(side="left", padx=10, pady=10)
        
        self.thickness_slider = ctk.CTkSlider(self.controls_frame, from_=1, to=20, number_of_steps=19, command=self.update_thickness)
        self.thickness_slider.pack(side="left", padx=10, pady=10)
        self.thickness_slider.set(2)
        
        self.thickness_label = ctk.CTkLabel(self.controls_frame, text="Thickness: 2")
        self.thickness_label.pack(side="left", padx=5, pady=10)
        
        # Add color buttons
        self.color_black = ctk.CTkButton(self.controls_frame, text="Black", fg_color="#000000", command=lambda: self.change_color((0, 0, 0)))
        self.color_black.pack(side="left", padx=5, pady=10)
        
        self.color_red = ctk.CTkButton(self.controls_frame, text="Red", fg_color="#FF0000", command=lambda: self.change_color((0, 0, 255)))
        self.color_red.pack(side="left", padx=5, pady=10)
        
        self.color_green = ctk.CTkButton(self.controls_frame, text="Green", fg_color="#00FF00", command=lambda: self.change_color((0, 255, 0)))
        self.color_green.pack(side="left", padx=5, pady=10)
        
        self.color_blue = ctk.CTkButton(self.controls_frame, text="Blue", fg_color="#0000FF", command=lambda: self.change_color((255, 0, 0)))
        self.color_blue.pack(side="left", padx=5, pady=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.controls_frame, text="Status: Ready - Right hand to draw, Left hand to erase")
        self.status_label.pack(side="right", padx=10, pady=10)
        
        # Start camera thread
        self.running = True
        self.camera_thread = threading.Thread(target=self.camera_loop)
        self.camera_thread.daemon = True
        self.camera_thread.start()
    
    def update_thickness(self, value):
        self.thickness = int(value)
        self.thickness_label.configure(text=f"Thickness: {self.thickness}")
    
    def change_color(self, color):
        self.color = color
    
    def clear_canvas(self):
        self.canvas = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    def camera_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Flip horizontally for a mirror effect
            frame = cv2.flip(frame, 1)
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hands
            results = self.hands.process(rgb_frame)
            
            # Make a copy of the frame for visualization
            vis_frame = frame.copy()
            
            if results.multi_hand_landmarks:
                # Determine which hand is which
                left_index_tip = None
                right_index_tip = None
                
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # Draw hand landmarks on visualization frame
                    self.mp_drawing.draw_landmarks(
                        vis_frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Get handedness (left or right)
                    handedness = results.multi_handedness[idx].classification[0].label
                    
                    # Get index finger tip position
                    index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    h, w, _ = frame.shape
                    index_tip_x, index_tip_y = int(index_tip.x * w), int(index_tip.y * h)
                    
                    # Store according to hand
                    if handedness == "Right":  # This is the right hand (appears on left due to mirroring)
                        right_index_tip = (index_tip_x, index_tip_y)
                        # Draw a green circle for right hand (drawing)
                        cv2.circle(vis_frame, right_index_tip, 10, (0, 255, 0), -1)
                        cv2.putText(vis_frame, "Draw", (right_index_tip[0]-20, right_index_tip[1]-20), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                    else:  # This is the left hand (appears on right due to mirroring)
                        left_index_tip = (index_tip_x, index_tip_y)
                        # Draw a red circle for left hand (erasing)
                        cv2.circle(vis_frame, left_index_tip, 15, (0, 0, 255), -1)
                        cv2.putText(vis_frame, "Erase", (left_index_tip[0]-20, left_index_tip[1]-20), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # Handle right hand drawing
                if right_index_tip:
                    if self.right_last_point is None:
                        self.right_last_point = right_index_tip
                    else:
                        # Draw line between last and current point
                        cv2.line(self.canvas, self.right_last_point, right_index_tip, self.color, self.thickness)
                        self.right_last_point = right_index_tip
                else:
                    self.right_last_point = None
                
                # Handle left hand erasing
                if left_index_tip:
                    # Erase mode: draw white circle
                    cv2.circle(self.canvas, left_index_tip, self.thickness * 5, (255, 255, 255), -1)
                    self.left_last_point = left_index_tip
                else:
                    self.left_last_point = None
            else:
                self.right_last_point = None
                self.left_last_point = None
                self.status_label.configure(text="Status: No Hands Detected")
            
            # Convert frames to PhotoImage
            vis_image = cv2.cvtColor(vis_frame, cv2.COLOR_BGR2RGB)
            vis_image = Image.fromarray(vis_image)
            vis_photo = ImageTk.PhotoImage(image=vis_image)
            
            canvas_image = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2RGB)
            canvas_image = Image.fromarray(canvas_image)
            canvas_photo = ImageTk.PhotoImage(image=canvas_image)
            
            # Update labels
            self.camera_label.configure(image=vis_photo)
            self.camera_label.image = vis_photo
            
            self.canvas_label.configure(image=canvas_photo)
            self.canvas_label.image = canvas_photo
            
            time.sleep(0.01)
    
    def cleanup(self):
        self.running = False
        if self.camera_thread.is_alive():
            self.camera_thread.join(timeout=1.0)
        self.cap.release()

if __name__ == "__main__":
    # Set CTk appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create app
    root = ctk.CTk()
    app = CameraWhiteboard(root)
    
    # Handle closing
    def on_closing():
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()