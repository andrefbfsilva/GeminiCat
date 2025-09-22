"""
Gerador de sprites pixel art do gatinho
"""
from PIL import Image, ImageDraw
import os

def create_cat_sprites():
    """Criar sprites pixel art do gatinho"""
    
    # Criar pasta para sprites
    sprites_dir = "sprites"
    if not os.path.exists(sprites_dir):
        os.makedirs(sprites_dir)
    
    # Configurações
    size = 32
    scale = 2  # Para ficar visível
    final_size = size * scale
    
    # Cores do gatinho
    colors = {
        'body': '#FF69B4',      # Rosa
        'darker': '#E55A9B',    # Rosa escuro
        'white': '#FFFFFF',     # Branco
        'black': '#000000',     # Preto
        'eyes': '#00FF00',      # Verde
        'nose': '#FF1493'       # Rosa choque
    }
    
    def create_sprite(name, pixel_data):
        """Criar sprite a partir de dados de pixel"""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        
        for y, row in enumerate(pixel_data):
            for x, color_key in enumerate(row):
                if color_key and color_key in colors:
                    img.putpixel((x, y), hex_to_rgba(colors[color_key]))
        
        # Escalar para ficar visível
        img = img.resize((final_size, final_size), Image.NEAREST)
        img.save(f"{sprites_dir}/{name}.png")
        print(f"Sprite {name} criado")
        return img
    
    def hex_to_rgba(hex_color):
        """Converter hex para RGBA"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    
    # Sprite 1: Gatinho parado (idle)
    idle_pixels = [
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, 'body', 'body', 'body', 'body', 'body', 'body', None, None, None, None, None, None],
        [None, None, None, 'body', 'body', 'body', 'body', 'body', 'body', 'body', 'body', None, None, None, None, None],
        [None, None, 'body', 'body', 'white', 'black', 'body', 'body', 'black', 'white', 'body', 'body', None, None, None, None],
        [None, None, 'body', 'body', 'eyes', 'black', 'body', 'body', 'black', 'eyes', 'body', 'body', None, None, None, None],
        [None, None, 'body', 'body', 'body', 'body', 'nose', 'nose', 'body', 'body', 'body', 'body', None, None, None, None],
        [None, None, 'body', 'body', 'body', 'black', 'black', 'black', 'black', 'body', 'body', 'body', None, None, None, None],
        [None, None, None, 'body', 'body', 'body', 'body', 'body', 'body', 'body', 'body', None, None, None, None, None],
        [None, None, None, None, 'body', 'body', 'body', 'body', 'body', 'body', None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
    ]
    
    # Sprite 2: Gatinho feliz (happy)
    happy_pixels = [
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, 'body', 'body', 'body', 'body', 'body', 'body', None, None, None, None, None, None],
        [None, None, None, 'body', 'body', 'body', 'body', 'body', 'body', 'body', 'body', None, None, None, None, None],
        [None, None, 'body', 'body', 'white', 'black', 'body', 'body', 'black', 'white', 'body', 'body', None, None, None, None],
        [None, None, 'body', 'body', 'black', 'eyes', 'body', 'body', 'eyes', 'black', 'body', 'body', None, None, None, None],
        [None, None, 'body', 'body', 'body', 'body', 'nose', 'nose', 'body', 'body', 'body', 'body', None, None, None, None],
        [None, None, 'body', 'body', 'black', 'body', 'black', 'black', 'body', 'black', 'body', 'body', None, None, None, None],
        [None, None, None, 'body', 'body', 'black', 'black', 'black', 'black', 'body', 'body', None, None, None, None, None],
        [None, None, None, None, 'body', 'body', 'body', 'body', 'body', 'body', None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
    ]
    
    # Sprite 3: Gatinho dormindo (sleep)
    sleep_pixels = [
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, 'body', 'body', 'body', 'body', 'body', 'body', None, None, None, None, None, None],
        [None, None, None, 'body', 'body', 'body', 'body', 'body', 'body', 'body', 'body', None, None, None, None, None],
        [None, None, 'body', 'body', 'white', 'white', 'body', 'body', 'white', 'white', 'body', 'body', None, None, None, None],
        [None, None, 'body', 'body', 'black', 'black', 'body', 'body', 'black', 'black', 'body', 'body', None, None, None, None],
        [None, None, 'body', 'body', 'body', 'body', 'nose', 'nose', 'body', 'body', 'body', 'body', None, None, None, None],
        [None, None, 'body', 'body', 'body', 'body', 'black', 'black', 'body', 'body', 'body', 'body', None, None, None, None],
        [None, None, None, 'body', 'body', 'body', 'body', 'body', 'body', 'body', 'body', None, None, None, None, None],
        [None, None, None, None, 'body', 'body', 'body', 'body', 'body', 'body', None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
    ]
    
    # Criar sprites
    sprites = {}
    sprites['idle'] = create_sprite('cat_idle', idle_pixels)
    sprites['happy'] = create_sprite('cat_happy', happy_pixels)
    sprites['sleep'] = create_sprite('cat_sleep', sleep_pixels)
    
    return sprites

if __name__ == "__main__":
    print("Criando sprites do gatinho...")
    try:
        sprites = create_cat_sprites()
        print("Sprites criados com sucesso!")
        print("Arquivos salvos na pasta 'sprites/'")
    except Exception as e:
        print(f"Erro ao criar sprites: {e}")
        print("Instalando Pillow...")
        import subprocess
        subprocess.run(["pip", "install", "Pillow"])
        print("Tente executar novamente")