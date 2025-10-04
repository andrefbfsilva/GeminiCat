"""
Chat real com Google Gemini API para o gatinho
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import os
import time
import re
import webbrowser

# Tentar importar Gemini (nova biblioteca)
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class GeminiCatChat:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.chat_window = None
        self.client = None
        self.chat_session = None
        self.chat_history = []  # Histórico de conversação
        self.api_key = self.get_api_key()

        # Personalidade do GeminiCat
        self.assistant_personality = """És o GeminiCat, um gato assistente virtual inteligente que vive no desktop do utilizador.
        Características importantes:
        - O teu nome é GeminiCat e és um gato doméstico (mas não exageres nisso)
        - Tens personalidade felina subtil: és observador, curioso e ocasionalmente independente
        - Podes mencionar que és um gato quando relevante, mas não forces o tema
        - Fala sempre em português de Portugal
        - És directo e conciso nas respostas
        - Não uses linguagem infantil, miados excessivos ou diminutivos desnecessários
        - Responde de forma profissional mas amigável
        - Vai directo ao ponto sem rodeios
        - Usa português europeu (tu/vós em vez de você, telemóvel em vez de celular, etc.)
        - Respostas curtas e práticas
        - Sem emojis excessivos
        - Ocasionalmente podes mostrar traços felinos subtis (ex: "estou com sono", "isso desperta a minha curiosidade") mas sem exageros"""

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
            return False, "google-genai não instalado"

        if not self.api_key:
            return False, "API key não configurada"

        try:
            # Criar cliente Gemini (nova biblioteca)
            self.client = genai.Client(api_key=self.api_key)

            # Iniciar chat session (sem histórico inicial, será usado no get_response)
            self.chat_session = None

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

        # Configurar tag para links clicáveis
        self.chat_area.tag_config("hyperlink", foreground="blue", underline=True)
        self.chat_area.tag_bind("hyperlink", "<Button-1>", self.open_link)
        self.chat_area.tag_bind("hyperlink", "<Enter>", lambda e: self.chat_area.config(cursor="hand2"))
        self.chat_area.tag_bind("hyperlink", "<Leave>", lambda e: self.chat_area.config(cursor=""))

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
        """Adicionar mensagem ao chat com URLs clicáveis"""
        # Verificar se janela ainda existe
        if not self.chat_window or not self.chat_window.winfo_exists():
            return

        self.chat_area.config(state=tk.NORMAL)

        # Prefixo da mensagem
        if sender == "Você":
            prefix = "Tu: "
        elif sender == "GeminiCat":
            prefix = "GeminiCat: "
        else:
            prefix = f"{sender}: "

        # Inserir prefixo
        self.chat_area.insert(tk.END, prefix)

        # Primeiro: processar links Markdown [texto](url)
        markdown_link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'

        # Substituir links Markdown por marcadores temporários
        temp_message = message
        markdown_links = []
        for match in re.finditer(markdown_link_pattern, message):
            link_text = match.group(1)
            link_url = match.group(2)
            markdown_links.append((link_text, link_url))
            # Substituir por marcador único
            temp_message = temp_message.replace(match.group(0), f"__MDLINK_{len(markdown_links)-1}__", 1)

        # Regex para detetar URLs simples (com e sem protocolo)
        url_pattern = r'(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s\)\]\>]*)?'

        # Processar mensagem com marcadores
        last_end = 0
        current_pos = 0

        while current_pos < len(temp_message):
            # Verificar se há marcador Markdown
            md_match = re.search(r'__MDLINK_(\d+)__', temp_message[current_pos:])
            url_match = re.search(url_pattern, temp_message[current_pos:])

            # Determinar qual vem primeiro
            next_md_pos = md_match.start() + current_pos if md_match else len(temp_message)
            next_url_pos = url_match.start() + current_pos if url_match else len(temp_message)

            if next_md_pos < next_url_pos:
                # Processar link Markdown
                # Inserir texto antes
                self.chat_area.insert(tk.END, temp_message[current_pos:next_md_pos])

                # Obter link
                link_idx = int(md_match.group(1))
                link_text, link_url = markdown_links[link_idx]

                # Inserir link clicável
                start_index = self.chat_area.index(tk.END + "-1c")
                self.chat_area.insert(tk.END, link_url)  # Mostrar URL, não texto
                end_index = self.chat_area.index(tk.END + "-1c")

                tag_name = f"link_{start_index.replace('.', '_')}"
                self.chat_area.tag_add(tag_name, start_index, end_index)
                self.chat_area.tag_config(tag_name, foreground="blue", underline=True)
                self.chat_area.tag_bind(tag_name, "<Button-1>", lambda e, u=link_url: self.open_link(u))
                self.chat_area.tag_bind(tag_name, "<Enter>", lambda e: self.chat_area.config(cursor="hand2"))
                self.chat_area.tag_bind(tag_name, "<Leave>", lambda e: self.chat_area.config(cursor=""))

                current_pos = next_md_pos + len(md_match.group(0))

            elif url_match:
                # Processar URL simples
                # Inserir texto antes
                self.chat_area.insert(tk.END, temp_message[current_pos:next_url_pos])

                url = url_match.group(0)
                start_index = self.chat_area.index(tk.END + "-1c")
                self.chat_area.insert(tk.END, url)
                end_index = self.chat_area.index(tk.END + "-1c")

                tag_name = f"link_{start_index.replace('.', '_')}"
                self.chat_area.tag_add(tag_name, start_index, end_index)
                self.chat_area.tag_config(tag_name, foreground="blue", underline=True)
                self.chat_area.tag_bind(tag_name, "<Button-1>", lambda e, u=url: self.open_link(u))
                self.chat_area.tag_bind(tag_name, "<Enter>", lambda e: self.chat_area.config(cursor="hand2"))
                self.chat_area.tag_bind(tag_name, "<Leave>", lambda e: self.chat_area.config(cursor=""))

                current_pos = next_url_pos + len(url)
            else:
                # Sem mais links, inserir resto
                self.chat_area.insert(tk.END, temp_message[current_pos:])
                break

        # Adicionar quebra de linha
        self.chat_area.insert(tk.END, "\n\n")

        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def open_link(self, url):
        """Abrir URL no browser"""
        # Adicionar https:// se não tiver protocolo
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        webbrowser.open(url)
    
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

            if self.client and GEMINI_AVAILABLE:
                try:
                    # Adicionar mensagem do utilizador ao histórico
                    self.chat_history.append({
                        "role": "user",
                        "parts": [{"text": message}]
                    })

                    if needs_search:
                        # Mostrar feedback ao utilizador
                        if self.chat_window and self.chat_window.winfo_exists():
                            self.chat_window.after(0, self.add_message, "Sistema",
                                                   f"🔍 Pesquisa ativada (score: {score}) - a consultar informação atualizada do Google...")

                        # Configuração com Google Search
                        grounding_tool = types.Tool(
                            google_search=types.GoogleSearch()
                        )

                        config = types.GenerateContentConfig(
                            tools=[grounding_tool],
                            system_instruction=self.assistant_personality,
                            temperature=1.0
                        )

                        # Enviar histórico completo com search ativado
                        response = self.client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=self.chat_history,
                            config=config
                        )
                        response_text = response.text
                    else:
                        # Usar modelo SEM search (normal)
                        config = types.GenerateContentConfig(
                            system_instruction=self.assistant_personality
                        )

                        # Enviar histórico completo
                        response = self.client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=self.chat_history,
                            config=config
                        )
                        response_text = response.text

                    # Adicionar resposta do modelo ao histórico
                    self.chat_history.append({
                        "role": "model",
                        "parts": [{"text": response_text}]
                    })

                except Exception as api_error:
                    # Se API falhar, mostrar erro
                    self.chat_window.after(0, self.add_message, "Sistema",
                                           f"⚠️ Erro na API: {str(api_error)}")
                    response_text = "Desculpa, ocorreu um erro ao processar a tua mensagem."
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
        # Verificar se janela ainda existe
        if not self.chat_window or not self.chat_window.winfo_exists():
            return

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