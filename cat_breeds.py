"""
Sistema simples de 4 raças de gatos
"""
from PIL import Image, ImageDraw
import os

class CatBreedSystem:
    def __init__(self):
        self.breeds = {
            'pink': {
                'name': 'GeminiCat Rosa',
                'body': (255, 182, 193),
                'eyes': (0, 255, 0)
            },
            'tuxedo': {
                'name': 'Gato Tuxedo',
                'body': (20, 20, 20),
                'chest': (255, 255, 255),
                'eyes': (50, 205, 50)
            },
            'orange': {
                'name': 'Gato Laranja',
                'body': (255, 140, 0),
                'eyes': (255, 215, 0)
            },
            'siamese': {
                'name': 'Gato Siamês',
                'body': (255, 248, 220),
                'points': (101, 67, 33),
                'eyes': (30, 144, 255)
            }
        }
    
    def generate_cat_sprite(self, breed_name, state='idle'):
        """Gerar sprite 64x64 para uma raça"""
        if breed_name not in self.breeds:
            breed_name = 'pink'
        
        breed = self.breeds[breed_name]
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if breed_name == 'tuxedo':
            # Corpo preto
            draw.ellipse([18, 28, 46, 56], fill=breed['body'])
            draw.ellipse([22, 10, 42, 30], fill=breed['body'])
            
            # Peito branco V
            draw.polygon([(28, 35), (32, 45), (36, 35)], fill=breed['chest'])
            
            # Patas brancas
            draw.ellipse([22, 52, 28, 58], fill=breed['chest'])
            draw.ellipse([36, 52, 42, 58], fill=breed['chest'])
            
        elif breed_name == 'siamese':
            # Corpo creme
            draw.ellipse([18, 28, 46, 56], fill=breed['body'])
            draw.ellipse([22, 10, 42, 30], fill=breed['body'])
            
            # Pontos escuros (cara, orelhas, patas)
            draw.ellipse([26, 14, 38, 26], fill=breed['points'])
            draw.polygon([(20, 12), (16, 4), (24, 8)], fill=breed['points'])
            draw.polygon([(44, 12), (48, 4), (40, 8)], fill=breed['points'])
            draw.ellipse([22, 52, 28, 58], fill=breed['points'])
            draw.ellipse([36, 52, 42, 58], fill=breed['points'])
            
        else:  # pink e orange usam formato simples
            # Corpo
            draw.ellipse([18, 28, 46, 56], fill=breed['body'])
            # Cabeça
            draw.ellipse([22, 10, 42, 30], fill=breed['body'])
            # Orelhas
            draw.polygon([(20, 12), (16, 4), (24, 8)], fill=breed['body'])
            draw.polygon([(44, 12), (48, 4), (40, 8)], fill=breed['body'])
            # Patas
            draw.ellipse([22, 52, 28, 58], fill=breed['body'])
            draw.ellipse([36, 52, 42, 58], fill=breed['body'])
        
        # Olhos (comum a todos)
        eye_color = breed['eyes']
        if state == 'sleep':
            # Olhos fechados
            draw.line([(26, 18), (30, 18)], fill=(0, 0, 0), width=1)
            draw.line([(34, 18), (38, 18)], fill=(0, 0, 0), width=1)
        else:
            # Olhos abertos
            draw.ellipse([26, 16, 30, 20], fill=(255, 255, 255))
            draw.ellipse([34, 16, 38, 20], fill=(255, 255, 255))
            draw.ellipse([27, 17, 29, 19], fill=eye_color)
            draw.ellipse([35, 17, 37, 19], fill=eye_color)
        
        # Nariz (rosa para todos)
        draw.polygon([(32, 22), (30, 24), (34, 24)], fill=(255, 192, 203))
        
        # Boca
        if state == 'happy':
            # Sorriso
            draw.arc([28, 24, 36, 28], 0, 180, fill=(0, 0, 0))
        else:
            # Boca normal
            draw.line([(32, 24), (30, 26)], fill=(0, 0, 0))
            draw.line([(32, 24), (34, 26)], fill=(0, 0, 0))
        
        # Bigodes
        draw.line([(10, 20), (22, 22)], fill=(0, 0, 0), width=1)
        draw.line([(42, 22), (54, 20)], fill=(0, 0, 0), width=1)
        
        # Cauda
        draw.arc([42, 35, 58, 50], 180, 270, fill=breed['body'], width=6)
        
        return img
    
    def generate_all_breeds(self):
        """Gerar sprites para todas as raças e estados"""
        os.makedirs('sprites', exist_ok=True)
        
        for breed_name in self.breeds.keys():
            breed_dir = f'sprites/{breed_name}'
            os.makedirs(breed_dir, exist_ok=True)
            
            for state in ['idle', 'happy', 'sleep']:
                sprite = self.generate_cat_sprite(breed_name, state)
                sprite.save(f'{breed_dir}/cat_{state}.png')
                print(f"OK Gerado {breed_name}/cat_{state}.png")

if __name__ == "__main__":
    print("Gerando sprites das 4 raças...")
    system = CatBreedSystem()
    system.generate_all_breeds()
    print("Completo!")