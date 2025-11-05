"""
Script para criar ícone do Monitor de IPs
Tema: Matrix/Hacking - Monitoramento de Rede
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Cria o ícone do Monitor de IPs com tema Matrix/Hacking"""
    
    # Tamanhos do ícone (Windows precisa de múltiplos tamanhos)
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        # Cria imagem com fundo preto transparente
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Cores do tema Matrix/Hacking
        bg_color = (0, 0, 0, 255)  # Preto
        neon_green = (0, 255, 0, 255)  # Verde neon
        dark_green = (0, 200, 0, 255)  # Verde escuro
        accent = (0, 255, 100, 255)  # Verde claro
        
        # Preenche fundo (opcional - pode deixar transparente)
        # draw.rectangle([0, 0, size-1, size-1], fill=bg_color)
        
        # Desenha símbolo de rede/monitoramento
        # Base: círculo ou hexágono representando rede
        
        # Calcula proporções
        margin = size // 8
        center = size // 2
        radius = (size - margin * 2) // 2
        
        # Desenha círculo externo (representando rede)
        draw.ellipse(
            [center - radius, center - radius, 
             center + radius, center + radius],
            outline=neon_green,
            width=max(2, size // 16)
        )
        
        # Desenha círculo interno menor
        inner_radius = radius * 0.6
        draw.ellipse(
            [center - inner_radius, center - inner_radius,
             center + inner_radius, center + inner_radius],
            outline=dark_green,
            width=max(1, size // 32)
        )
        
        # Desenha pontos de conexão (4 pontos cardeais)
        point_size = max(2, size // 16)
        points = [
            (center, margin),  # Top
            (size - margin, center),  # Right
            (center, size - margin),  # Bottom
            (margin, center),  # Left
        ]
        
        for point in points:
            draw.ellipse(
                [point[0] - point_size, point[1] - point_size,
                 point[0] + point_size, point[1] + point_size],
                fill=neon_green
            )
        
        # Desenha linhas conectando os pontos (representando conexões de rede)
        line_width = max(1, size // 32)
        # Linha horizontal
        draw.line(
            [points[3][0], center, points[1][0], center],
            fill=dark_green,
            width=line_width
        )
        # Linha vertical
        draw.line(
            [center, points[0][1], center, points[2][1]],
            fill=dark_green,
            width=line_width
        )
        
        # Desenha "IP" ou números no centro (se o tamanho permitir)
        if size >= 32:
            try:
                # Tenta usar fonte padrão do sistema
                font_size = max(8, size // 4)
                # Usa fonte padrão do sistema
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    # Tenta fonte alternativa
                    font = ImageFont.truetype("calibri.ttf", font_size)
                except:
                    # Usa fonte padrão do PIL
                    font = ImageFont.load_default()
            
            # Desenha "IP" no centro
            if size >= 48:
                text = "IP"
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = center - text_width // 2
                text_y = center - text_height // 2
                
                # Desenha texto com sombra (glow effect)
                for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    draw.text(
                        (text_x + offset[0], text_y + offset[1]),
                        text,
                        fill=(0, 100, 0, 255),
                        font=font
                    )
                draw.text((text_x, text_y), text, fill=neon_green, font=font)
            else:
                # Para tamanhos menores, desenha apenas um ponto central
                point_center = max(2, size // 20)
                draw.ellipse(
                    [center - point_center, center - point_center,
                     center + point_center, center + point_center],
                    fill=accent
                )
        
        # Adiciona efeito de brilho nas bordas (opcional)
        if size >= 64:
            # Desenha círculo externo com brilho
            draw.ellipse(
                [center - radius - 1, center - radius - 1,
                 center + radius + 1, center + radius + 1],
                outline=accent,
                width=1
            )
        
        images.append(img)
    
    # Salva como .ico
    output_file = "icon.ico"
    images[0].save(
        output_file,
        format='ICO',
        sizes=[(img.width, img.height) for img in images]
    )
    
    print(f"Icone criado: {output_file}")
    print(f"  Tamanhos incluidos: {sizes}")
    return output_file


if __name__ == "__main__":
    import sys
    # Configura encoding para Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    try:
        create_icon()
        print("\n[OK] Icone gerado com sucesso!")
        print("  Arquivo: icon.ico")
        print("\n  Voce pode usar este icone no build.bat")
    except ImportError:
        print("[ERRO] PIL (Pillow) nao esta instalado.")
        print("\n  Instale com:")
        print("    pip install pillow")
    except Exception as e:
        print(f"[ERRO] Erro ao criar icone: {e}")

