# GeminiCat - Assistente Virtual com Sprites e Gemini AI

## O que é
Assistente virtual com sprites pixel art no desktop que conversa com Google Gemini.

**REGRAS DE DOCUMENTAÇÃO:**
- Documentação SEM emojis
- Texto simples e sucinto
- READMEs curtos, informativos apenas do presente
- Sem roadmaps ou funcionalidades não implementadas
- Focar no que existe agora

**IMPORTANTE PARA CLAUDE CODE:**
- Use filosofia KISS (Keep It Simple)
- Não criar roadmaps extensos
- Não inventar funcionalidades complexas
- Focar só no essencial: assistente + chat Gemini
- READMEs devem ser simples e diretos
- **NUNCA usar email @kyndryl.com - usar sempre andrefbfsilva@gmail.com**

## Status Atual
- GeminiCat HD 128x128 estilo Stardew Valley
- 4 raças de gatos (Laranja, Tabby, Siamês, Tuxedo)
- Animação de caminhada com 6 frames por gato
- Movimento restrito à zona inferior do ecrã (últimos 250px)
- Chat com Gemini API integrado
- Sistema de preferências guardadas em JSON
- Modo simulado para chat sem API key

## Como executar
```bash
pip install -r requirements.txt
python main.py
```

Ou duplo clique em `run-cat.bat`

## Arquivos essenciais
- `main.py` - Aplicação principal HD 128x128
- `sprite_generator_hd.py` - Gerador de sprites HD Stardew Valley
- `gemini_chat_real.py` - Chat real com Gemini
- `cat_breeds.py` - Sistema de raças (legacy)
- `sprites_hd/` - Sprites HD 128x128 e animações
- `cat_preferences.json` - Raça selecionada guardada
- `run-cat.bat` - Atalho principal
- `.env` - Configurações API

## Controles
- Clique esquerdo: deixar feliz
- Clique botão do meio: menu de seleção de raça (2x2 com preview)
- Clique direito: chat com GeminiCat
- Arrastar: mover assistente
- ESC: sair

## Sprites HD
- 128x128 pixels
- Estilo Stardew Valley premium
- Outline marrom escuro
- Sombreamento multi-tom suave
- Sombra no chão
- 6 frames de animação por gato
- Patas alternadas, cauda balançando, cabeça com bounce

## Créditos
Cat sprites by Pop Shop Packs
- https://pop-shop-packs.itch.io/cats-pixel-asset-pack
- Licença: Free for commercial use