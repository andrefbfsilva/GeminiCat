# GeminiCat HD

Assistente virtual com sprites HD estilo Stardew Valley que conversa com Google Gemini.

## Instalação
```bash
pip install -r requirements.txt
```

## Execução
Duplo clique em `run-cat.bat` ou:
```bash
python main.py
```

## Configuração Gemini (opcional)
Criar arquivo `.env` com:
```
GEMINI_API_KEY=sua_chave_aqui
```

Obter chave em: https://makersuite.google.com/app/apikey

Funciona sem API key (respostas simuladas).

## Controles
- Clique esquerdo: deixar feliz
- Botão do meio: escolher raça do gato
- Clique direito: chat com GeminiCat
- Arrastar: mover assistente
- ESC: sair

## Funcionalidades
- Sprites HD 128x128 estilo Stardew Valley
- 4 raças de gatos (Laranja, Tabby, Siamês, Tuxedo)
- Animação de caminhada com 6 frames
- Movimento na zona inferior do ecrã
- Chat inteligente com Gemini AI
- Sistema de preferências guardadas
- Janela transparente (se suportada)

## Arquivos
- `main.py` - aplicação principal HD
- `sprite_generator_hd.py` - gerador de sprites HD
- `gemini_chat_real.py` - chat com Gemini
- `sprites_hd/` - sprites HD e animações
- `run-cat.bat` - atalho principal

## Créditos e Atribuições
Cat sprites by **Pop Shop Packs**
- https://pop-shop-packs.itch.io/cats-pixel-asset-pack
- Licença: Free for commercial use