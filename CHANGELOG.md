# Changelog

## [3.2.0] - 2025-10-04
### Adicionado
- Links clicáveis no chat (abrem no browser)
- Parser Markdown para links (remove formatação [texto](url))
- Auto-detecção de URLs com e sem protocolo
- Histórico de conversação (memória entre mensagens)
- Cursor muda para mãozinha ao passar sobre links

### Corrigido
- Migração para google-genai v1.41.0 (sintaxe atualizada)
- Google Search Grounding funcional com nova API
- Crash ao fechar chat durante processamento
- Bindings duplicados (clique direito abria 2 chats)
- Personalidade felina subtil do GeminiCat

## [3.1.0] - 2025-10-04
### Adicionado
- Google Search Grounding no chat Gemini
- Sistema inteligente de detecção de keywords (85 keywords em 15 categorias)
- Pontuação automática para ativar pesquisa apenas quando necessário
- Proteção contra false positives com threshold >= 3
- Dois modelos Gemini (com/sem search) para poupar rate limit
- Feedback visual quando pesquisa ativa

## [3.0.0] - 2025-09-29
### Major Refatoração
- Correção sistemática de 14 bugs críticos
- Sistema de logging configurável
- Arquitetura robusta com EventBus, TimerManager, AnimationStateMachine
- Eliminação de memory leaks e race conditions
- Exception handling robusto

## [2.0.0] - 2025-09-22
### Adicionado
- Sprites HD 128x128 estilo Stardew Valley
- 4 raças de gatos com animações
- Chat com Google Gemini API
- Sistema de preferências

## [1.0.0] - 2025-09-22
### Inicial
- Desktop pet básico em Python
- Janela transparente
- Movimento automático