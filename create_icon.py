#!/usr/bin/env python3
"""
Script para criar um ícone simples para o SevenX Studio
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_icon():
        # Criar imagem 256x256
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Fundo gradiente azul
        for i in range(size):
            alpha = int(255 * (1 - i / size))
            color = (0, 120, 212, alpha)
            draw.rectangle([0, i, size, i+1], fill=color)
        
        # Círculo central
        circle_size = size // 2
        circle_pos = (size // 4, size // 4)
        draw.ellipse([circle_pos[0], circle_pos[1], 
                     circle_pos[0] + circle_size, circle_pos[1] + circle_size], 
                    fill=(255, 255, 255, 200), outline=(0, 120, 212, 255), width=4)
        
        # Texto "7X"
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        text = "7X"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2 - 10
        
        draw.text((text_x, text_y), text, fill=(0, 120, 212, 255), font=font)
        
        # Salvar como ICO
        os.makedirs('assets', exist_ok=True)
        
        # Criar múltiplos tamanhos para o ICO
        sizes = [16, 32, 48, 64, 128, 256]
        images = []
        
        for s in sizes:
            resized = img.resize((s, s), Image.Resampling.LANCZOS)
            images.append(resized)
        
        # Salvar como ICO
        img.save('assets/icon.ico', format='ICO', sizes=[(s, s) for s in sizes])
        print("Ícone criado com sucesso: assets/icon.ico")
        
        # Salvar também como PNG
        img.save('assets/icon.png', format='PNG')
        print("Ícone PNG criado: assets/icon.png")
        
    if __name__ == "__main__":
        create_icon()
        
except ImportError:
    print("PIL (Pillow) não encontrado. Instalando...")
    import subprocess
    subprocess.run(["pip", "install", "Pillow"])
    
    # Tentar novamente
    try:
        from PIL import Image, ImageDraw, ImageFont
        create_icon()
    except:
        print("Erro ao criar ícone. Usando ícone padrão.")
        
        # Criar arquivo vazio como fallback
        os.makedirs('assets', exist_ok=True)
        with open('assets/icon.ico', 'w') as f:
            f.write("# Placeholder icon")