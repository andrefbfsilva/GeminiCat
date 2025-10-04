"""
GeminiCat - Assistente Virtual com Sprites e Gemini AI
"""
import tkinter as tk
import sys
import random
import time
import os
import json
import logging
from functools import partial
from PIL import Image, ImageTk, ImageDraw
# from cat_breeds import CatBreedSystem  # REMOVIDO: não utilizado

# CORREÇÃO: Constantes para eliminar magic numbers
class GeminiCatConfig:
    """Configurações centralizadas do GeminiCat"""
    # Sprite settings
    SPRITE_SIZE = 128
    ANIMATION_FRAMES = 6
    ANIMATION_SPEED_THRESHOLD = 10
    
    # Timing settings (em milissegundos)
    MOOD_RESET_TIME = 2000
    SLEEP_THRESHOLD_SECONDS = 30
    MOOD_CHECK_INTERVAL = 5000
    BEHAVIOR_CHANGE_MIN = 100
    BEHAVIOR_CHANGE_MAX = 500
    POSITION_UPDATE_INTERVAL = 100
    
    # Movement settings
    MOVEMENT_ZONE_HEIGHT = 250
    BOTTOM_MARGIN = 40
    DEFAULT_START_X_OFFSET = 300
    
    # Desktop level settings
    DESKTOP_LEVEL_INIT_DELAY = 1000
    DESKTOP_CHECK_DELAY = 5000
    DESKTOP_CHECK_INTERVAL = 10000
    DESKTOP_RETRY_DELAY = 2000
    
    # Colors
    TRANSPARENT_COLOR = "#000001"
    FALLBACK_BG = "lightgray"
    
    # Wake up threshold
    WAKE_UP_THRESHOLD_SECONDS = 5

CONFIG = GeminiCatConfig()

# CORREÇÃO: Sistema de logging configurável
def setup_logging():
    """Configura sistema de logging baseado em variável de ambiente"""
    log_level = os.environ.get('GEMINICAT_LOG_LEVEL', 'INFO').upper()
    
    # Converte string para constante do logging
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    level = level_map.get(log_level, logging.INFO)
    
    # Configuração básica do logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger('GeminiCat')

# Inicializar logger
logger = setup_logging()

# CORREÇÃO: Observer Pattern para eliminar circular dependencies
from typing import Dict, List, Callable
import weakref

class EventBus:
    """Event-driven architecture para desacoplar componentes"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._listeners = {}
        return cls._instance
    
    def subscribe(self, event: str, callback: Callable):
        """Subscrever a evento"""
        if event not in self._listeners:
            self._listeners[event] = []
        # Use weak references para prevenir memory leaks
        self._listeners[event].append(weakref.ref(callback))
    
    def publish(self, event: str, data=None):
        """Publicar evento"""
        if event not in self._listeners:
            return
        
        # Limpar referências mortas e executar callbacks ativos
        alive_listeners = []
        for weak_callback in self._listeners[event]:
            callback = weak_callback()
            if callback is not None:
                try:
                    callback(data)
                    alive_listeners.append(weak_callback)
                except Exception as e:
                    logger.error(f"Erro no callback do evento {event}: {e}")
        
        self._listeners[event] = alive_listeners

# Singleton global event bus
event_bus = EventBus()

# CORREÇÃO: Timer Manager centralizado para thread safety
from dataclasses import dataclass
import time as time_module

@dataclass
class TimedTask:
    callback: Callable
    interval: float  # em segundos
    last_run: float = 0
    enabled: bool = True
    name: str = ""

class TimerManager:
    """Centralized timer system para evitar race conditions"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tasks = {}
            cls._instance._running = False
            cls._instance._window = None
        return cls._instance
    
    def set_window(self, window):
        """Definir janela Tkinter"""
        self._window = window
    
    def add_task(self, name: str, callback: Callable, interval_ms: int):
        """Adicionar task ao timer manager"""
        self._tasks[name] = TimedTask(
            callback=callback,
            interval=interval_ms / 1000.0,  # converter para segundos
            last_run=time_module.time(),
            name=name
        )
        logger.debug(f"Timer task '{name}' adicionado com intervalo {interval_ms}ms")
    
    def remove_task(self, name: str):
        """Remover task"""
        self._tasks.pop(name, None)
        logger.debug(f"Timer task '{name}' removido")
    
    def start(self):
        """Iniciar timer manager"""
        if not self._running and self._window:
            self._running = True
            self._tick()
            logger.debug("TimerManager iniciado")
    
    def stop(self):
        """Parar timer manager"""
        self._running = False
        logger.debug("TimerManager parado")
    
    def _tick(self):
        """Tick interno do timer manager"""
        if not self._running:
            return
        
        current_time = time_module.time()
        
        # Executar tasks que estão prontos
        for task in list(self._tasks.values()):
            if (task.enabled and 
                current_time - task.last_run >= task.interval):
                try:
                    task.callback()
                    task.last_run = current_time
                except Exception as e:
                    logger.error(f"Erro na task '{task.name}': {e}")
        
        # Schedule próximo tick (50ms = 20 FPS)
        if self._window and self._running:
            self._window.after(50, self._tick)

