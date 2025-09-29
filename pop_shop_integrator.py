from PIL import Image
import os

def analyze_spritesheet(image_path):
    img = Image.open(image_path)
    width, height = img.size
    print(f"Spritesheet: {os.path.basename(image_path)}")
    print(f"  Dimensions: {width}x{height}")
    
    # Detectar tamanho do sprite individual (primeira linha parece ter frames individuais)
    # Assumindo grid regular, vamos testar 32x32
    sprite_size = 32
    cols = width // sprite_size
    rows = height // sprite_size
    print(f"  Estimated grid: {cols}x{rows} (sprite size: {sprite_size}x{sprite_size})")
    return img, sprite_size

def extract_walk_frames(spritesheet, sprite_size, row_index, start_col, num_frames):
    """Extrair frames de caminhada de uma spritesheet"""
    frames = []
    for i in range(num_frames):
        col = start_col + i
        x = col * sprite_size
        y = row_index * sprite_size
        
        frame = spritesheet.crop((x, y, x + sprite_size, y + sprite_size))
        frames.append(frame)
    
    return frames

def scale_and_save_frames(frames, breed_name, output_dir='sprites_hd'):
    """Escalar frames para 128x128 e guardar"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Sprite sentado (usar primeiro frame)
    sit_frame = frames[0].resize((128, 128), Image.NEAREST)
    sit_frame.save(f'{output_dir}/{breed_name}_sit.png')
    print(f"  Saved: {breed_name}_sit.png")
    
    # Frames de caminhada (repetir para ter 6 frames)
    walk_frames = frames[:6] if len(frames) >= 6 else frames * 2
    walk_frames = walk_frames[:6]
    
    for i, frame in enumerate(walk_frames):
        scaled = frame.resize((128, 128), Image.NEAREST)
        scaled.save(f'{output_dir}/{breed_name}_walk_{i}.png')
        print(f"  Saved: {breed_name}_walk_{i}.png")

def map_breed_colors():
    """Mapear cores do Pop Shop para as 4 raças"""
    return {
        'orange': ['orange_0.png', 'orange_1.png', 'orange_2.png'],
        'tuxedo': ['black_0.png', 'black_1.png'],
        'siamese': ['seal_point_0.png', 'creme_0.png'],
        'tabby': ['grey_0.png', 'grey_1.png', 'brown_0.png']
    }

def integrate_pop_shop_cats():
    base_path = 'pop_shop_cats/Cats Download'
    
    # Mapear raças para ficheiros disponíveis
    breed_files = {
        'orange': 'orange_0.png',
        'tuxedo': 'black_0.png', 
        'siamese': 'seal_point_0.png',
        'tabby': 'grey_0.png',
        'tortie': 'calico_0.png',
        'calico': 'white_grey_0.png'
    }
    
    print("=== POP SHOP CATS INTEGRATION ===\n")
    
    for breed, filename in breed_files.items():
        filepath = os.path.join(base_path, filename)
        
        if not os.path.exists(filepath):
            print(f"SKIP: {filename} not found")
            continue
        
        print(f"\nProcessing {breed} ({filename})...")
        
        # Analisar spritesheet
        spritesheet, sprite_size = analyze_spritesheet(filepath)
        
        # Extrair frames de caminhada
        # WALKING está na linha que contém animação horizontal
        # Baseado na imagem: linha 4 parece ter walking frames (índice 4)
        walk_row = 4
        walk_start_col = 0
        num_frames = 6
        
        frames = extract_walk_frames(spritesheet, sprite_size, walk_row, walk_start_col, num_frames)
        
        # Escalar e guardar
        scale_and_save_frames(frames, breed)
    
    print("\n=== INTEGRATION COMPLETE ===")
    print("All Pop Shop Cats sprites converted to 128x128")
    print("Saved in sprites_hd/ folder")
    print("Compatible with existing GeminiCat HD system")

if __name__ == "__main__":
    integrate_pop_shop_cats()