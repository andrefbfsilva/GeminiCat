from PIL import Image, ImageDraw
import os
import math

def create_sprites_directory():
    if not os.path.exists('sprites_hd'):
        os.makedirs('sprites_hd')

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (255,)

def draw_smooth_ellipse(draw, bbox, fill_color, outline_color, outline_width=2):
    draw.ellipse(bbox, fill=fill_color, outline=outline_color, width=outline_width)

def draw_cat_sitting(draw, colors, y_offset=0):
    base, shadow, light = colors['base'], colors['shadow'], colors['light']
    outline = hex_to_rgb('#5C4A3A')
    
    # SOMBRA NO CHÃO
    shadow_floor = (0, 0, 0, 60)
    draw.ellipse([30, 100+y_offset, 98, 115+y_offset], fill=shadow_floor)
    
    # CORPO (oval sentado)
    body_x, body_y = 64, 70+y_offset
    draw.ellipse([body_x-28, body_y-20, body_x+28, body_y+25], fill=base, outline=outline, width=2)
    
    # Sombreamento do corpo (lado direito)
    draw.ellipse([body_x+8, body_y-18, body_x+26, body_y+23], fill=shadow)
    
    # Luz do corpo (lado esquerdo)
    draw.ellipse([body_x-26, body_y-18, body_x-8, body_y+23], fill=light)
    
    # PATAS TRASEIRAS (parcialmente visíveis)
    draw.ellipse([42, 80+y_offset, 56, 100+y_offset], fill=shadow, outline=outline, width=1)
    draw.ellipse([72, 80+y_offset, 86, 100+y_offset], fill=shadow, outline=outline, width=1)
    
    # PATAS FRONTAIS (visíveis, sentadas)
    draw.ellipse([48, 85+y_offset, 60, 105+y_offset], fill=base, outline=outline, width=2)
    draw.ellipse([68, 85+y_offset, 80, 105+y_offset], fill=base, outline=outline, width=2)
    
    # Dedos das patas (detalhes)
    toe_color = shadow
    draw.ellipse([50, 98+y_offset, 53, 102+y_offset], fill=toe_color)
    draw.ellipse([55, 98+y_offset, 58, 102+y_offset], fill=toe_color)
    draw.ellipse([70, 98+y_offset, 73, 102+y_offset], fill=toe_color)
    draw.ellipse([75, 98+y_offset, 78, 102+y_offset], fill=toe_color)
    
    # CAUDA (enrolada ao lado)
    tail_points = [
        (88, 75+y_offset), (95, 70+y_offset), (100, 68+y_offset), 
        (105, 70+y_offset), (108, 75+y_offset), (105, 80+y_offset),
        (98, 78+y_offset), (92, 78+y_offset)
    ]
    draw.polygon(tail_points, fill=base, outline=outline)
    
    # Sombreamento da cauda
    draw.polygon([(100, 70+y_offset), (105, 72+y_offset), (106, 76+y_offset), (102, 76+y_offset)], fill=shadow)
    
    # CABEÇA (grande e redonda)
    head_x, head_y = 64, 42+y_offset
    draw.ellipse([head_x-24, head_y-22, head_x+24, head_y+22], fill=base, outline=outline, width=2)
    
    # Sombreamento da cabeça (direita)
    draw.ellipse([head_x+6, head_y-20, head_x+22, head_y+20], fill=shadow)
    
    # Luz da cabeça (esquerda)
    draw.ellipse([head_x-22, head_y-20, head_x-6, head_y+20], fill=light)
    
    # ORELHAS
    ear_left = [(head_x-18, head_y-18), (head_x-22, head_y-28), (head_x-10, head_y-22)]
    ear_right = [(head_x+18, head_y-18), (head_x+22, head_y-28), (head_x+10, head_y-22)]
    draw.polygon(ear_left, fill=base, outline=outline)
    draw.polygon(ear_right, fill=base, outline=outline)
    
    # Interior das orelhas
    draw.polygon([(head_x-16, head_y-20), (head_x-18, head_y-25), (head_x-12, head_y-22)], fill=shadow)
    draw.polygon([(head_x+16, head_y-20), (head_x+18, head_y-25), (head_x+12, head_y-22)], fill=shadow)
    
    # OLHOS GRANDES
    eye_white = (255, 255, 255, 255)
    eye_pupil = (0, 0, 0, 255)
    eye_shine = (255, 255, 255, 200)
    
    # Olho esquerdo
    draw.ellipse([head_x-16, head_y-8, head_x-4, head_y+8], fill=eye_white, outline=outline, width=1)
    draw.ellipse([head_x-13, head_y-2, head_x-7, head_y+6], fill=eye_pupil)
    draw.ellipse([head_x-12, head_y-1, head_x-9, head_y+2], fill=eye_shine)
    
    # Olho direito
    draw.ellipse([head_x+4, head_y-8, head_x+16, head_y+8], fill=eye_white, outline=outline, width=1)
    draw.ellipse([head_x+7, head_y-2, head_x+13, head_y+6], fill=eye_pupil)
    draw.ellipse([head_x+9, head_y-1, head_x+12, head_y+2], fill=eye_shine)
    
    # NARIZ
    nose_color = hex_to_rgb('#FF9999')
    draw.polygon([(head_x, head_y+6), (head_x-3, head_y+10), (head_x+3, head_y+10)], fill=nose_color, outline=outline)
    
    # BOCA
    draw.arc([head_x-6, head_y+8, head_x-2, head_y+14], start=0, end=180, fill=outline, width=1)
    draw.arc([head_x+2, head_y+8, head_x+6, head_y+14], start=0, end=180, fill=outline, width=1)

