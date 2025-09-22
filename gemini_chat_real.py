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
        self.model = None
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
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Iniciar chat com personalidade
            self.chat_session = self.model.start_chat(history=[
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
            if self.chat_session and GEMINI_AVAILABLE:
                # Resposta real do Gemini
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