# Singleton global timer manager
timer_manager = TimerManager()

# CORREÇÃO: State Machine para consistência de animações
from enum import Enum

class AnimationState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    SLEEPING = "sleeping"

class AnimationStateMachine:
    """State machine para controlar animações consistentemente"""
    
    def __init__(self):
        self.current_state = AnimationState.IDLE
        self.walk_frame = 0
        self.frame_counter = 0
        self.last_sprite_name = None
        self.walk_frames_available = 0
    
    def set_walk_frames_count(self, count):
        """Definir número de frames de caminhada disponíveis"""
        self.walk_frames_available = count
    
    def can_transition_to(self, new_state: AnimationState) -> bool:
        """Verificar se transição de estado é válida"""
        # Todas as transições são válidas neste caso simples
        return True
    
    def transition_to(self, new_state: AnimationState, mood: str, vx: int, vy: int):
        """Transição de estado com lógica consistente"""
        if not self.can_transition_to(new_state):
            return self.current_state
        
        old_state = self.current_state
        self.current_state = new_state
        
        # Reset frame counter apenas em mudanças de estado
        if old_state != new_state:
            self.frame_counter = 0
            if new_state != AnimationState.WALKING:
                self.walk_frame = 0  # Reset apenas quando sai de walking
        
        return self.current_state
    
    def get_next_frame(self):
        """Obter próximo frame de animação de forma consistente"""
        self.frame_counter += 1
        
        if self.current_state == AnimationState.WALKING:
            if self.frame_counter >= CONFIG.ANIMATION_SPEED_THRESHOLD:
                if self.walk_frames_available > 0:
                    self.walk_frame = (self.walk_frame + 1) % self.walk_frames_available
                self.frame_counter = 0
                return self.walk_frame
            return self.walk_frame
        
        return 0  # Frame 0 para estados não-walking
    
    def get_sprite_name(self, mood: str) -> str:
        """Obter nome do sprite baseado no estado"""
        return f"cat_{mood}"