def create_walk_frame(colors, frame_num, total_frames=6):
    img = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    base, shadow, light = colors['base'], colors['shadow'], colors['light']
    outline = hex_to_rgb('#5C4A3A')
    
    # Calcular offset de animação
    bounce = int(math.sin(frame_num * math.pi / total_frames) * 3)
    tail_swing = int(math.sin(frame_num * 2 * math.pi / total_frames) * 8)
    
    # SOMBRA NO CHÃO
    shadow_floor = (0, 0, 0, 60)
    draw.ellipse([30, 100, 98, 115], fill=shadow_floor)
    
    # CORPO
    body_x, body_y = 64, 65 + bounce
    draw.ellipse([body_x-28, body_y-18, body_x+28, body_y+22], fill=base, outline=outline, width=2)
    draw.ellipse([body_x+8, body_y-16, body_x+26, body_y+20], fill=shadow)
    draw.ellipse([body_x-26, body_y-16, body_x-8, body_y+20], fill=light)
    
    # PATAS (alternando)
    paw_offset_l = 5 if frame_num % 2 == 0 else -5
    paw_offset_r = -5 if frame_num % 2 == 0 else 5
    
    # Patas traseiras
    draw.ellipse([42, 75, 54, 95+paw_offset_l], fill=shadow, outline=outline, width=1)
    draw.ellipse([74, 75, 86, 95+paw_offset_r], fill=shadow, outline=outline, width=1)
    
    # Patas frontais
    draw.ellipse([50, 78, 60, 100+paw_offset_r], fill=base, outline=outline, width=2)
    draw.ellipse([68, 78, 78, 100+paw_offset_l], fill=base, outline=outline, width=2)
    
    # CAUDA (balançando)
    tail_x = 90 + tail_swing
    tail_points = [
        (88, 70), (tail_x, 65), (tail_x+8, 63), 
        (tail_x+10, 68), (tail_x+8, 73), (tail_x, 71), (92, 73)
    ]
    draw.polygon(tail_points, fill=base, outline=outline)
    draw.polygon([(tail_x+2, 66), (tail_x+8, 68), (tail_x+7, 71), (tail_x+3, 70)], fill=shadow)
    
    # CABEÇA
    head_x, head_y = 64, 37 + bounce
    draw.ellipse([head_x-24, head_y-22, head_x+24, head_y+22], fill=base, outline=outline, width=2)
    draw.ellipse([head_x+6, head_y-20, head_x+22, head_y+20], fill=shadow)
    draw.ellipse([head_x-22, head_y-20, head_x-6, head_y+20], fill=light)
    
    # ORELHAS
    ear_left = [(head_x-18, head_y-18), (head_x-22, head_y-28), (head_x-10, head_y-22)]
    ear_right = [(head_x+18, head_y-18), (head_x+22, head_y-28), (head_x+10, head_y-22)]
    draw.polygon(ear_left, fill=base, outline=outline)
    draw.polygon(ear_right, fill=base, outline=outline)
    draw.polygon([(head_x-16, head_y-20), (head_x-18, head_y-25), (head_x-12, head_y-22)], fill=shadow)
    draw.polygon([(head_x+16, head_y-20), (head_x+18, head_y-25), (head_x+12, head_y-22)], fill=shadow)
    
    # OLHOS
    eye_white = (255, 255, 255, 255)
    eye_pupil = (0, 0, 0, 255)
    eye_shine = (255, 255, 255, 200)
    
    draw.ellipse([head_x-16, head_y-8, head_x-4, head_y+8], fill=eye_white, outline=outline, width=1)
    draw.ellipse([head_x-13, head_y-2, head_x-7, head_y+6], fill=eye_pupil)
    draw.ellipse([head_x-12, head_y-1, head_x-9, head_y+2], fill=eye_shine)
    
    draw.ellipse([head_x+4, head_y-8, head_x+16, head_y+8], fill=eye_white, outline=outline, width=1)
    draw.ellipse([head_x+7, head_y-2, head_x+13, head_y+6], fill=eye_pupil)
    draw.ellipse([head_x+9, head_y-1, head_x+12, head_y+2], fill=eye_shine)
    
    # NARIZ E BOCA
    nose_color = hex_to_rgb('#FF9999')
    draw.polygon([(head_x, head_y+6), (head_x-3, head_y+10), (head_x+3, head_y+10)], fill=nose_color, outline=outline)
    draw.arc([head_x-6, head_y+8, head_x-2, head_y+14], start=0, end=180, fill=outline, width=1)
    draw.arc([head_x+2, head_y+8, head_x+6, head_y+14], start=0, end=180, fill=outline, width=1)
    
    return img

