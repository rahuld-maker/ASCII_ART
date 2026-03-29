import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
import pyfiglet
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import os

# --- UI Configuration & Theme ---
ctk.set_appearance_mode("dark")
BG_COLOR = "#0D0D15"
SIDEBAR_COLOR = "#151521"
CARD_COLOR = "#1E1E2E"
TEXT_COLOR = "#FFFFFF"
ACCENT_BLUE = "#00F0FF"   
ACCENT_PURPLE = "#BD00FF" 

# ASCII Brightness Map (Dark to Light for Dark Mode UI)
ASCII_CHARS = [" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"]

class FuturisticASCIIGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NeonArt | ASCII Studio")
        self.geometry("1300x850")
        self.configure(fg_color=BG_COLOR)
        self.minsize(1100, 750)

        # App Data
        self.all_fonts = pyfiglet.FigletFont.getFonts()
        self.current_color = ACCENT_BLUE
        self.generation_count = 0
        self.current_image_path = None

        self.setup_layout()
        self.show_dashboard() 

    def setup_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ==================== SIDEBAR ====================
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=SIDEBAR_COLOR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="✦ NeonArt", font=ctk.CTkFont(family="Helvetica", size=28, weight="bold"), text_color=ACCENT_BLUE)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 40))

        # Nav Buttons
        self.btn_dash = ctk.CTkButton(self.sidebar, text="📊 Dashboard", font=ctk.CTkFont(size=15), fg_color="transparent", text_color=TEXT_COLOR, hover_color=CARD_COLOR, anchor="w", command=self.show_dashboard)
        self.btn_dash.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_gen = ctk.CTkButton(self.sidebar, text="✨ Text Art", font=ctk.CTkFont(size=15), fg_color="transparent", text_color=TEXT_COLOR, hover_color=CARD_COLOR, anchor="w", command=self.show_generator)
        self.btn_gen.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_img = ctk.CTkButton(self.sidebar, text="🖼️ Image Art", font=ctk.CTkFont(size=15), fg_color="transparent", text_color=TEXT_COLOR, hover_color=CARD_COLOR, anchor="w", command=self.show_image_gen)
        self.btn_img.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self.sidebar, text="🟢 System Online\nSaaS v3.0", text_color="gray", justify="left")
        self.status_label.grid(row=5, column=0, padx=20, pady=20, sticky="sw")

        # ==================== MAIN CONTENT AREA ====================
        self.main_container = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.frame_dashboard = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frame_generator = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frame_image_gen = ctk.CTkFrame(self.main_container, fg_color="transparent")

        self.build_dashboard()
        self.build_generator()
        self.build_image_generator()

    # ------------------ DASHBOARD VIEW ------------------
    def build_dashboard(self):
        self.frame_dashboard.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(self.frame_dashboard, text="Overview", font=ctk.CTkFont(size=32, weight="bold"), text_color=TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=(0, 20))

        cards_data = [
            ("Total Fonts", f"{len(self.all_fonts)}+", ACCENT_BLUE),
            ("Active Sessions", "1", ACCENT_PURPLE),
            ("Renders Today", "Live", "#00FF66")
        ]

        for i, (title, value, color) in enumerate(cards_data):
            card = ctk.CTkFrame(self.frame_dashboard, fg_color=CARD_COLOR, corner_radius=15, border_width=1, border_color="#2A2A3D")
            card.grid(row=1, column=i, padx=10, pady=10, sticky="nsew")
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14), text_color="gray").pack(pady=(20, 5), padx=20, anchor="w")
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=color).pack(pady=(0, 20), padx=20, anchor="w")

        graph_frame = ctk.CTkFrame(self.frame_dashboard, fg_color=CARD_COLOR, corner_radius=15, border_width=1, border_color="#2A2A3D")
        graph_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=20, sticky="nsew")
        ctk.CTkLabel(graph_frame, text="Rendering Performance (ms)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10, padx=20, anchor="w")

        fig, ax = plt.subplots(figsize=(8, 3), facecolor=CARD_COLOR)
        ax.set_facecolor(CARD_COLOR)
        x = list(range(1, 11))
        y = [random.randint(10, 50) for _ in range(10)]
        ax.plot(x, y, color=ACCENT_PURPLE, marker='o', linewidth=2, markersize=6)
        ax.tick_params(colors='gray')
        for spine in ax.spines.values(): spine.set_color('#2A2A3D')
            
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)

    # ------------------ TEXT GENERATOR VIEW ------------------
    def build_generator(self):
        self.frame_generator.grid_columnconfigure(1, weight=1)
        self.frame_generator.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self.frame_generator, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(header, text="Text Studio Workspace", font=ctk.CTkFont(size=32, weight="bold"), text_color=TEXT_COLOR).pack(side="left")

        controls = ctk.CTkFrame(self.frame_generator, width=300, fg_color=CARD_COLOR, corner_radius=15)
        controls.grid(row=1, column=0, sticky="nsew", padx=(0, 20))
        controls.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(controls, text="ENTER TEXT", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w", padx=20, pady=(20, 5))
        self.text_input = ctk.CTkEntry(controls, placeholder_text="Type to generate...", height=40, border_color=ACCENT_BLUE, border_width=1, fg_color="#151521")
        self.text_input.pack(fill="x", padx=20, pady=5)
        self.text_input.insert(0, "NEON")
        self.text_input.bind("<KeyRelease>", self.generate_text_art)

        ctk.CTkLabel(controls, text="FONT LIBRARY", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w", padx=20, pady=(20, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_font_list)
        self.search_entry = ctk.CTkEntry(controls, textvariable=self.search_var, placeholder_text="Search 50+ fonts...", height=35)
        self.search_entry.pack(fill="x", padx=20, pady=5)

        self.font_listbox = tk.Listbox(controls, bg="#151521", fg=TEXT_COLOR, selectbackground=ACCENT_PURPLE, highlightthickness=0, borderwidth=0, font=("Inter", 12))
        self.font_listbox.pack(fill="both", expand=True, padx=20, pady=5)
        self.font_listbox.bind("<<ListboxSelect>>", self.generate_text_art)
        self.update_font_list()

        ctk.CTkLabel(controls, text="GLOW COLOR", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w", padx=20, pady=(15, 5))
        color_frame = ctk.CTkFrame(controls, fg_color="transparent")
        color_frame.pack(fill="x", padx=20, pady=5)
        
        colors = [ACCENT_BLUE, ACCENT_PURPLE, "#00FF66", "#FF0055", "#FFD700", "#FFFFFF"]
        for i, color in enumerate(colors):
            btn = ctk.CTkButton(color_frame, text="", width=25, height=25, fg_color=color, hover_color=color, corner_radius=12, command=lambda c=color: self.set_color(c))
            btn.grid(row=0, column=i, padx=4)

        preview_container = ctk.CTkFrame(self.frame_generator, fg_color=CARD_COLOR, corner_radius=15)
        preview_container.grid(row=1, column=1, sticky="nsew")
        preview_container.grid_rowconfigure(0, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)

        self.text_preview_box = ctk.CTkTextbox(preview_container, font=ctk.CTkFont(family="Courier", size=14), wrap="none", fg_color="#0D0D15", text_color=self.current_color, border_width=1, border_color="#2A2A3D")
        self.text_preview_box.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        export_frame = ctk.CTkFrame(preview_container, fg_color="transparent")
        export_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        export_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(export_frame, text="📋 Copy", fg_color=ACCENT_PURPLE, hover_color="#9B00D3", command=lambda: self.copy_to_clipboard(self.text_preview_box)).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(export_frame, text="📄 Save TXT", fg_color="transparent", border_width=1, border_color=ACCENT_PURPLE, command=lambda: self.save_txt(self.text_preview_box)).grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(export_frame, text="🖼️ Export PNG", fg_color="transparent", border_width=1, border_color=ACCENT_BLUE, command=lambda: self.save_image(self.text_preview_box)).grid(row=0, column=2, padx=5, sticky="ew")

    # ------------------ IMAGE GENERATOR VIEW ------------------
    def build_image_generator(self):
        self.frame_image_gen.grid_columnconfigure(1, weight=1)
        self.frame_image_gen.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self.frame_image_gen, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(header, text="Image Engine Vision", font=ctk.CTkFont(size=32, weight="bold"), text_color=TEXT_COLOR).pack(side="left")

        controls = ctk.CTkFrame(self.frame_image_gen, width=300, fg_color=CARD_COLOR, corner_radius=15)
        controls.grid(row=1, column=0, sticky="nsew", padx=(0, 20))

        ctk.CTkLabel(controls, text="UPLOAD ASSET", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkButton(controls, text="📂 Browse Image...", fg_color=ACCENT_BLUE, text_color="black", hover_color="#00C4D1", font=ctk.CTkFont(weight="bold"), command=self.load_image).pack(fill="x", padx=20, pady=10)
        
        self.img_label_status = ctk.CTkLabel(controls, text="No image selected", text_color="gray", font=ctk.CTkFont(size=11))
        self.img_label_status.pack(padx=20, pady=0)

        ctk.CTkLabel(controls, text="RESOLUTION (WIDTH)", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w", padx=20, pady=(30, 5))
        self.res_slider = ctk.CTkSlider(controls, from_=50, to=250, number_of_steps=200, progress_color=ACCENT_PURPLE, button_color=ACCENT_BLUE, command=self.update_image_art)
        self.res_slider.set(100)
        self.res_slider.pack(fill="x", padx=20, pady=10)
        self.res_label = ctk.CTkLabel(controls, text="100 columns", font=ctk.CTkFont(size=11))
        self.res_label.pack(padx=20, pady=0)

        preview_container = ctk.CTkFrame(self.frame_image_gen, fg_color=CARD_COLOR, corner_radius=15)
        preview_container.grid(row=1, column=1, sticky="nsew")
        preview_container.grid_rowconfigure(0, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)

        # VERY IMPORTANT: Using a smaller font for image ASCII so it fits better on screen
        self.img_preview_box = ctk.CTkTextbox(preview_container, font=ctk.CTkFont(family="Courier", size=6), wrap="none", fg_color="#0D0D15", text_color=self.current_color, border_width=1, border_color="#2A2A3D")
        self.img_preview_box.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        export_frame = ctk.CTkFrame(preview_container, fg_color="transparent")
        export_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        export_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(export_frame, text="📋 Copy", fg_color=ACCENT_PURPLE, hover_color="#9B00D3", command=lambda: self.copy_to_clipboard(self.img_preview_box)).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(export_frame, text="📄 Save TXT", fg_color="transparent", border_width=1, border_color=ACCENT_PURPLE, command=lambda: self.save_txt(self.img_preview_box)).grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(export_frame, text="🖼️ Export PNG", fg_color="transparent", border_width=1, border_color=ACCENT_BLUE, command=lambda: self.save_image(self.img_preview_box, is_image=True)).grid(row=0, column=2, padx=5, sticky="ew")

    # --- View Switching Logic ---
    def reset_nav_buttons(self):
        self.btn_dash.configure(fg_color="transparent", text_color=TEXT_COLOR)
        self.btn_gen.configure(fg_color="transparent", text_color=TEXT_COLOR)
        self.btn_img.configure(fg_color="transparent", text_color=TEXT_COLOR)

    def show_dashboard(self):
        self.frame_generator.grid_forget()
        self.frame_image_gen.grid_forget()
        self.frame_dashboard.grid(row=0, column=0, sticky="nsew")
        self.reset_nav_buttons()
        self.btn_dash.configure(fg_color=CARD_COLOR, text_color=ACCENT_BLUE)

    def show_generator(self):
        self.frame_dashboard.grid_forget()
        self.frame_image_gen.grid_forget()
        self.frame_generator.grid(row=0, column=0, sticky="nsew")
        self.reset_nav_buttons()
        self.btn_gen.configure(fg_color=CARD_COLOR, text_color=ACCENT_PURPLE)
        self.generate_text_art()

    def show_image_gen(self):
        self.frame_dashboard.grid_forget()
        self.frame_generator.grid_forget()
        self.frame_image_gen.grid(row=0, column=0, sticky="nsew")
        self.reset_nav_buttons()
        self.btn_img.configure(fg_color=CARD_COLOR, text_color="#00FF66")

    # --- Logic: Text Generator ---
    def update_font_list(self, *args):
        search = self.search_var.get().lower()
        self.font_listbox.delete(0, tk.END)
        for f in self.all_fonts:
            if search in f.lower():
                self.font_listbox.insert(tk.END, f)
        if self.font_listbox.size() > 0: self.font_listbox.selection_set(0)

    def generate_text_art(self, event=None):
        text = self.text_input.get()
        selection = self.font_listbox.curselection()
        font_name = self.font_listbox.get(selection[0]) if selection else "standard"

        if not text.strip(): result = "Awaiting input..."
        else:
            try: result = pyfiglet.Figlet(font=font_name).renderText(text)
            except Exception as e: result = f"Rendering error:\n{e}"

        self.text_preview_box.configure(state="normal")
        self.text_preview_box.delete("1.0", "end")
        self.text_preview_box.insert("1.0", result)
        self.text_preview_box.configure(state="disabled")

    # --- Logic: Image Generator ---
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.current_image_path = file_path
            filename = os.path.basename(file_path)
            self.img_label_status.configure(text=f"Loaded: {filename[:15]}...")
            self.generate_image_art()

    def update_image_art(self, value):
        self.res_label.configure(text=f"{int(value)} columns")
        if self.current_image_path:
            self.generate_image_art()

    def generate_image_art(self):
        if not self.current_image_path: return
        
        try:
            img = Image.open(self.current_image_path)
            new_width = int(self.res_slider.get())
            
            # Aspect ratio correction (characters are roughly twice as tall as they are wide)
            width, height = img.size
            aspect_ratio_correction = 0.55
            ratio = height / width * aspect_ratio_correction
            new_height = int(new_width * ratio)
            
            # Resize and convert to grayscale
            img = img.resize((new_width, new_height))
            img = img.convert("L")
            
            # Map pixels to characters
            pixels = img.getdata()
            # 256 color values / 10 characters = 25.6 range per char
            new_pixels = [ASCII_CHARS[pixel // 26] for pixel in pixels]
            new_pixels_string = "".join(new_pixels)
            
            # Format to image structure
            pixel_count = len(new_pixels_string)
            ascii_image = "\n".join([new_pixels_string[index:(index + new_width)] for index in range(0, pixel_count, new_width)])
            
            self.img_preview_box.configure(state="normal")
            self.img_preview_box.delete("1.0", "end")
            self.img_preview_box.insert("1.0", ascii_image)
            self.img_preview_box.configure(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Processing Error", f"Failed to process image:\n{e}")

    # --- Shared Functions ---
    def set_color(self, hex_color):
        self.current_color = hex_color
        self.text_preview_box.configure(text_color=self.current_color)
        self.img_preview_box.configure(text_color=self.current_color)

    def copy_to_clipboard(self, target_box):
        self.clipboard_clear()
        self.clipboard_append(target_box.get("1.0", "end-1c"))
        messagebox.showinfo("Copied", "Copied to clipboard!")

    def save_txt(self, target_box):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(target_box.get("1.0", "end-1c"))

    def save_image(self, target_box, is_image=False):
        text = target_box.get("1.0", "end-1c")
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if not path: return

        # Image ASCII requires a smaller font to export cleanly without massive file sizes
        font_size = 10 if is_image else 20
        try: font = ImageFont.truetype("cour.ttf", font_size)
        except: font = ImageFont.load_default()

        lines = text.split('\n')
        char_w = 6 if is_image else 12
        line_h = 10 if is_image else 20
        
        img_w = max(max((len(line) for line in lines), default=0) * char_w, 100)
        img_h = max(len(lines) * line_h, 100)

        img = Image.new('RGB', (img_w + 60, img_h + 60), color=BG_COLOR)
        draw = ImageDraw.Draw(img)
        draw.text((30, 30), text, fill=self.current_color, font=font)
        img.save(path)
        messagebox.showinfo("Success", "Render saved as Image!")

if __name__ == "__main__":
    app = FuturisticASCIIGenerator()
    app.mainloop()