"""
GeminiCat - Assistente Virtual com Sprites e Gemini AI
"""
import tkinter as tk
import sys
import random
import time
import os
from PIL import Image, ImageTk

class CatPet:
    def __init__(self, window):
        self.window = window
        self.size = 64
        
        # Estado do pet
        self.vx = 0
        self.vy = 0
        self.state = 'idle'
        self.mood = 'idle'
        self.last_interaction = time.time()
        
        # Carregar sprites
        self.sprites = self.load_sprites()
        
        # Canvas
        self.canvas = tk.Canvas(
            window,
            width=self.size,
            height=self.size,
            bg="white" if hasattr(window, 'winfo_rgb') and window.cget('bg') == 'lightgray' else "black",
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Pet sprite
        self.pet_sprite = None
        self.update_sprite()
        
        # Bindings
        self.canvas.bind('<Button-1>', self.on_left_click)
        self.canvas.bind('<Button-3>', self.on_right_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        
        # Iniciar comportamentos
        self.update_position()
        self.random_behavior()
        self.mood_check()
        
        print("GeminiCat criado com sprites!")
    
    def load_sprites(self):
        """Carregar sprites do gatinho"""
        sprites = {}
        sprites_dir = "sprites"
        
        if os.path.exists(sprites_dir):
            try:
                for sprite_name in ['cat_idle', 'cat_happy', 'cat_sleep']:
                    sprite_path = os.path.join(sprites_dir, f"{sprite_name}.png")
                    if os.path.exists(sprite_path):
                        img = Image.open(sprite_path)
                        sprites[sprite_name] = ImageTk.PhotoImage(img)
                        print(f"Sprite {sprite_name} carregado")
                    else:
                        print(f"Sprite {sprite_name} não encontrado")
            except Exception as e:
                print(f"Erro ao carregar sprites: {e}")
        
        # Fallback: criar sprites simples se não encontrar arquivos
        if not sprites:
            print("Usando sprites de fallback")
            sprites = self.create_fallback_sprites()
        
        return sprites
    
    def create_fallback_sprites(self):
        """Criar sprites simples como fallback"""
        sprites = {}
        
        # Criar imagens simples coloridas
        for name, color in [('cat_idle', 'hotpink'), ('cat_happy', 'yellow'), ('cat_sleep', 'lightblue')]:
            img = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # Desenhar gatinho simples
            draw.ellipse([10, 10, 54, 54], fill=color)  # Corpo
            draw.ellipse([20, 20, 30, 30], fill='black')  # Olho esquerdo
            draw.ellipse([34, 20, 44, 30], fill='black')  # Olho direito
            draw.ellipse([30, 35, 34, 39], fill='pink')   # Nariz
            
            sprites[name] = ImageTk.PhotoImage(img)
        
        return sprites
    
    def update_sprite(self):
        """Atualizar sprite do gatinho baseado no mood"""
        sprite_name = f"cat_{self.mood}"
        
        if sprite_name in self.sprites:
            if self.pet_sprite:
                self.canvas.delete(self.pet_sprite)
            
            self.pet_sprite = self.canvas.create_image(
                self.size // 2, self.size // 2,
                image=self.sprites[sprite_name]
            )
        else:
            print(f"Sprite {sprite_name} não encontrado")
    
    def on_left_click(self, event):
        """GeminiCat fica feliz quando clicado"""
        print("GeminiCat feliz!")
        self.mood = 'happy'
        self.last_interaction = time.time()
        self.update_sprite()
        
        # Voltar ao normal após um tempo
        self.window.after(2000, self.reset_mood)
    
    def on_right_click(self, event):
        """Abrir chat com Gemini"""
        print("Chat com GeminiCat")
        try:
            from gemini_chat_real import open_gemini_chat
            open_gemini_chat(self.window)
        except ImportError:
            # Fallback para chat simples
            self.open_simple_chat()
    
    def open_simple_chat(self):
        """Chat simples como fallback"""
        chat_window = tk.Toplevel(self.window)
        chat_window.title("Chat com GeminiCat")
        chat_window.geometry("400x300+400+400")
        
        text_area = tk.Text(chat_window, height=15, width=50)
        text_area.pack(padx=10, pady=10)
        text_area.insert("1.0", "Olá! Sou o GeminiCat!\n\nO chat completo com Gemini está disponível.\nEste é apenas um modo de fallback.\n\nFecha e tenta novamente!")
        text_area.config(state="disabled")
        
        btn = tk.Button(chat_window, text="Fechar", command=chat_window.destroy)
        btn.pack(pady=5)
    
    def on_drag(self, event):
        """Arrastar o GeminiCat"""
        try:
            x = self.window.winfo_pointerx() - self.size//2
            y = self.window.winfo_pointery() - self.size//2
            self.window.geometry(f'{self.size}x{self.size}+{x}+{y}')
            self.last_interaction = time.time()
        except Exception as e:
            print(f"Erro no drag: {e}")
    
    def reset_mood(self):
        """Resetar humor do GeminiCat"""
        if self.mood == 'happy':
            self.mood = 'idle'
            self.update_sprite()
    
    def mood_check(self):
        """Verificar se o GeminiCat deve dormir"""
        time_since_interaction = time.time() - self.last_interaction
        
        if time_since_interaction > 30 and self.mood != 'sleep':  # 30 segundos sem interação
            self.mood = 'sleep'
            self.vx = 0  # Parar movimento
            self.vy = 0
            self.update_sprite()
            print("GeminiCat dormindo...")
        elif time_since_interaction <= 5 and self.mood == 'sleep':
            self.mood = 'idle'
            self.update_sprite()
            print("GeminiCat acordou!")
        
        # Verificar novamente em 5 segundos
        self.window.after(5000, self.mood_check)
    
    def random_behavior(self):
        """Comportamento aleatório do GeminiCat"""
        if self.mood != 'sleep':
            behaviors = ['idle', 'move_left', 'move_right', 'move_up', 'move_down', 'wander']
            self.state = random.choice(behaviors)
            
            if self.state == 'move_left':
                self.vx, self.vy = -1, 0
            elif self.state == 'move_right':
                self.vx, self.vy = 1, 0
            elif self.state == 'move_up':
                self.vx, self.vy = 0, -1
            elif self.state == 'move_down':
                self.vx, self.vy = 0, 1
            elif self.state == 'wander':
                self.vx = random.randint(-1, 1)
                self.vy = random.randint(-1, 1)
            else:
                self.vx, self.vy = 0, 0
        
        next_time = random.randint(3000, 8000)
        self.window.after(next_time, self.random_behavior)
    
    def update_position(self):
        """Atualizar posição do GeminiCat"""
        if self.mood != 'sleep':
            try:
                screen_width = self.window.winfo_screenwidth()
                screen_height = self.window.winfo_screenheight()
                
                geometry = self.window.geometry()
                parts = geometry.split('+')
                if len(parts) >= 3:
                    current_x = int(parts[1])
                    current_y = int(parts[2])
                    
                    new_x = current_x + self.vx
                    new_y = current_y + self.vy
                    
                    # Verificar limites
                    if new_x <= 0 or new_x >= screen_width - self.size:
                        self.vx = -self.vx
                        new_x = max(0, min(new_x, screen_width - self.size))
                    
                    if new_y <= 0 or new_y >= screen_height - self.size - 40:
                        self.vy = -self.vy
                        new_y = max(0, min(new_y, screen_height - self.size - 40))
                    
                    # Mover janela
                    self.window.geometry(f'{self.size}x{self.size}+{new_x}+{new_y}')
            
            except Exception as e:
                print(f"Erro no movimento: {e}")
        
        self.window.after(100, self.update_position)

class CatDesktopApp:
    def __init__(self):
        self.window = tk.Tk()
        self.setup_window()
        self.pet = CatPet(self.window)
    
    def setup_window(self):
        """Configurar janela do GeminiCat"""
        print("Configurando janela do GeminiCat...")
        
        self.window.title("GeminiCat")
        self.window.wm_attributes('-topmost', True)
        
        # Tentar transparência
        transparency_mode = False
        try:
            self.window.overrideredirect(True)
            self.window.wm_attributes('-transparentcolor', "black")
            self.window.geometry("64x64+300+300")
            transparency_mode = True
            print("Modo transparente ativado")
        except Exception as e:
            print(f"Transparência não funcionou: {e}")
            transparency_mode = False
        
        if not transparency_mode:
            print("Usando modo visível")
            self.window.overrideredirect(False)
            self.window.configure(bg="lightgray")
            self.window.geometry("84x104+300+300")
        
        # ESC para sair
        self.window.bind('<Escape>', lambda e: self.quit())
        self.window.focus_set()
    
    def quit(self):
        print("Adeus! Miau!")
        self.window.quit()
        sys.exit()
    
    def run(self):
        print("GeminiCat iniciado!")
        print("Controles:")
        print("  - Clique esquerdo: deixar feliz")
        print("  - Clique direito: chat")
        print("  - Arrastar: mover GeminiCat")
        print("  - ESC: sair")
        print("  - GeminiCat dorme se não interagir por 30s")
        
        try:
            self.window.mainloop()
        except KeyboardInterrupt:
            self.quit()

if __name__ == "__main__":
    try:
        app = CatDesktopApp()
        app.run()
    except Exception as e:
        print(f"Erro ao iniciar: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")