def create_static_sitting(colors):
    img = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_cat_sitting(draw, colors)
    return img

def get_color_palettes():
    return {
        'orange': {
            'base': hex_to_rgb('#FF8C42'),
            'shadow': hex_to_rgb('#D65F20'),
            'light': hex_to_rgb('#FFB570')
        },
        'tabby': {
            'base': hex_to_rgb('#8B7355'),
            'shadow': hex_to_rgb('#5C4A3A'),
            'light': hex_to_rgb('#B39C7E')
        },
        'siamese': {
            'base': hex_to_rgb('#FFF8DC'),
            'shadow': hex_to_rgb('#E6D7B8'),
            'light': hex_to_rgb('#FFFFF0')
        },
        'tuxedo': {
            'base': hex_to_rgb('#2C2C2C'),
            'shadow': hex_to_rgb('#1A1A1A'),
            'light': hex_to_rgb('#404040')
        }
    }

def add_siamese_points(img, colors):
    pixels = img.load()
    point_color = hex_to_rgb('#8B4513')
    
    # Escurecer orelhas
    for y in range(10, 30):
        for x in range(20, 108):
            if pixels[x, y][3] > 0 and y < 25:
                r, g, b, a = pixels[x, y]
                if r > 200:
                    pixels[x, y] = point_color
    
    # Escurecer cauda
    for y in range(63, 80):
        for x in range(85, 115):
            if pixels[x, y][3] > 0:
                pixels[x, y] = point_color

def add_tuxedo_markings(img):
    pixels = img.load()
    white = (255, 255, 255, 255)
    
    # Peito branco
    for y in range(60, 95):
        for x in range(50, 78):
            if pixels[x, y][3] > 0:
                pixels[x, y] = white
    
    # Patas brancas
    for y in range(85, 105):
        for x in range(48, 80):
            if pixels[x, y][3] > 0:
                pixels[x, y] = white

def add_tabby_stripes(img, colors):
    pixels = img.load()
    stripe_color = colors['shadow']
    
    # Listras verticais na cabeça e corpo
    for x in [50, 58, 70, 78]:
        for y in range(25, 85):
            if pixels[x, y][3] > 0:
                pixels[x, y] = stripe_color

def main():
    print("Gerando sprites HD 128x128 estilo Stardew Valley...")
    create_sprites_directory()
    
    palettes = get_color_palettes()
    
    # Gerar sprites estáticos primeiro
    print("\n=== SPRITES ESTÁTICOS (SENTADOS) ===")
    for breed, colors in palettes.items():
        print(f"Gerando {breed} static...")
        img = create_static_sitting(colors)
        
        # Aplicar marcações especiais
        if breed == 'siamese':
            add_siamese_points(img, colors)
        elif breed == 'tuxedo':
            add_tuxedo_markings(img)
        elif breed == 'tabby':
            add_tabby_stripes(img, colors)
        
        img.save(f'sprites_hd/{breed}_sit.png')
        print(f"  OK sprites_hd/{breed}_sit.png")
    
    # Gerar animações de caminhada
    print("\n=== ANIMAÇÕES DE CAMINHADA (6 FRAMES) ===")
    for breed, colors in palettes.items():
        print(f"Gerando {breed} walk animation...")
        for frame in range(6):
            img = create_walk_frame(colors, frame, total_frames=6)
            
            # Aplicar marcações especiais
            if breed == 'siamese':
                add_siamese_points(img, colors)
            elif breed == 'tuxedo':
                add_tuxedo_markings(img)
            elif breed == 'tabby':
                add_tabby_stripes(img, colors)
            
            img.save(f'sprites_hd/{breed}_walk_{frame}.png')
            print(f"  OK sprites_hd/{breed}_walk_{frame}.png")
    
    print("\nOK Todos os sprites HD gerados com sucesso!")
    print(f"  - 4 sprites estáticos (sitting)")
    print(f"  - 24 frames de animação (6 por gato)")

if __name__ == "__main__":
    main()