class CatPet:
    def __init__(self, window):
        self.window = window
        # CORREÇÃO: Eliminada dependência circular - sem desktop_app reference
        self.size = CONFIG.SPRITE_SIZE
        self.position_frame_count = 0
        
        # CORREÇÃO: State Machine para animações consistentes
        self.animation_state_machine = AnimationStateMachine()
        
        # Sistema de raças
        self.current_breed = self.load_saved_breed()
        
        # Estado do pet
        self.vx = 0
        self.vy = 0
        self.state = 'idle'
        self.mood = 'idle'
        self.last_interaction = time.time()
        
        # Cache permanente de sprites
        self.sprite_cache = {}
        
        # Carregar sprites
        self.sprites = self.load_sprites()
        self.walk_sprites = self.load_walk_sprites()
        
        # CORREÇÃO: Informar state machine sobre frames disponíveis com proteção
        walk_frame_count = max(1, len(self.walk_sprites))  # Mínimo 1 para evitar divisão por zero
        self.animation_state_machine.set_walk_frames_count(walk_frame_count)
        
        # Canvas (cor diferente de transparentcolor para evitar conflitos)
        self.canvas = tk.Canvas(
            window,
            width=self.size,
            height=self.size,
            bg=CONFIG.TRANSPARENT_COLOR,
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Pet sprite (será criado no primeiro update_position)
        self.pet_sprite = None
        
        # Anti-flicker: tracking de estado anterior
        self.last_image = None
        
        # CORREÇÃO: Estado gerido pela state machine (não variáveis individuais)
        
        # Bindings apenas no canvas (evitar duplicação)
        self.canvas.bind('<Button-1>', self.on_left_click)
        self.canvas.bind('<Button-2>', self.open_breed_selector)
        self.canvas.bind('<Button-3>', self.on_right_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        
        # Subscrever a eventos via EventBus
        event_bus.subscribe("monitor_info_response", self.handle_monitor_info_response)
        
        # CORREÇÃO: Usar TimerManager para coordenar todos os timers
        timer_manager.set_window(window)
        timer_manager.add_task("position_update", self.update_position, CONFIG.POSITION_UPDATE_INTERVAL)
        timer_manager.add_task("mood_check", self.mood_check, CONFIG.MOOD_CHECK_INTERVAL)
        timer_manager.add_task("random_behavior", self.random_behavior, CONFIG.BEHAVIOR_CHANGE_MIN)
        timer_manager.start()
        
        logger.info("GeminiCat criado com sprites!")
    
    def handle_monitor_info_response(self, data):
        """Handle monitor info response via EventBus"""
        self._monitor_info = data
    
    def get_monitor_info(self):
        """Obter monitor info via EventBus"""
        # Publicar request e usar fallback se não houver response
        event_bus.publish("monitor_info_request")
        
        if hasattr(self, '_monitor_info') and self._monitor_info:
            return self._monitor_info
        
        # Fallback para Tkinter se não houver monitor info
        return {
            'left': 0, 'top': 0, 
            'right': self.window.winfo_screenwidth(), 
            'bottom': self.window.winfo_screenheight()
        }
    
    def load_saved_breed(self):
        """Carregar raça guardada"""
        try:
            with open('cat_preferences.json', 'r') as f:
                prefs = json.load(f)
                return prefs.get('breed', 'orange')
        except (FileNotFoundError, json.JSONDecodeError, KeyError, PermissionError) as e:
            # CORREÇÃO: Exception específica em vez de bare except
            logger.warning(f"Erro ao carregar preferências: {e} - usando padrão 'orange'")
            return 'orange'
    
    def save_breed(self, breed):
        """Guardar raça selecionada"""
        with open('cat_preferences.json', 'w') as f:
            json.dump({'breed': breed}, f)
    
    def load_sprites(self):
        """Carregar sprites HD da raça atual - OTIMIZADO: 1 PhotoImage por raça"""
        sprites = {}
        
        # Tentar carregar sprites HD 128x128
        sit_path = f"sprites_hd/{self.current_breed}_sit.png"
        logger.debug(f"Tentando carregar: {sit_path}")
        if os.path.exists(sit_path):
            try:
                with Image.open(sit_path) as img:
                    logger.debug(f"Imagem carregada: {img.size}, modo: {img.mode}")
                    
                    # CORREÇÃO: Criar apenas 1 PhotoImage por raça (não 3 duplicados)
                    single_photo = ImageTk.PhotoImage(img.copy())
                    
                    # Reutilizar o mesmo PhotoImage para todos os moods
                    sprites['cat_idle'] = single_photo
                    sprites['cat_happy'] = single_photo
                    sprites['cat_sleep'] = single_photo
                    
                    # Cache com chave única por raça
                    cache_key = f"{self.current_breed}_sprite"
                    self.sprite_cache[cache_key] = single_photo
                    
                    logger.info(f"Sprite HD {self.current_breed} carregado - 1 PhotoImage reutilizado")
                    return sprites
            except Exception as e:
                logger.error(f"Erro ao carregar HD: {e}")
        else:
            logger.warning(f"Arquivo não encontrado: {sit_path}")
        
        # Fallback: sprites antigos
        variant_path = f"sprites/cat_{self.current_breed}.png"
        if os.path.exists(variant_path):
            try:
                with Image.open(variant_path) as img:
                    resized_img = img.resize((CONFIG.SPRITE_SIZE, CONFIG.SPRITE_SIZE), Image.NEAREST)
                    
                    # CORREÇÃO: Criar apenas 1 PhotoImage por raça
                    single_photo = ImageTk.PhotoImage(resized_img)
                    
                    # Reutilizar para todos os moods
                    sprites['cat_idle'] = single_photo
                    sprites['cat_happy'] = single_photo  
                    sprites['cat_sleep'] = single_photo
                    
                    # Cache otimizado
                    cache_key = f"{self.current_breed}_sprite"
                    self.sprite_cache[cache_key] = single_photo
                    
                    logger.info(f"Sprite variante {self.current_breed} carregado - 1 PhotoImage reutilizado")
                    return sprites
            except Exception as e:
                logger.error(f"Erro ao carregar variante: {e}")
        
        # Fallback final
        if not sprites:
            logger.warning("Usando sprites de fallback")
            sprites = self.create_fallback_sprites()
            # Cache fallback sprites
            for name, photo in sprites.items():
                self.sprite_cache[f"fallback_{name}"] = photo
        
        return sprites
    
    def load_walk_sprites(self):
        """Carregar frames de animação de caminhada com cache permanente"""
        walk_sprites = []
        
        for frame in range(6):
            walk_path = f"sprites_hd/{self.current_breed}_walk_{frame}.png"
            if os.path.exists(walk_path):
                try:
                    # CORREÇÃO: Context manager para evitar resource leak
                    with Image.open(walk_path) as img:
                        photo = ImageTk.PhotoImage(img.copy())
                        walk_sprites.append(photo)
                        
                        # Cache permanente
                        self.sprite_cache[f'walk_{frame}'] = photo
                except Exception as e:
                    logger.error(f"Erro ao carregar walk frame {frame}: {e}")
        
        if not walk_sprites:
            logger.info("Sem animação de caminhada, usando sprite estático")
        
        return walk_sprites
    
    def create_fallback_sprites(self):
        """Criar sprites simples como fallback - OTIMIZADO: 1 sprite reutilizado"""
        # CORREÇÃO: Import movido para topo do ficheiro
        
        # CORREÇÃO: Criar apenas 1 sprite fallback em vez de 3 diferentes
        img = Image.new('RGBA', (CONFIG.SPRITE_SIZE, CONFIG.SPRITE_SIZE), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Desenhar gatinho simples (cor neutra para todos os moods)
        draw.ellipse([20, 20, 108, 108], fill='orange')  # Corpo
        draw.ellipse([40, 40, 60, 60], fill='black')     # Olho esquerdo
        draw.ellipse([68, 40, 88, 60], fill='black')     # Olho direito  
        draw.ellipse([60, 70, 68, 78], fill='pink')      # Nariz
        
        # Criar 1 PhotoImage e reutilizar
        fallback_photo = ImageTk.PhotoImage(img)
        
        sprites = {
            'cat_idle': fallback_photo,
            'cat_happy': fallback_photo,
            'cat_sleep': fallback_photo
        }
        
        return sprites
    
    def update_sprite(self, force=False):
        """CORREÇÃO: Atualizar sprite usando State Machine"""
        # Determinar estado de animação baseado em movimento e mood
        if (self.vx != 0 or self.vy != 0) and self.walk_sprites and self.mood != 'sleep':
            target_state = AnimationState.WALKING
        elif self.mood == 'sleep':
            target_state = AnimationState.SLEEPING
        else:
            target_state = AnimationState.IDLE
        
        # Usar state machine para transição
        current_state = self.animation_state_machine.transition_to(
            target_state, self.mood, self.vx, self.vy
        )
        
        # Obter sprite baseado no estado atual
        if current_state == AnimationState.WALKING and self.walk_sprites:
            # Usar animação de caminhada com proteção robusta
            frame_index = self.animation_state_machine.get_next_frame()
            # CORREÇÃO: Proteção contra índices inválidos (negativos ou >= length)
            if 0 <= frame_index < len(self.walk_sprites):
                new_image = self.walk_sprites[frame_index]
            else:
                # Fallback se frame inválido
                logger.warning(f"Frame index inválido: {frame_index} para {len(self.walk_sprites)} frames")
                new_image = self.sprites.get(f"cat_{self.mood}", None)
        else:
            # Usar sprite estático
            sprite_name = self.animation_state_machine.get_sprite_name(self.mood)
            new_image = self.sprites.get(sprite_name, None)
        
        # Atualizar canvas apenas se imagem mudou ou é forçado
        if new_image and (self.last_image != new_image or force or not self.pet_sprite):
            if not self.pet_sprite:
                self.pet_sprite = self.canvas.create_image(
                    self.size // 2, self.size // 2,
                    image=new_image
                )
                logger.debug(f"Sprite criado: {current_state.value}, ID: {self.pet_sprite}")
            else:
                self.canvas.itemconfig(self.pet_sprite, image=new_image)
                logger.debug(f"Sprite atualizado: {current_state.value}")
            
            self.last_image = new_image
        elif not new_image:
            logger.error(f"Sprite não encontrado para estado {current_state.value}")
            return
    
    def on_left_click(self, event):
        """GeminiCat fica feliz quando clicado"""
        logger.debug("Clique esquerdo detectado!")
        logger.debug("GeminiCat feliz!")
        self.mood = 'happy'
        self.last_interaction = time.time()
        self.update_sprite(force=True)
        
        # Voltar ao normal após um tempo
        self.window.after(CONFIG.MOOD_RESET_TIME, self.reset_mood)
    
    def open_breed_selector(self, event):
        """Abrir menu de seleção de raça"""
        logger.debug("Botão do meio detectado!")
        logger.debug("Abrindo seletor de raça...")
        try:
            selector = tk.Toplevel()
            selector.title("Escolher Gato")
            selector.resizable(False, False)
            selector.wm_attributes('-topmost', True)
            
            # Título
            title_frame = tk.Frame(selector)
            title_frame.pack(pady=10)
            tk.Label(title_frame, text="Escolhe o teu gato:", 
                     font=("Arial", 14, "bold")).pack()
            
            # Frame para os 6 botões (3x2)
            preview_frame = tk.Frame(selector)
            preview_frame.pack(padx=20, pady=10)
            
            # 6 variantes com preview HD (3 colunas x 2 linhas)
            breeds = [
                ('orange', 'Laranja', 0, 0),
                ('tabby', 'Tabby', 0, 1),
                ('siamese', 'Siamês', 0, 2),
                ('tuxedo', 'Tuxedo', 1, 0),
                ('tortie', 'Tortoiseshell', 1, 1),
                ('calico', 'Calico', 1, 2)
            ]
            
            for breed_id, name, row, col in breeds:
                # Preview do sprite HD
                sprite_path = f"sprites_hd/{breed_id}_sit.png"
                if os.path.exists(sprite_path):
                    try:
                        # CORREÇÃO: Context manager para evitar resource leak
                        with Image.open(sprite_path) as img:
                            resized_img = img.resize((80, 80), Image.NEAREST)
                            photo = ImageTk.PhotoImage(resized_img)
                        
                        btn = tk.Button(
                            preview_frame,
                            image=photo,
                            text=name,
                            compound="top",
                            width=120,
                            height=110,
                            font=("Arial", 9),
                            command=partial(self.change_breed, breed_id, selector)
                        )
                        btn.image = photo
                        btn.grid(row=row, column=col, padx=5, pady=5)
                    except Exception as e:
                        logger.error(f"Erro ao carregar preview {breed_id}: {e}")
                        tk.Button(
                            preview_frame,
                            text=name,
                            width=15,
                            height=8,
                            font=("Arial", 9),
                            command=partial(self.change_breed, breed_id, selector)
                        ).grid(row=row, column=col, padx=5, pady=5)
                else:
                    tk.Button(
                        preview_frame,
                        text=name,
                        width=15,
                        height=8,
                        font=("Arial", 9),
                        command=partial(self.change_breed, breed_id, selector)
                    ).grid(row=row, column=col, padx=5, pady=5)
            
            # Créditos
            credits_frame = tk.Frame(selector)
            credits_frame.pack(pady=10)
            tk.Label(
                credits_frame, 
                text="Sprites: Pop Shop Packs",
                font=("Arial", 8),
                fg="gray"
            ).pack()
            
            # Calcular tamanho automaticamente
            selector.update_idletasks()
            width = preview_frame.winfo_reqwidth() + 60
            height = title_frame.winfo_reqheight() + preview_frame.winfo_reqheight() + credits_frame.winfo_reqheight() + 60
            selector.geometry(f"{width}x{height}")
            
            # Centrar na tela
            x = (selector.winfo_screenwidth() // 2) - (width // 2)
            y = (selector.winfo_screenheight() // 2) - (height // 2)
            selector.geometry(f"{width}x{height}+{x}+{y}")
            
        except Exception as e:
            logger.error(f"Erro ao criar seletor de raça: {e}")
            import traceback
            traceback.print_exc()
    
    def change_breed(self, breed, selector_window):
        """Mudar raça do gato"""
        try:
            logger.debug(f"Iniciando troca para {breed}...")
            
            # CORREÇÃO: Limpar cache da raça anterior para evitar memory leak
            old_breed = self.current_breed
            if old_breed != breed:
                old_cache_key = f"{old_breed}_sprite" 
                self.sprite_cache.pop(old_cache_key, None)
                logger.debug(f"Cache da raça {old_breed} limpo")
            
            self.current_breed = breed
            self.save_breed(breed)
            
            # Limpar sprite atual antes de recarregar
            if self.pet_sprite:
                self.canvas.delete(self.pet_sprite)
                self.pet_sprite = None
            
            # Recarregar sprites
            self.sprites = self.load_sprites()
            self.walk_sprites = self.load_walk_sprites()
            
            # CORREÇÃO: Atualizar state machine com proteção após reload
            walk_frame_count = max(1, len(self.walk_sprites))
            self.animation_state_machine.set_walk_frames_count(walk_frame_count)
            
            # Recriar sprite
            self.update_sprite(force=True)
            
            logger.info(f"Mudou para gato {breed}")
            
        except Exception as e:
            logger.error(f"Erro na troca de raça: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Fechar janela sempre, mesmo se houver erro
            try:
                if selector_window and selector_window.winfo_exists():
                    selector_window.destroy()
            except Exception as e:
                logger.error(f"Erro ao fechar seletor: {e}")
    
    def on_right_click(self, event):
        """Abrir chat com Gemini"""
        logger.debug("Right click detectado - abrindo chat...")
        try:
            logger.debug("Tentando importar gemini_chat_real...")
            from gemini_chat_real import open_gemini_chat
            logger.debug("Import bem-sucedido, chamando open_gemini_chat...")
            open_gemini_chat(None)  # Não passar self.window que tem overrideredirect
            logger.debug("open_gemini_chat executado com sucesso")
        except ImportError as e:
            logger.warning(f"ImportError: {e} - usando fallback")
            # Fallback para chat simples
            self.open_simple_chat()
        except Exception as e:
            logger.critical(f"ERRO CRÍTICO no chat: {e}")
            import traceback
            traceback.print_exc()
            # Fallback para chat simples
            try:
                logger.debug("Tentando fallback chat...")
                self.open_simple_chat()
            except Exception as e2:
                logger.error(f"ERRO no fallback chat: {e2}")
                traceback.print_exc()
    
    def open_simple_chat(self):
        """Chat simples como fallback"""
        try:
            chat_window = tk.Toplevel()  # Sem parent
            chat_window.title("Chat com GeminiCat")
            chat_window.geometry("400x300+400+400")
            chat_window.wm_attributes('-topmost', True)
            
            text_area = tk.Text(chat_window, height=15, width=50)
            text_area.pack(padx=10, pady=10)
            text_area.insert("1.0", "Olá! Sou o GeminiCat!\n\nO chat completo com Gemini está disponível.\nEste é apenas um modo de fallback.\n\nFecha e tenta novamente!")
            text_area.config(state="disabled")
            
            btn = tk.Button(chat_window, text="Fechar", command=chat_window.destroy)
            btn.pack(pady=5)
        except Exception as e:
            logger.error(f"Erro ao criar chat simples: {e}")
            import traceback
            traceback.print_exc()
    
    def move_window_smooth(self, x, y):
        """Mover janela sem flickering usando geometry()"""
        try:
            self.window.geometry(f'{self.size}x{self.size}+{x}+{y}')
        except Exception as e:
            logger.error(f"Erro no movimento: {e}")
    
    def on_drag(self, event):
        """Arrastar o GeminiCat"""
        logger.debug("Arrasto detectado!")
        try:
            x = self.window.winfo_pointerx() - self.size//2
            y = self.window.winfo_pointery() - self.size//2
            logger.debug(f"Movendo para: {x}, {y}")
            self.move_window_smooth(x, y)
            self.last_interaction = time.time()
        except Exception as e:
            logger.error(f"Erro no drag: {e}")
    
    def reset_mood(self):
        """Resetar humor do GeminiCat"""
        if self.mood == 'happy':
            self.mood = 'idle'
            self.update_sprite(force=True)
    
    def mood_check(self):
        """Verificar se o GeminiCat deve dormir"""
        time_since_interaction = time.time() - self.last_interaction
        
        if time_since_interaction > CONFIG.SLEEP_THRESHOLD_SECONDS and self.mood != 'sleep':
            self.mood = 'sleep'
            self.vx = 0  # Parar movimento
            self.vy = 0
            self.update_sprite(force=True)
            logger.debug("GeminiCat dormindo...")
        elif time_since_interaction <= CONFIG.WAKE_UP_THRESHOLD_SECONDS and self.mood == 'sleep':
            self.mood = 'idle'
            self.update_sprite(force=True)
            logger.debug("GeminiCat acordou!")
        
        # CORREÇÃO: Mood check agora gerido pelo TimerManager (não precisa schedule manual)
    
    def random_behavior(self):
        """Comportamento aleatório do GeminiCat"""
        if self.mood != 'sleep':
            behaviors = ['idle', 'move_left', 'move_right', 'move_up', 'move_down', 'wander']
            self.state = random.choice(behaviors)
            
            if self.state == 'move_left':
                self.vx, self.vy = -1, 0
            elif self.state == 'move_right':
                self.vx, self.vy = 1, 0
            elif self.state == 'move_up':
                self.vx, self.vy = 0, -1
            elif self.state == 'move_down':
                self.vx, self.vy = 0, 1
            elif self.state == 'wander':
                self.vx = random.randint(-1, 1)
                self.vy = random.randint(-1, 1)
            else:
                self.vx, self.vy = 0, 0
        
        # CORREÇÃO: Random behavior com intervalo variável no TimerManager
        next_interval = random.randint(CONFIG.BEHAVIOR_CHANGE_MIN, CONFIG.BEHAVIOR_CHANGE_MAX)
        timer_manager.remove_task("random_behavior")
        timer_manager.add_task("random_behavior", self.random_behavior, next_interval)
    
    def update_position(self):
        """Atualizar posição do GeminiCat - movimento apenas na zona inferior"""
        # Criar sprite apenas na primeira vez
        if not self.pet_sprite:
            self.update_sprite(force=True)
        
        # Incrementar contador de frames
        self.position_frame_count += 1
        
        if self.mood != 'sleep':
            try:
                # CORREÇÃO: Usar EventBus para obter monitor info sem dependency
                monitor = self.get_monitor_info()
                
                geometry = self.window.geometry()
                parts = geometry.split('+')
                if len(parts) >= 3:
                    current_x = int(parts[1])
                    current_y = int(parts[2])
                    
                    new_x = current_x + self.vx
                    new_y = current_y + self.vy
                    
                    # Limitar movimento horizontal dentro do monitor primário
                    min_x = monitor['left']
                    max_x = monitor['right'] - self.size
                    
                    if new_x <= min_x or new_x >= max_x:
                        self.vx = -self.vx
                        new_x = max(min_x, min(new_x, max_x))
                    
                    # RESTRIÇÃO: apenas últimos pixels do monitor primário
                    min_y = monitor['bottom'] - CONFIG.MOVEMENT_ZONE_HEIGHT
                    max_y = monitor['bottom'] - self.size - CONFIG.BOTTOM_MARGIN
                    
                    if new_y < min_y:
                        new_y = min_y
                        self.vy = 0
                    elif new_y > max_y:
                        self.vy = 0
                        new_y = max_y
                    
                    # Mover janela - só se posição mudou
                    if new_x != current_x or new_y != current_y:
                        self.move_window_smooth(new_x, new_y)
                    
                    # Atualizar animação
                    self.update_sprite()
            
            except Exception as e:
                logger.error(f"Erro no movimento: {e}")
        else:
            # Quando dorme, atualizar sprite (forçar para garantir visibilidade)
            self.update_sprite(force=True)
        
        # REMOVIDO: reforço periódico causava flickering
        # if self.desktop_app and self.position_frame_count % 50 == 0:
        #     self.desktop_app.set_desktop_level()
        
        # CORREÇÃO: Position update agora gerido pelo TimerManager (não precisa schedule manual)

class CatDesktopApp:
    def __init__(self):
        self.window = tk.Tk()
        # CORREÇÃO: State tracking para evitar race conditions
        self.desktop_level_initialized = False
        self.setup_window()
        
        # CORREÇÃO: EventBus para comunicação desacoplada
        event_bus.subscribe("monitor_info_request", self.provide_monitor_info)
        
        self.pet = CatPet(self.window)  # Sem circular dependency
    
    def provide_monitor_info(self, data=None):
        """Provide monitor info via EventBus"""
        if hasattr(self, 'monitor_info'):
            event_bus.publish("monitor_info_response", self.monitor_info)
    
    def get_primary_monitor_info(self):
        """Obter informações do monitor primário usando Windows API"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Obter monitor primário
            primary_monitor = ctypes.windll.user32.MonitorFromPoint(
                wintypes.POINT(0, 0), 1  # MONITOR_DEFAULTTOPRIMARY
            )
            
            # Estrutura MONITORINFO
            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("rcMonitor", wintypes.RECT),
                    ("rcWork", wintypes.RECT),
                    ("dwFlags", wintypes.DWORD)
                ]
            
            monitor_info = MONITORINFO()
            monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
            
            if ctypes.windll.user32.GetMonitorInfoW(primary_monitor, ctypes.byref(monitor_info)):
                work_area = monitor_info.rcWork
                monitor_area = monitor_info.rcMonitor
                
                logger.debug(f"Monitor primário - Work area: {work_area.left},{work_area.top} to {work_area.right},{work_area.bottom}")
                logger.debug(f"Monitor primário - Full area: {monitor_area.left},{monitor_area.top} to {monitor_area.right},{monitor_area.bottom}")
                
                return {
                    'left': work_area.left,
                    'top': work_area.top, 
                    'right': work_area.right,
                    'bottom': work_area.bottom,
                    'width': work_area.right - work_area.left,
                    'height': work_area.bottom - work_area.top
                }
        except Exception as e:
            logger.error(f"Erro ao obter info do monitor: {e}")
            
        # Fallback para Tkinter
        return {
            'left': 0,
            'top': 0,
            'right': self.window.winfo_screenwidth(),
            'bottom': self.window.winfo_screenheight(),
            'width': self.window.winfo_screenwidth(),
            'height': self.window.winfo_screenheight()
        }

    def setup_window(self):
        """Configurar janela do GeminiCat"""
        logger.debug("Configurando janela do GeminiCat...")
        
        self.window.title("GeminiCat")
        
        # Obter informações do monitor primário
        self.monitor_info = self.get_primary_monitor_info()
        
        # Tentar transparência
        transparency_mode = False
        try:
            self.window.overrideredirect(True)
            self.window.wm_attributes('-transparentcolor', CONFIG.TRANSPARENT_COLOR)
            
            # Posicionar na zona inferior do monitor primário
            start_x = self.monitor_info['left'] + CONFIG.DEFAULT_START_X_OFFSET
            start_y = self.monitor_info['bottom'] - CONFIG.MOVEMENT_ZONE_HEIGHT
            
            logger.debug(f"Posicionando GeminiCat em: {start_x}, {start_y}")
            self.window.geometry(f"128x128+{start_x}+{start_y}")
            transparency_mode = True
            logger.debug("Modo transparente ativado")
            
            # CORREÇÃO: Usar TimerManager também para desktop level
            self.window.update()
            timer_manager.add_task("desktop_init", self.initialize_desktop_level, CONFIG.DESKTOP_LEVEL_INIT_DELAY)
        except Exception as e:
            logger.warning(f"Transparência não funcionou: {e}")
            transparency_mode = False
        
        if not transparency_mode:
            logger.debug("Usando modo visível")
            self.window.overrideredirect(False)
            self.window.configure(bg="lightgray")
            screen_height = self.window.winfo_screenheight()
            start_y = screen_height - 250
            self.window.geometry(f"128x128+300+{start_y}")
        
        # ESC para sair
        self.window.bind('<Escape>', lambda e: self.quit())
        self.window.focus_set()
    
    def is_window_visible(self):
        """Verificar se a janela está realmente visível no ecrã"""
        try:
            import ctypes
            from ctypes import wintypes
            hwnd = self.window.winfo_id()
            
            # Verificar se janela está visível
            is_visible = ctypes.windll.user32.IsWindowVisible(hwnd)
            
            # CORREÇÃO: Estrutura WINDOWPLACEMENT correta
            class WINDOWPLACEMENT(ctypes.Structure):
                _fields_ = [
                    ("length", wintypes.UINT),
                    ("flags", wintypes.UINT),
                    ("showCmd", wintypes.UINT),
                    ("ptMinPosition", wintypes.POINT),
                    ("ptMaxPosition", wintypes.POINT),
                    ("rcNormalPosition", wintypes.RECT)
                ]
            
            # Verificar se não está minimizada usando estrutura correta
            placement = WINDOWPLACEMENT()
            placement.length = ctypes.sizeof(WINDOWPLACEMENT)
            
            if ctypes.windll.user32.GetWindowPlacement(hwnd, ctypes.byref(placement)):
                is_normal = placement.showCmd != 2  # 2 = SW_SHOWMINIMIZED
                logger.debug(f"Window showCmd: {placement.showCmd} (1=normal, 2=minimized, 3=maximized)")
            else:
                logger.warning("GetWindowPlacement falhou - assumindo normal")
                is_normal = True
            
            return is_visible and is_normal
        except Exception as e:
            logger.error(f"Erro ao verificar visibilidade: {e}")
            import traceback
            traceback.print_exc()
            return True  # Assumir visível se erro
    
    def initialize_desktop_level(self):
        """CORREÇÃO: Inicialização coordenada do desktop level"""
        logger.debug("Iniciando configuração desktop level...")
        timer_manager.remove_task("desktop_init")  # Remove a task de inicialização
        
        if self.set_desktop_level():
            self.desktop_level_initialized = True
            logger.debug("Desktop level inicializado com sucesso")
            # Só iniciar monitoring após inicialização bem-sucedida
            timer_manager.add_task("desktop_check", self.smart_desktop_check, CONFIG.DESKTOP_CHECK_INTERVAL)
        else:
            logger.warning("Falha na inicialização desktop level - tentando novamente")
            # Retry se falhou
            timer_manager.add_task("desktop_init_retry", self.initialize_desktop_level, CONFIG.DESKTOP_RETRY_DELAY)
    
    def set_desktop_level(self):
        """Definir janela para ficar no nível do desktop - versão multi-monitor segura"""
        try:
            import ctypes
            from ctypes import wintypes
            
            hwnd = self.window.winfo_id()
            logger.debug(f"Aplicando desktop level para hwnd: {hwnd}")
            
            # Método simplificado que funciona melhor em multi-monitor
            HWND_BOTTOM = 1
            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002
            SWP_NOACTIVATE = 0x0010
            
            # Primeiro: colocar no fundo
            result = ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE
            )
            
            if result:
                logger.debug("Desktop level: SetWindowPos HWND_BOTTOM successful")
                
                # Segundo: definir flags para não interferir
                GWL_EXSTYLE = -20
                WS_EX_NOACTIVATE = 0x08000000
                WS_EX_TOOLWINDOW = 0x00000080
                WS_EX_TOPMOST = 0x00000008
                
                exstyle = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                new_exstyle = exstyle | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
                # Remover TOPMOST se existir
                new_exstyle &= ~WS_EX_TOPMOST
                
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_exstyle)
                logger.debug("Desktop level: Window styles applied")
                return True  # CORREÇÃO: Retornar sucesso/falha
            else:
                logger.warning("Desktop level: SetWindowPos failed")
                return False
            
        except Exception as e:
            logger.error(f"Erro ao definir nível desktop: {e}")
            return False
    
    def smart_desktop_check(self):
        """Verificação inteligente do nível desktop - só reposiciona se necessário"""
        try:
            # CORREÇÃO: Só executar se desktop level foi inicializado
            if not self.desktop_level_initialized:
                logger.debug("Desktop level ainda não inicializado - aguardando...")
                return
                
            if not self.is_window_visible():
                logger.debug("GeminiCat não visível - reposicionando...")
                self.set_desktop_level()
            # CORREÇÃO: Desktop check agora gerido pelo TimerManager (não precisa schedule manual)
        except Exception as e:
            logger.error(f"Erro no smart_desktop_check: {e}")
            # CORREÇÃO: Timer continua automaticamente
    
    def quit(self):
        print("Adeus! Miau!")
        # CORREÇÃO: Parar TimerManager antes de encerrar
        timer_manager.stop()
        try:
            self.window.destroy()
        except tk.TclError:
            # CORREÇÃO: Exception específica - window já pode estar destruída
            pass
        import os
        os._exit(0)
    
    def run(self):
        print("GeminiCat iniciado!")
        print("Controles:")
        print("  - Clique esquerdo: deixar feliz")
        print("  - Clique direito: chat")
        print("  - Arrastar: mover GeminiCat")
        print("  - ESC: sair")
        print("  - GeminiCat dorme se não interagir por 30s")
        
        try:
            self.window.mainloop()
        except KeyboardInterrupt:
            print("\nCtrl+C detectado - encerrando GeminiCat...")
            self.quit()
        finally:
            self.quit()

if __name__ == "__main__":
    try:
        app = CatDesktopApp()
        app.run()
    except KeyboardInterrupt:
        print("\nCtrl+C detectado - encerrando...")
        import os
        os._exit(0)
    except Exception as e:
        logger.critical(f"Erro ao iniciar: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")
        import os
        os._exit(0)