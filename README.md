# GeminiCat

Assistente virtual com sprites pixel art que conversa com Google Gemini.

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
- Clique direito: chat com GeminiCat
- Arrastar: mover assistente
- ESC: sair

## Funcionalidades
- Sprites pixel art animados
- Diferentes humores (idle, happy, sleep)
- Chat inteligente com Gemini AI
- Assistente dorme após 30s sem interação
- Movimento automático pela tela
- Janela transparente (se suportada)

## Arquivos
- `main.py` - aplicação principal
- `cat_sprites.py` - gerador de sprites
- `gemini_chat_real.py` - chat GeminiCat
- `sprites/` - imagens do assistente
- `run-cat.bat` - atalho principal