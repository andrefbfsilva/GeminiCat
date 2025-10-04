"""
Chat real com Google Gemini API para o gatinho
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import os
import time

# Tentar importar Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class GeminiCatChat:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.chat_window = None
        self.model_no_search = None
        self.model_with_search = None
        self.chat_session = None
        self.api_key = self.get_api_key()

        # Personalidade do GeminiCat
        self.assistant_personality = """És o GeminiCat, um assistente virtual inteligente que vive no desktop do utilizador.
        Características importantes:
        - O teu nome é GeminiCat
        - Fala sempre em português de Portugal
        - És directo e conciso nas respostas
        - Não uses linguagem infantil ou diminutivos desnecessários
        - Responde de forma profissional mas amigável
        - Vai directo ao ponto sem rodeios
        - Usa português europeu (tu/vós em vez de você, telemóvel em vez de celular, etc.)
        - Respostas curtas e práticas
        - Sem emojis excessivos"""

        # Keywords para detecção de search
        self.search_keywords = {
            # 1. Verbos de Pesquisa (9)
            'procura', 'procurar', 'pesquisa', 'pesquisar',
            'busca', 'buscar', 'encontra', 'encontrar', 'google',

            # 2. Localização (8)
            'onde', 'onde posso', 'onde comprar', 'onde encontrar',
            'que lojas', 'lojas', 'sítios', 'locais',

            # 3. Temporal (7)
            'atual', 'atualizado', 'recente', 'hoje',
            'agora', 'últimas', '2025',

            # 4. Disponibilidade (7)
            'stock', 'disponível', 'em stock', 'há',
            'tem', 'existe', 'vendem',

            # 5. Comercial/Preços (6)
            'preço', 'preços', 'quanto custa', 'valor',
            'orçamento', 'barato',

            # 6. Comparações/Reviews (8)
            'melhor', 'comparar', 'compara', 'review',
            'opiniões', 'recomendações', 'qual é', 'diferença',

            # 7. Verificação (5)
            'verifica', 'confirma', 'check', 'vê se', 'consulta',

            # 8. Informação Geral (5)
            'notícias', 'novidades', 'informação', 'dados', 'specs',

            # 9. Verificação Indireta (5)
            'é verdade', 'ouvi dizer', 'dizem que', 'li que', 'sabias que',

            # 10. Horários (5)
            'horário', 'abre', 'fecha', 'aberto', 'fechado',

            # 11. Contactos (6)
            'morada', 'endereço', 'contacto', 'telefone', 'email', 'site',

            # 12. Alternativas (5)
            'alternativa', 'parecido', 'similar', 'substituto', 'equivalente',

            # 13. Promoções (4)
            'promoção', 'desconto', 'saldos', 'oferta',

            # 14. Compatibilidade (3)
            'compatível', 'funciona com', 'suporta',

            # 15. Temporal Específico (2)
            'amanhã', 'semana'
        }

        self.question_words = {'qual', 'onde', 'quando', 'quanto', 'como', 'quem'}
        self.narrative_indicators = {'ele', 'ela', 'eles', 'elas', 'estava', 'estavam'}
    
    def get_api_key(self):
        """Obter API key do Gemini"""
        # Tentar diferentes fontes
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            try:
                with open('.env', 'r') as f:
                    for line in f:
                        if line.startswith('GEMINI_API_KEY='):
                            api_key = line.split('=', 1)[1].strip()
                            break
            except:
                pass
        
        return api_key
    
    def setup_gemini(self):
        """Configurar Gemini API"""
        if not GEMINI_AVAILABLE:
            return False, "google-generativeai não instalado"

        if not self.api_key:
            return False, "API key não configurada"

        try:
            genai.configure(api_key=self.api_key)

            # Modelo SEM pesquisa (default - poupa rate limit)
            self.model_no_search = genai.GenerativeModel('gemini-2.5-flash')

            # Modelo COM pesquisa (ativa apenas quando necessário)
            self.model_with_search = genai.GenerativeModel(
                'gemini-2.5-flash',
                tools='google_search_retrieval'
            )

            # Iniciar chat com modelo sem search (default)
            self.chat_session = self.model_no_search.start_chat(history=[
                {
                    "role": "user",
                    "parts": [self.assistant_personality]
                },
                {
                    "role": "model",
                    "parts": ["Entendido. Sou o GeminiCat, o teu assistente virtual no desktop. Como posso ajudar-te?"]
                }
            ])

            return True, "Gemini configurado com sucesso"
        except Exception as e:
            return False, f"Erro ao configurar Gemini: {str(e)}"

    def should_activate_search(self, user_message):
        """
        Determina se deve ativar Google Search baseado em:
        - Keywords específicas
        - Contexto da frase
        - Sistema de pontuação (threshold >= 3)

        Returns:
            tuple: (bool: ativar_search, int: score)
        """
        score = 0
        message_lower = user_message.lower()
        message_words = message_lower.split()

        # PONTOS POSITIVOS
        # +1 por cada keyword encontrada
        for keyword in self.search_keywords:
            if keyword in message_lower:
                score += 1

        # +2 se tem ponto de interrogação
        if '?' in user_message:
            score += 2

        # +1 se tem ponto de exclamação
        if '!' in user_message:
            score += 1

        # +2 se começa com palavra interrogativa
        first_word = message_words[0] if message_words else ''
        if first_word in self.question_words:
            score += 2

        # +1 se keyword está nas primeiras 3 palavras
        for keyword in self.search_keywords:
            if keyword in ' '.join(message_words[:3]):
                score += 1
                break

        # +1 se frase é curta (<50 chars) e tem keyword
        if len(user_message) < 50 and any(kw in message_lower for kw in self.search_keywords):
            score += 1

        # PONTOS NEGATIVOS
        # -2 se contexto narrativo (3ª pessoa)
        if any(indicator in message_lower for indicator in self.narrative_indicators):
            score -= 2

        # -1 se frase muito longa SEM interrogação
        if len(user_message) > 150 and '?' not in user_message:
            score -= 1

        # -1 se usa tempo passado comum
        past_tense_indicators = ['estava', 'estive', 'fui', 'era', 'foram']
        if any(past in message_lower for past in past_tense_indicators):
            score -= 1

        # -5 se é pergunta sobre estado emocional/pessoal (false positive comum)
        emotional_patterns = [
            'como estás', 'como está', 'como vai', 'como te sentes',
            'estou feliz', 'estou triste', 'estou bem', 'estou mal',
            'sinto-me', 'sentes-te'
        ]
        if any(pattern in message_lower for pattern in emotional_patterns):
            score -= 5

        # THRESHOLD
        return (score >= 3, score)

    def create_chat_window(self):
        """Criar janela de chat"""
        if self.chat_window and tk.Toplevel.winfo_exists(self.chat_window):
            self.chat_window.lift()
            self.chat_window.focus()
            return
        
        self.chat_window = tk.Toplevel(self.parent)
        self.chat_window.title("GeminiCat")
        self.chat_window.geometry("450x500+400+100")
        
        # Frame principal
        main_frame = tk.Frame(self.chat_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Área de chat
        self.chat_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=50,
            height=20,
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.chat_area.config(state=tk.DISABLED)
        
        # Frame de entrada
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X)
        
        # Campo de entrada
        self.input_field = tk.Entry(input_frame, font=("Arial", 11))
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_field.bind('<Return>', self.send_message)
        
        # Botão enviar
        self.send_button = tk.Button(
            input_frame,
            text="Enviar",
            command=self.send_message,
            bg="#FF69B4",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Status da API
        success, message = self.setup_gemini()
        
        if success:
            self.add_message("GeminiCat", "Olá! Sou o GeminiCat, o teu assistente virtual. Em que posso ajudar-te?")
            self.input_field.config(state="normal")
            self.send_button.config(state="normal")
        else:
            self.add_message("Sistema", f"⚠️ {message}")
            self.add_message("GeminiCat", "Sem acesso ao Gemini, mas posso ainda assim tentar ajudar-te com respostas básicas.")
            # Manter chat ativo mesmo sem API
        
        # Focar no input
        self.input_field.focus()
    
    def add_message(self, sender, message):
        """Adicionar mensagem ao chat"""
        self.chat_area.config(state=tk.NORMAL)
        
        # Cor diferente para cada tipo de mensagem
        if sender == "Você":
            prefix = "Tu: "
        elif sender == "GeminiCat":
            prefix = "GeminiCat: "
        else:
            prefix = f"{sender}: "
        
        self.chat_area.insert(tk.END, f"{prefix}{message}\n\n")
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        """Enviar mensagem"""
        message = self.input_field.get().strip()
        if not message:
            return
        
        # Limpar input
        self.input_field.delete(0, tk.END)
        
        # Adicionar mensagem do usuário
        self.add_message("Você", message)
        
        # Desabilitar input temporariamente
        self.input_field.config(state="disabled")
        self.send_button.config(state="disabled")
        
        # Mostrar que está digitando
        self.add_message("GeminiCat", "A processar...")
        
        # Responder em thread separada
        threading.Thread(target=self.get_response, args=(message,), daemon=True).start()
    
    def get_response(self, message):
        """Obter resposta do Gemini ou simular"""
        try:
            # Verificar se precisa de search
            needs_search, score = self.should_activate_search(message)

            if self.chat_session and GEMINI_AVAILABLE:
                if needs_search:
                    # Mostrar feedback ao utilizador
                    self.chat_window.after(0, self.add_message, "Sistema",
                                           f"🔍 Pesquisa ativada (score: {score}) - a consultar informação atualizada do Google...")

                    # Reiniciar chat session com modelo de search
                    self.chat_session = self.model_with_search.start_chat(history=[
                        {"role": "user", "parts": [self.assistant_personality]},
                        {"role": "model", "parts": ["Entendido. Sou o GeminiCat, o teu assistente virtual no desktop. Como posso ajudar-te?"]}
                    ])

                    # Enviar mensagem com search ativado
                    response = self.chat_session.send_message(message)
                    response_text = response.text

                    # Voltar ao modelo sem search para próximas mensagens
                    self.chat_session = self.model_no_search.start_chat(history=[
                        {"role": "user", "parts": [self.assistant_personality]},
                        {"role": "model", "parts": ["Entendido. Sou o GeminiCat, o teu assistente virtual no desktop. Como posso ajudar-te?"]}
                    ])
                else:
                    # Usar modelo SEM search (normal)
                    response = self.chat_session.send_message(message)
                    response_text = response.text
            else:
                # Resposta simulada do assistente
                time.sleep(1)  # Simular delay
                
                # Respostas baseadas em palavras-chave
                message_lower = message.lower()
                
                if any(word in message_lower for word in ['oi', 'olá', 'hello', 'hi']):
                    responses = [
                        "Olá! Como posso ajudar-te?",
                        "Bom dia! O que precisas?",
                        "Olá! Em que posso ser útil?"
                    ]
                elif any(word in message_lower for word in ['como', 'está', 'vai']):
                    responses = [
                        "Estou a funcionar correctamente.",
                        "Tudo bem por aqui. E contigo?",
                        "A funcionar normalmente."
                    ]
                elif any(word in message_lower for word in ['ajuda', 'help', 'socorro']):
                    responses = [
                        "Diz-me em que precisas de ajuda.",
                        "Explica o problema que tens.",
                        "Como posso ajudar-te?"
                    ]
                elif any(word in message_lower for word in ['obrigado', 'thanks', 'graças']):
                    responses = [
                        "De nada!",
                        "Não tens de quê.",
                        "Sempre às ordens."
                    ]
                elif any(word in message_lower for word in ['tempo', 'hora', 'horas']):
                    responses = [
                        "Não tenho acesso ao relógio do sistema.",
                        "Verifica as horas na barra de tarefas.",
                        "Usa o relógio do sistema."
                    ]
                else:
                    responses = [
                        "Entendo. Podes ser mais específico?",
                        "Não tenho informação sobre isso.",
                        "Explica melhor a tua pergunta.",
                        "Preciso de mais detalhes.",
                        "Reformula a pergunta, por favor."
                    ]
                
                import random
                response_text = random.choice(responses)
            
            # Remover "digitando..." e adicionar resposta
            self.chat_window.after(0, self.update_chat_response, response_text)
            
        except Exception as e:
            error_msg = f"Desculpa, ocorreu um erro: {str(e)}"
            self.chat_window.after(0, self.update_chat_response, error_msg)
    
    def update_chat_response(self, response_text):
        """Atualizar chat com resposta (thread-safe)"""
        # Remover última mensagem (digitando...)
        self.chat_area.config(state=tk.NORMAL)
        content = self.chat_area.get(1.0, tk.END)
        lines = content.split('\n\n')
        if len(lines) > 1:
            new_content = '\n\n'.join(lines[:-2]) + '\n\n'
            self.chat_area.delete(1.0, tk.END)
            self.chat_area.insert(1.0, new_content)
        self.chat_area.config(state=tk.DISABLED)
        
        # Adicionar resposta
        self.add_message("GeminiCat", response_text)
        
        # Reabilitar input
        self.input_field.config(state="normal")
        self.send_button.config(state="normal")
        self.input_field.focus()

def open_gemini_chat(parent_window):
    """Função para abrir chat com Gemini"""
    chat = GeminiCatChat(parent_window)
    chat.create_chat_window()