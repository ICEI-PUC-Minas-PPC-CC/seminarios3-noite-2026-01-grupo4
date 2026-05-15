import pygame
import sys
import os
import json
import urllib.request
import urllib.error
import webbrowser
import pathlib
import shutil
from dataclasses import dataclass

# Iniciar pygame
pygame.init()

# Inicializa em modo janela redimensionável
windowed_width, windowed_height = 1280, 720
fullscreen = False

tela = pygame.display.set_mode((windowed_width, windowed_height), pygame.RESIZABLE)
largura, altura = tela.get_size()
pygame.display.set_caption("Detetive das Virtudes")

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AZUL = (100, 150, 255)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)

# Fontes
fonte_titulo = pygame.font.SysFont("arial", 50, bold=True)
fonte_texto = pygame.font.SysFont("arial", 32)
fonte_opcoes = pygame.font.SysFont("arial", 28, bold=True)
fonte_feedback = pygame.font.SysFont("arial", 28, bold=True)
fonte_pequena = pygame.font.SysFont("arial", 22)

# Imagens fallback
fundo_caso = pygame.image.load("src/backgrounds/lamen.png")
fundo_caso = pygame.transform.scale(fundo_caso, (largura, altura))

fundo_virtude = pygame.image.load("src/backgrounds/virtude.png")
fundo_virtude = pygame.transform.scale(fundo_virtude, (largura, altura))

menu_background_path = "src/backgrounds/menu.png"
if os.path.exists(menu_background_path):
    fundo_menu = pygame.image.load(menu_background_path)
    fundo_menu = pygame.transform.scale(fundo_menu, (largura, altura))
else:
    fundo_menu = None

# Cache das imagens específicas por caso
imagens_cache = {}

LIBRAS_CACHE_DIR = os.path.join("src", "libras_cache")
LIBRAS_CACHE_IMAGES_DIR = os.path.join(LIBRAS_CACHE_DIR, "images")
LIBRAS_CACHE_MAOS_JSON = os.path.join(LIBRAS_CACHE_DIR, "mao.json")
LIBRAS_CACHE_MAOS_DIR = os.path.join(LIBRAS_CACHE_DIR, "mao")
LIBRAS_CACHE_VIDEOS_DIR = os.path.join(LIBRAS_CACHE_DIR, "videos")
LIBRAS_CACHE_PALAVRAS_JSON = os.path.join(LIBRAS_CACHE_DIR, "palavras.json")
LIBRAS_URL_PALAVRAS_JS = "https://dicionario.ines.gov.br/public/site/js/palavras.js"
LIBRAS_URL_MAOS_JS = "https://dicionario.ines.gov.br/public/site/js/mao.js"
LIBRAS_URL_IMAGENS_BASE = "https://dicionario.ines.gov.br/public/media/palavras/images/"
LIBRAS_URL_MAOS_BASE = "https://dicionario.ines.gov.br/public/media/mao/"
LIBRAS_URL_VIDEOS_BASE = "https://dicionario.ines.gov.br/public/media/palavras/videos/"


@dataclass(frozen=True)
class LibrasVerbete:
    id: int
    letra: str
    palavra: str
    image: str | None
    descricao: str | None
    mao_id: int | None
    video: str | None


def _http_get_text(url: str, timeout: float = 20.0) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html,application/javascript,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _http_download_file(url: str, dest_path: str, timeout: float = 30.0) -> None:
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())


def _scale_to_fit(img: pygame.Surface, max_w: int, max_h: int) -> pygame.Surface:
    """
    Mantém proporção e garante que a imagem caiba em (max_w, max_h).
    """
    if max_w <= 0 or max_h <= 0:
        return img
    w, h = img.get_size()
    if w <= 0 or h <= 0:
        return img
    escala = min(max_w / w, max_h / h, 1.0)
    if escala == 1.0:
        return img
    return pygame.transform.smoothscale(img, (max(1, int(w * escala)), max(1, int(h * escala))))


def carregar_verbetes_libras() -> list[LibrasVerbete]:
    """
    Carrega o índice de verbetes do dicionário do INES.
    Faz cache local em `src/libras_cache/palavras.json` para não depender de rede toda vez.
    """
    os.makedirs(LIBRAS_CACHE_DIR, exist_ok=True)
    if os.path.exists(LIBRAS_CACHE_PALAVRAS_JSON):
        try:
            with open(LIBRAS_CACHE_PALAVRAS_JSON, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return [
                LibrasVerbete(
                    id=int(v.get("id", 0)),
                    letra=str(v.get("letra", "")).upper()[:1],
                    palavra=str(v.get("palavra", "")).strip(),
                    image=v.get("image"),
                    descricao=v.get("descricao"),
                    mao_id=int(v["mao"]) if v.get("mao") is not None else None,
                    video=v.get("video"),
                )
                for v in raw
                if v.get("palavra")
            ]
        except Exception:
            pass

    js = _http_get_text(LIBRAS_URL_PALAVRAS_JS)
    prefix = "var palavras = "
    if not js.startswith(prefix):
        raise RuntimeError("Formato inesperado ao baixar lista de palavras (INES).")
    payload = js[len(prefix) :].strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    raw = json.loads(payload)

    with open(LIBRAS_CACHE_PALAVRAS_JSON, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False)

    return [
        LibrasVerbete(
            id=int(v.get("id", 0)),
            letra=str(v.get("letra", "")).upper()[:1],
            palavra=str(v.get("palavra", "")).strip(),
            image=v.get("image"),
            descricao=v.get("descricao"),
            mao_id=int(v["mao"]) if v.get("mao") is not None else None,
            video=v.get("video"),
        )
        for v in raw
        if v.get("palavra")
    ]


def carregar_maos_libras() -> dict[int, str]:
    """
    Carrega o mapeamento de "configuração de mão" (id -> arquivo jpg) do INES.
    Cache em `src/libras_cache/mao.json`.
    """
    os.makedirs(LIBRAS_CACHE_DIR, exist_ok=True)
    if os.path.exists(LIBRAS_CACHE_MAOS_JSON):
        try:
            with open(LIBRAS_CACHE_MAOS_JSON, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return {int(v["id"]): str(v["url"]) for v in raw if v.get("id") and v.get("url")}
        except Exception:
            pass

    js = _http_get_text(LIBRAS_URL_MAOS_JS)
    prefix = "var mao = "
    if not js.startswith(prefix):
        raise RuntimeError("Formato inesperado ao baixar mapeamento de mão (INES).")
    payload = js[len(prefix) :].strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    raw = json.loads(payload)
    with open(LIBRAS_CACHE_MAOS_JSON, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False)
    return {int(v["id"]): str(v["url"]) for v in raw if v.get("id") and v.get("url")}


def garantir_imagem_mao_libras(nome_arquivo: str) -> str:
    os.makedirs(LIBRAS_CACHE_MAOS_DIR, exist_ok=True)
    dest = os.path.join(LIBRAS_CACHE_MAOS_DIR, nome_arquivo)
    if os.path.exists(dest):
        return dest
    url = LIBRAS_URL_MAOS_BASE + nome_arquivo
    _http_download_file(url, dest)
    return dest


def garantir_video_libras(nome_arquivo: str) -> str:
    os.makedirs(LIBRAS_CACHE_VIDEOS_DIR, exist_ok=True)
    dest = os.path.join(LIBRAS_CACHE_VIDEOS_DIR, nome_arquivo)
    if os.path.exists(dest):
        return dest
    url = LIBRAS_URL_VIDEOS_BASE + nome_arquivo
    _http_download_file(url, dest)
    return dest


def limpar_cache_libras():
    """
    Remove o cache local do glossário para não acumular imagens/vídeos no disco.
    """
    try:
        shutil.rmtree(LIBRAS_CACHE_DIR, ignore_errors=True)
    except Exception:
        # Se falhar (arquivo em uso/permissão), não deve impedir o fechamento do jogo
        pass

def garantir_imagem_libras(nome_arquivo: str) -> str:
    """
    Garante que a imagem do verbete existe no cache e retorna o caminho local.
    """
    os.makedirs(LIBRAS_CACHE_IMAGES_DIR, exist_ok=True)
    dest = os.path.join(LIBRAS_CACHE_IMAGES_DIR, nome_arquivo)
    if os.path.exists(dest):
        return dest
    url = LIBRAS_URL_IMAGENS_BASE + nome_arquivo
    _http_download_file(url, dest)
    return dest


def desenhar_botao(rect: pygame.Rect, texto: str, cor_fundo: tuple[int, int, int], cor_borda=BRANCO):
    pygame.draw.rect(tela, cor_fundo, rect, border_radius=12)
    pygame.draw.rect(tela, cor_borda, rect, 3, border_radius=12)
    surf = fonte_opcoes.render(texto, True, BRANCO)
    tela.blit(surf, (rect.x + (rect.width - surf.get_width()) // 2, rect.y + (rect.height - surf.get_height()) // 2))


def desenhar_texto_centralizado(texto: str, y: int, fonte, cor=BRANCO):
    surf = fonte.render(texto, True, cor)
    tela.blit(surf, (largura // 2 - surf.get_width() // 2, y))


def desenhar_botao_pequeno(rect: pygame.Rect, texto: str, cor_fundo: tuple[int, int, int], cor_borda=BRANCO):
    pygame.draw.rect(tela, cor_fundo, rect, border_radius=10)
    pygame.draw.rect(tela, cor_borda, rect, 2, border_radius=10)
    surf = fonte_pequena.render(texto, True, BRANCO)
    tela.blit(surf, (rect.x + (rect.width - surf.get_width()) // 2, rect.y + (rect.height - surf.get_height()) // 2))


def obter_grade_letras_rects() -> dict[str, pygame.Rect]:
    """
    Retorna retângulos das letras A-Z centralizados na janela,
    mantendo proporção e funcionando tanto em tela cheia quanto janela.
    """
    cols = 9
    gap = 10
    w = 70
    h = 52
    letras = [chr(ord("A") + i) for i in range(26)]
    rows = (len(letras) + cols - 1) // cols
    grid_h = rows * h + (rows - 1) * gap

    top_margin = 170
    bottom_margin = 60
    available_h = max(0, altura - top_margin - bottom_margin)
    start_y = top_margin + max(0, (available_h - grid_h) // 2)

    rects: dict[str, pygame.Rect] = {}
    for row in range(rows):
        start_idx = row * cols
        end_idx = min(start_idx + cols, len(letras))
        row_count = end_idx - start_idx
        row_w = row_count * w + (row_count - 1) * gap
        start_x = (largura - row_w) // 2
        for col in range(row_count):
            idx = start_idx + col
            letra = letras[idx]
            r = pygame.Rect(start_x + col * (w + gap), start_y + row * (h + gap), w, h)
            rects[letra] = r
    return rects


def desenhar_mensagem_erro(texto: str):
    overlay = pygame.Surface((largura, altura), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    tela.blit(overlay, (0, 0))
    desenhar_texto_centralizado("Glossário de Libras (INES)", 60, fonte_titulo, BRANCO)
    render_texto_quebrado(texto, fonte_texto, BRANCO, tela, 80, 180, largura - 160)

def get_imagem_caso(caso_index):
    """Carrega imagem específica do caso (com fallback)"""
    caminho = casos[caso_index].get("imagem_caso", "src/backgrounds/lamen.png")
    if caminho not in imagens_cache:
        if os.path.exists(caminho):
            img = pygame.image.load(caminho)
            imagens_cache[caminho] = pygame.transform.scale(img, (largura, altura))
        else:
            imagens_cache[caminho] = fundo_caso
    return imagens_cache[caminho]

def get_imagem_virtude(caso_index):
    """Carrega imagem específica da virtude (com fallback)"""
    caminho = casos[caso_index].get("imagem_virtude", "src/backgrounds/virtude.png")
    if caminho not in imagens_cache:
        if os.path.exists(caminho):
            img = pygame.image.load(caminho)
            imagens_cache[caminho] = pygame.transform.scale(img, (largura, altura))
        else:
            imagens_cache[caminho] = fundo_virtude
    return imagens_cache[caminho]


def atualizar_imagens():
    global fundo_caso, fundo_virtude, fundo_menu, imagens_cache

    imagens_cache.clear()
    fundo_caso = pygame.image.load("src/backgrounds/lamen.png")
    fundo_caso = pygame.transform.scale(fundo_caso, (largura, altura))

    fundo_virtude = pygame.image.load("src/backgrounds/virtude.png")
    fundo_virtude = pygame.transform.scale(fundo_virtude, (largura, altura))

    if os.path.exists(menu_background_path):
        fundo_menu = pygame.image.load(menu_background_path)
        fundo_menu = pygame.transform.scale(fundo_menu, (largura, altura))
    else:
        fundo_menu = None


def atualizar_botoes_caso():
    global botoes
    botoes.clear()
    largura_botao = min(880, largura - 80)
    for i in range(len(casos[caso_atual]["opcoes"])):
        x = 40
        y = 280 + i * 120
        altura_botao = 100
        retangulo = pygame.Rect(x, y, largura_botao, altura_botao)
        botoes.append({"rect": retangulo})


def atualizar_layout():
    global botao_jogar, botao_sair, botao_fullscreen, botao_glossario, botao_tentar, seta_x, seta_y, seta_rect

    botao_jogar = pygame.Rect(largura // 2 - 150, altura // 2 - 120, 300, 70)
    botao_glossario = pygame.Rect(largura // 2 - 150, altura // 2 - 30, 300, 70)
    botao_fullscreen = pygame.Rect(largura // 2 - 150, altura // 2 + 60, 300, 70)
    botao_sair = pygame.Rect(largura // 2 - 150, altura // 2 + 150, 300, 70)
    botao_tentar = pygame.Rect(largura // 2 - 150, altura // 2 + 150, 300, 60)

    seta_x = largura - 120
    seta_y = altura - 80
    seta_rect = pygame.Rect(seta_x - seta_tamanho, seta_y - seta_tamanho, seta_tamanho * 2, seta_tamanho * 2)

    atualizar_botoes_caso()


def atualizar_tela():
    global tela, largura, altura
    if fullscreen:
        tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        largura, altura = tela.get_size()
    else:
        tela = pygame.display.set_mode((windowed_width, windowed_height), pygame.RESIZABLE)
        largura, altura = tela.get_size()
    atualizar_imagens()
    atualizar_layout()


def render_texto_quebrado(texto, fonte, cor, superficie, x, y, largura_max, espaco_linha=None):
    if espaco_linha is None:
        espaco_linha = fonte.get_height() + 8
    palavras = texto.split(' ')
    linha_atual = ""
    for palavra in palavras:
        teste = f"{linha_atual}{palavra} "
        if fonte.size(teste)[0] > largura_max and linha_atual:
            superficie.blit(fonte.render(linha_atual.strip(), True, cor), (x, y))
            y += espaco_linha
            linha_atual = palavra + " "
        else:
            linha_atual = teste
    if linha_atual.strip():
        superficie.blit(fonte.render(linha_atual.strip(), True, cor), (x, y))
    return y

# Dados dos casos
casos =[
    {
        "titulo": "Caso 1: O lamen do ichiraku",
        "descricao": "Voc encontra um lamen na mesa ao lado. Ninguém está vendo. O que você faz?",
        "imagem_caso": "src/backgrounds/lamen.png",
        "imagem_virtude": "src/backgrounds/HE.png",
        "opcoes": [
            "1-Levar o lamen para casa, ninguém está olhando",
            "2-Procurar o dono ou avisar o ichiraku",
            "3-Esconder o lamenpara que ninguém o encontre",
        ],
        "resposta_correta": 1,
        "virtude": "Honestidade",
        "explicacao": "A honestidade é fazer o certo mesmo quando ninguém está olhando. Procurar o dono mostra que você valoriza a verdade. Cada ato honesto constrói um caráter forte!",
        "licao_errada": "Levar algo que não é seu ou esconder é roubo. Isso machuca quem perdeu o objeto e prejudica sua própria alma."
    },
    {
        "titulo": "Caso 2: A moeda do Bruxo",
        "descricao": "Voce esta em uma estrada de lama fazendo um treinamento de duelos para entrar na cavalaria e consegue desarmar seu oponente. Voce pode mostrar a todos que é melhor que ele. O que você faz?",
        "imagem_caso": "src/backgrounds/caso2thewitcher.png",
        "imagem_virtude": "src/backgrounds/respeito.png",  
        "opcoes": [
            "1-Rir do seu oponente",
            "2-Guardar sua espada e oferecer sua ajuda para ele se levantar",
            "3-Fazer piada do seu oponente para mostrar que é melhor",
        ],
        "resposta_correta": 1,
        "virtude": "Respeito",
        "explicacao": "Entender que todos merecem respeito, mesmo em competição, é fundamental. Oferecer ajuda mostra que você valoriza a dignidade do outro, enquanto rir  ou fazer piada demonstra falta de respeito e empatia.",
        "licao_errada": "Rir ou fazer piada do oponente é desrespeitoso e prejudica a confiança e o espírito esportivo. Oferecer ajuda mostra que você valoriza a dignidade do outro, mesmo em competição."
    },
    {
        "titulo": "Caso 3: O tesouro do pirata",
        "descricao": "Você encontra um baú de tesouro em uma ilha deserta",
        "imagem_caso": "src/backgrounds/pirata.png",
        "imagem_virtude": "src/backgrounds/pirata_rum.png",
        "opcoes": [
            "1-Pegar o baú inteiro para si mesmo",
            "2-Pegar apenas o que você acha que merece",
            "3-Deixar o baú onde está, respeitando a placa",
        ],
        "resposta_correta": 2,
        "virtude": "Coragem",
        "explicacao": "A coragem é enfrentar desafios e fazer o que é certo,esmo quando é difícil. Pegar apenas o que merece mostra que você tem a coragem de ser justo e honesto, mesmo quando ninguém está olhando.",
        "licao_errada": "Pegar tudo para si é ganância e falta deoragem para ser justo. Deixar o baú inteiro pode ser visto como covardia, pois você não tem a coragem de reivindicar o que é seu." 

    },
    {
        "titulo": "Caso 4: O Lanche na Praca",
        "descricao": "O sorvete do Leo caiu no chao. O que o amigo dele pode fazer?",
        "imagem_caso": "src/backgrounds/praca_pocos.jpg",
        "imagem_virtude": "src/backgrounds/amizade.jpg",
        "opcoes": [
            "1-Rir do Leo apontando o dedo.",
            "2-Dividir o seu proprio sorvete com ele.",
            "3-Ir brincar sozinho no parquinho."
        ],
        "resposta_correta": 1,
        "virtude": "Amizade",
        "explicacao": "Amigos de verdade dividem as coisas e apoiam nos momentos dificeis! Ajudar um amigo triste mostra o verdadeiro valor da amizade.",
        "licao_errada": "Rir do azar do amigo ou abandona-lo o deixa mais triste. Amigos de verdade nao fazem isso, eles ajudam."
    },
    {
        "titulo": "Caso 5: O Colega Novo",
        "descricao": "O Lucas e novo na escola e ainda nao conhece ninguem. Como podemos ajudar?",
        "imagem_caso": "src/backgrounds/patio_escola.jpg",
        "imagem_virtude": "src/backgrounds/empatia.jpg",
        "opcoes": [
            "1-Ignorar e continuar brincando so com os amigos de sempre.",
            "2-Fazer um sinal de 'Oi' e chamar ele para o jogo.",
            "3-Ficar olhando de longe sem falar nada."
        ],
        "resposta_correta": 1,
        "virtude": "Empatia",
        "explicacao": "Empatia e se colocar no lugar do outro e acolher. Chamar um colega novo para brincar faz ele se sentir bem-vindo e seguro!",
        "licao_errada": "Ignorar ou apenas olhar faz o colega novo se sentir sozinho e excluido. Tente sempre se colocar no lugar do outro."
    },
    {
        "titulo": "Caso 6: O Dever de Casa",
        "descricao": "Pedro tem um trabalho importante para entregar amanha, mas seus amigos o chamaram para jogar videogame. O que ele deve fazer??",
        "imagem_caso": "src/backgrounds/COLOCA_AQUI_IMAGEM.PNG",
        "imagem_virtude": "src/backgrounds/empatia.jpg",
        "opcoes": [
            "1-Ir jogar e deixar o trabalho para depois",
            "2-Terminar o trabalho primeiro e depois jogar se sobrar tempo",
            "3-Pedir para um colega fazer o trabalho por ele",
        ],
        "resposta_correta": 1,
        "virtude": "Responsabilidade",
        "explicacao": "Responsabilidade e cumprir com seus compromissos mesmo quando surgem distracoes. Terminar o trabalho primeiro garante que voce honre seus deveres sem prejudicar seu aprendizado.",
        "licao_errada": "DAR LICAO DE MORAL AQUI NICK ."
    }
]

# Estado do jogo
caso_atual = 0
estado = "menu"
feedback = ""
botao_errado_index = -1

# Criar botões iniciais e layout responsivo
botoes = []
botao_jogar = pygame.Rect(0, 0, 0, 0)
botao_sair = pygame.Rect(0, 0, 0, 0)
botao_fullscreen = pygame.Rect(0, 0, 0, 0)
botao_glossario = pygame.Rect(0, 0, 0, 0)
botao_tentar = pygame.Rect(0, 0, 0, 0)

# Seta para avançar
seta_x = 0
seta_y = 0
seta_tamanho = 50
seta_rect = pygame.Rect(0, 0, 0, 0)

atualizar_imagens()
atualizar_layout()

verbetes_libras: list[LibrasVerbete] = []
verbetes_por_letra: dict[str, list[LibrasVerbete]] = {}
letra_selecionada: str | None = None
indice_scroll_palavras = 0
verbete_selecionado: LibrasVerbete | None = None
imagem_verbete_surface: pygame.Surface | None = None
mao_surface: pygame.Surface | None = None
mao_por_id: dict[int, str] = {}
video_disponivel: str | None = None
botao_assistir_video = pygame.Rect(0, 0, 0, 0)
glossario_erro: str | None = None


def abrir_glossario_libras():
    global estado, verbetes_libras, verbetes_por_letra, letra_selecionada, indice_scroll_palavras
    global verbete_selecionado, imagem_verbete_surface, mao_surface, mao_por_id, video_disponivel, glossario_erro
    estado = "glossario_letra"
    letra_selecionada = None
    indice_scroll_palavras = 0
    verbete_selecionado = None
    imagem_verbete_surface = None
    mao_surface = None
    video_disponivel = None
    glossario_erro = None

    try:
        verbetes_libras = carregar_verbetes_libras()
        mao_por_id = carregar_maos_libras()
        verbetes_por_letra = {}
        for v in verbetes_libras:
            if v.letra and "A" <= v.letra <= "Z":
                verbetes_por_letra.setdefault(v.letra, []).append(v)
        for k in verbetes_por_letra:
            verbetes_por_letra[k].sort(key=lambda x: x.palavra.lower())
    except (urllib.error.URLError, TimeoutError):
        glossario_erro = "Não consegui acessar o dicionário do INES. Verifique sua internet e tente novamente."
    except Exception:
        glossario_erro = "O glossário falhou ao carregar. Tente novamente."


def carregar_detalhes_do_verbete(v: LibrasVerbete):
    global imagem_verbete_surface, mao_surface, video_disponivel, glossario_erro
    imagem_verbete_surface = None
    mao_surface = None
    video_disponivel = None
    glossario_erro = None

    # Vídeo: se existir no JSON, já habilita o botão (download só ao clicar)
    if v.video:
        video_disponivel = v.video

    # Imagem do verbete (se não existir no servidor, apenas fica None)
    if v.image:
        try:
            caminho = garantir_imagem_libras(v.image)
            img = pygame.image.load(caminho)
            imagem_verbete_surface = img
        except urllib.error.HTTPError as e:
            if getattr(e, "code", None) == 404:
                imagem_verbete_surface = None
            else:
                glossario_erro = "Falha ao baixar a imagem do INES."
        except (urllib.error.URLError, TimeoutError):
            glossario_erro = "Não consegui acessar o INES para baixar a imagem. Verifique sua internet."
        except Exception:
            imagem_verbete_surface = None

    # Mão (também não deve bloquear caso falhe)
    if v.mao_id is not None and v.mao_id in mao_por_id:
        try:
            arquivo = mao_por_id[v.mao_id]
            caminho_mao = garantir_imagem_mao_libras(arquivo)
            img_mao = pygame.image.load(caminho_mao)
            mao_surface = img_mao
        except urllib.error.HTTPError as e:
            if getattr(e, "code", None) == 404:
                mao_surface = None
            else:
                glossario_erro = glossario_erro or "Falha ao baixar a imagem de mão do INES."
        except (urllib.error.URLError, TimeoutError):
            glossario_erro = glossario_erro or "Não consegui acessar o INES para baixar a mão. Verifique sua internet."
        except Exception:
            mao_surface = None


def desenhar_seta():
    pontos = [
        (seta_x + seta_tamanho, seta_y),
        (seta_x - seta_tamanho, seta_y - seta_tamanho),
        (seta_x - seta_tamanho, seta_y + seta_tamanho),
    ]
    pygame.draw.polygon(tela, VERDE, pontos)
    pygame.draw.polygon(tela, BRANCO, pontos, 3)

def resetar_caso():
    global estado, feedback, botao_errado_index, botoes
    
    botoes.clear()
    for i in range(len(casos[caso_atual]["opcoes"])):
        x = 40
        y = 280 + i * 120
        largura_botao = 880
        altura_botao = 100
        retangulo = pygame.Rect(x, y, largura_botao, altura_botao)
        botoes.append({"rect": retangulo})
    
    estado = "caso"
    feedback = ""
    botao_errado_index = -1

# Loop principal
rodando = True
clock = pygame.time.Clock()

try:
    while rodando:
        # Fundo específico por caso ou menu
        if estado == "caso" or estado == "resposta_incorreta":
            fundo_atual = get_imagem_caso(caso_atual)
            tela.blit(fundo_atual, (0, 0))
        elif estado == "virtude":
            fundo_atual = get_imagem_virtude(caso_atual)
            tela.blit(fundo_atual, (0, 0))
        elif estado == "menu":
            if fundo_menu:
                tela.blit(fundo_menu, (0, 0))
            else:
                tela.fill((20, 20, 40))
        elif estado.startswith("glossario"):
            tela.fill((20, 20, 40))

        if estado == "menu":
            titulo_menu = fonte_titulo.render("Detetive das Virtudes", True, BRANCO)
            instrucao_menu = fonte_texto.render("Jogar, Glossário de Libras (INES), Tela Cheia ou Sair.", True, BRANCO)

            tela.blit(titulo_menu, (largura // 2 - titulo_menu.get_width() // 2, 120))
            tela.blit(instrucao_menu, (largura // 2 - instrucao_menu.get_width() // 2, 190))
            desenhar_botao(botao_jogar, "Jogar", AZUL)
            desenhar_botao(botao_glossario, "Glossário Libras", AZUL)
            desenhar_botao(botao_fullscreen, "Tela Cheia", VERDE if fullscreen else AZUL)
            desenhar_botao(botao_sair, "Sair", VERMELHO)
        elif estado == "caso":
            # Painel de contraste para a área de texto
            painel_texto = pygame.Surface((940, 520), pygame.SRCALPHA)
            painel_texto.fill((0, 0, 0, 170))
            tela.blit(painel_texto, (20, 20))

            texto_titulo = fonte_titulo.render(casos[caso_atual]["titulo"], True, BRANCO)
            tela.blit(texto_titulo, (40, 40))

            render_texto_quebrado(casos[caso_atual]["descricao"], fonte_texto, BRANCO, tela, 40, 120, 900)

            for i, botao in enumerate(botoes):
                cor = VERMELHO if botao_errado_index == i else AZUL
                pygame.draw.rect(tela, cor, botao["rect"], border_radius=12)
                pygame.draw.rect(tela, BRANCO, botao["rect"], 3, border_radius=12)
                render_texto_quebrado(
                    casos[caso_atual]["opcoes"][i],
                    fonte_opcoes,
                    BRANCO,
                    tela,
                    botao["rect"].x + 20,
                    botao["rect"].y + 15,
                    botao["rect"].width - 40,
                    fonte_opcoes.get_height() + 6,
                )

            if feedback and "Correto" in feedback:
                texto_feedback = fonte_feedback.render(feedback, True, VERDE)
                fundo_feedback = pygame.Surface((texto_feedback.get_width() + 40, texto_feedback.get_height() + 20), pygame.SRCALPHA)
                fundo_feedback.fill((0, 0, 0, 180))
                tela.blit(fundo_feedback, (20, 460))
                tela.blit(texto_feedback, (40, 470))
                desenhar_seta()

        elif estado == "virtude":
            painel_virtude = pygame.Surface((1300, 520), pygame.SRCALPHA)
            painel_virtude.fill((0, 0, 0, 180))
            tela.blit(painel_virtude, (300, 80))

            titulo_virtude = f"Virtude: {casos[caso_atual]['virtude']}"
            texto_titulo = fonte_titulo.render(titulo_virtude, True, BRANCO)
            tela.blit(texto_titulo, (340, 110))

            y = 200
            y = render_texto_quebrado(casos[caso_atual]["explicacao"], fonte_texto, BRANCO, tela, 340, y, 1200)

            desenhar_seta()

        elif estado == "resposta_incorreta":
            overlay = pygame.Surface((largura, altura))
            overlay.set_alpha(200)
            overlay.fill(PRETO)
            tela.blit(overlay, (0, 0))

            caixa_x = largura // 2 - 300
            caixa_y = altura // 2 - 200
            caixa_largura = 600
            caixa_altura = 400

            pygame.draw.rect(tela, PRETO, (caixa_x, caixa_y, caixa_largura, caixa_altura))
            pygame.draw.rect(tela, VERMELHO, (caixa_x, caixa_y, caixa_largura, caixa_altura), 5)

            titulo_erro = fonte_titulo.render("Resposta Incorreta!", True, VERMELHO)
            tela.blit(titulo_erro, (caixa_x + 100, caixa_y + 30))

            licao = casos[caso_atual]["licao_errada"]
            palavras = licao.split()
            y = caixa_y + 120
            linha_atual = ""

            for palavra in palavras:
                if len(linha_atual) + len(palavra) > 40:
                    texto_linha = fonte_texto.render(linha_atual.strip(), True, BRANCO)
                    tela.blit(texto_linha, (caixa_x + 30, y))
                    y += fonte_texto.get_height() + 10
                    linha_atual = palavra + " "
                else:
                    linha_atual += palavra + " "

            if linha_atual.strip():
                texto_linha = fonte_texto.render(linha_atual.strip(), True, BRANCO)
                tela.blit(texto_linha, (caixa_x + 30, y))

            pygame.draw.rect(tela, (0, 150, 0), botao_tentar)
            texto_botao = fonte_opcoes.render("Tentar Novamente", True, BRANCO)
            tela.blit(texto_botao, (botao_tentar.x + 30, botao_tentar.y + 15))

        elif estado == "glossario_letra":
            desenhar_texto_centralizado("Glossário de Libras (INES)", 40, fonte_titulo, BRANCO)
            desenhar_texto_centralizado("Escolha uma letra (A-Z). Esc para voltar ao menu.", 110, fonte_pequena, BRANCO)

            if glossario_erro:
                desenhar_mensagem_erro(glossario_erro)
            else:
                rects = obter_grade_letras_rects()
                for letra, r in rects.items():
                    cor = AZUL if letra in verbetes_por_letra else (60, 60, 60)
                    desenhar_botao(r, letra, cor)

        elif estado == "glossario_palavra":
            desenhar_texto_centralizado("Glossário de Libras (INES)", 30, fonte_titulo, BRANCO)
            desenhar_texto_centralizado(f"Letra: {letra_selecionada}  |  Clique em uma palavra. Rodinha do mouse para rolar. Esc para voltar.", 95, fonte_pequena, BRANCO)

            if glossario_erro:
                desenhar_mensagem_erro(glossario_erro)
            else:
                lista = verbetes_por_letra.get(letra_selecionada or "", [])
                if not lista:
                    desenhar_texto_centralizado("Nenhuma palavra encontrada para esta letra.", 220, fonte_texto, BRANCO)
                else:
                    area_x = 60
                    area_y = 150
                    area_w = 420
                    area_h = altura - 220
                    pygame.draw.rect(tela, (0, 0, 0), (area_x, area_y, area_w, area_h))
                    pygame.draw.rect(tela, BRANCO, (area_x, area_y, area_w, area_h), 2)

                    itens_por_pagina = max(5, (area_h - 30) // 44)
                    indice_scroll_palavras = max(0, min(indice_scroll_palavras, max(0, len(lista) - itens_por_pagina)))
                    visiveis = lista[indice_scroll_palavras : indice_scroll_palavras + itens_por_pagina]

                    for i, v in enumerate(visiveis):
                        y = area_y + 15 + i * 44
                        rect_item = pygame.Rect(area_x + 10, y, area_w - 20, 38)
                        selecionado = verbete_selecionado and verbete_selecionado.id == v.id
                        pygame.draw.rect(tela, (40, 90, 180) if selecionado else (30, 30, 30), rect_item, border_radius=8)
                        pygame.draw.rect(tela, BRANCO, rect_item, 2, border_radius=8)
                        txt = fonte_pequena.render(v.palavra, True, BRANCO)
                        tela.blit(txt, (rect_item.x + 12, rect_item.y + 8))

                    # painel da imagem
                    painel_x = 520
                    painel_y = 150
                    painel_w = largura - painel_x - 60
                    painel_h = altura - 220
                    pygame.draw.rect(tela, (0, 0, 0), (painel_x, painel_y, painel_w, painel_h))
                    pygame.draw.rect(tela, BRANCO, (painel_x, painel_y, painel_w, painel_h), 2)

                    if verbete_selecionado:
                        title = fonte_texto.render(verbete_selecionado.palavra, True, BRANCO)
                        tela.blit(title, (painel_x + 20, painel_y + 15))
                        # Acepção / descrição
                        if verbete_selecionado.descricao:
                            render_texto_quebrado(
                                verbete_selecionado.descricao,
                                fonte_pequena,
                                BRANCO,
                                tela,
                                painel_x + 20,
                                painel_y + 65,
                                painel_w - 40,
                                fonte_pequena.get_height() + 6,
                            )

                        # caixas de imagem (verbete + mão)
                        caixa_y = painel_y + 170
                        caixa_h = max(220, painel_h - 300)
                        caixa_w = (painel_w - 60) // 2
                        caixa1 = pygame.Rect(painel_x + 20, caixa_y, caixa_w, caixa_h)
                        caixa2 = pygame.Rect(painel_x + 40 + caixa_w, caixa_y, caixa_w, caixa_h)
                        pygame.draw.rect(tela, (15, 15, 15), caixa1, border_radius=10)
                        pygame.draw.rect(tela, BRANCO, caixa1, 2, border_radius=10)
                        pygame.draw.rect(tela, (15, 15, 15), caixa2, border_radius=10)
                        pygame.draw.rect(tela, BRANCO, caixa2, 2, border_radius=10)

                        label1 = fonte_pequena.render("Imagem", True, BRANCO)
                        label2 = fonte_pequena.render("Mão", True, BRANCO)
                        tela.blit(label1, (caixa1.x + 10, caixa1.y + 8))
                        tela.blit(label2, (caixa2.x + 10, caixa2.y + 8))

                        if imagem_verbete_surface:
                            inner = caixa1.inflate(-20, -60)
                            inner.y += 35
                            inner.height -= 35
                            img = _scale_to_fit(imagem_verbete_surface, inner.width, inner.height)
                            tela.blit(img, (inner.x + (inner.width - img.get_width()) // 2, inner.y + (inner.height - img.get_height()) // 2))
                        else:
                            render_texto_quebrado(
                                "Sem imagem para este verbete.",
                                fonte_pequena,
                                BRANCO,
                                tela,
                                caixa1.x + 10,
                                caixa1.y + 60,
                                caixa1.width - 20,
                            )

                        if mao_surface:
                            inner = caixa2.inflate(-20, -60)
                            inner.y += 35
                            inner.height -= 35
                            imgm = _scale_to_fit(mao_surface, inner.width, inner.height)
                            tela.blit(imgm, (inner.x + (inner.width - imgm.get_width()) // 2, inner.y + (inner.height - imgm.get_height()) // 2))
                        else:
                            render_texto_quebrado(
                                "Sem imagem de mão para este verbete.",
                                fonte_pequena,
                                BRANCO,
                                tela,
                                caixa2.x + 10,
                                caixa2.y + 60,
                                caixa2.width - 20,
                            )

                        # vídeo (botão)
                        botao_assistir_video = pygame.Rect(painel_x + 20, painel_y + painel_h - 70, 240, 50)
                        if video_disponivel:
                            desenhar_botao_pequeno(botao_assistir_video, "Assistir vídeo", VERDE)
                        else:
                            desenhar_botao_pequeno(botao_assistir_video, "Sem vídeo", (70, 70, 70))

                        if glossario_erro:
                            render_texto_quebrado(glossario_erro, fonte_pequena, BRANCO, tela, painel_x + 290, painel_y + painel_h - 62, painel_w - 310)
                    else:
                        render_texto_quebrado("Escolha uma palavra na lista à esquerda.", fonte_pequena, BRANCO, tela, painel_x + 20, painel_y + 100, painel_w - 40)

        pygame.display.update()
        clock.tick(60)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.VIDEORESIZE and not fullscreen:
                windowed_width, windowed_height = evento.w, evento.h
                atualizar_tela()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE and fullscreen:
                    fullscreen = False
                    atualizar_tela()
                elif evento.key == pygame.K_ESCAPE and estado.startswith("glossario"):
                    if estado == "glossario_palavra":
                        estado = "glossario_letra"
                        verbete_selecionado = None
                        imagem_verbete_surface = None
                        mao_surface = None
                        video_disponivel = None
                        glossario_erro = None
                    else:
                        estado = "menu"
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if estado == "menu":
                    if botao_jogar.collidepoint(mouse_x, mouse_y):
                        estado = "caso"
                    elif botao_glossario.collidepoint(mouse_x, mouse_y):
                        abrir_glossario_libras()
                    elif botao_sair.collidepoint(mouse_x, mouse_y):
                        rodando = False
                    elif botao_fullscreen.collidepoint(mouse_x, mouse_y):
                        fullscreen = not fullscreen
                        atualizar_tela()
                elif estado == "caso":
                    for i, botao in enumerate(botoes):
                        if botao["rect"].collidepoint(mouse_x, mouse_y):
                            if i == casos[caso_atual]["resposta_correta"]:
                                feedback = f"Correto! Virtude: {casos[caso_atual]['virtude']}"
                            else:
                                botao_errado_index = i
                                estado = "resposta_incorreta"
                                feedback = ""
                            break

                    if feedback and "Correto" in feedback and seta_rect.collidepoint(mouse_x, mouse_y):
                        estado = "virtude"
                elif estado == "virtude":
                    if seta_rect.collidepoint(mouse_x, mouse_y):
                        caso_atual += 1
                        if caso_atual >= len(casos):
                            rodando = False
                        else:
                            resetar_caso()
                elif estado == "resposta_incorreta":
                    if botao_tentar.collidepoint(mouse_x, mouse_y):
                        resetar_caso()
                elif estado == "glossario_letra":
                    if glossario_erro:
                        # clica em qualquer lugar para tentar novamente
                        abrir_glossario_libras()
                    else:
                        rects = obter_grade_letras_rects()
                        for letra, r in rects.items():
                            if r.collidepoint(mouse_x, mouse_y) and letra in verbetes_por_letra:
                                letra_selecionada = letra
                                indice_scroll_palavras = 0
                                verbete_selecionado = None
                                imagem_verbete_surface = None
                                mao_surface = None
                                video_disponivel = None
                                glossario_erro = None
                                estado = "glossario_palavra"
                                break
                elif estado == "glossario_palavra":
                    # rolagem via clique do mouse (4/5) ou wheel (eventos separados em pygame 2)
                    lista = verbetes_por_letra.get(letra_selecionada or "", [])
                    area_x = 60
                    area_y = 150
                    area_w = 420
                    area_h = altura - 220
                    itens_por_pagina = max(5, (area_h - 30) // 44)
                    visiveis = lista[indice_scroll_palavras : indice_scroll_palavras + itens_por_pagina]
                    for i, v in enumerate(visiveis):
                        y = area_y + 15 + i * 44
                        rect_item = pygame.Rect(area_x + 10, y, area_w - 20, 38)
                        if rect_item.collidepoint(mouse_x, mouse_y):
                            verbete_selecionado = v
                            carregar_detalhes_do_verbete(v)
                            break
                    # botão de vídeo
                    if verbete_selecionado and video_disponivel and botao_assistir_video.collidepoint(mouse_x, mouse_y):
                        try:
                            caminho = garantir_video_libras(video_disponivel)
                            p = pathlib.Path(caminho).resolve()
                            # Windows: abre com player padrão; fallback: abre no navegador
                            try:
                                os.startfile(str(p))  # type: ignore[attr-defined]
                            except Exception:
                                webbrowser.open(p.as_uri())
                        except (urllib.error.URLError, TimeoutError):
                            glossario_erro = "Não consegui baixar o vídeo do INES. Verifique sua internet."
                        except Exception:
                            glossario_erro = "Falha ao abrir o vídeo."
            elif evento.type == pygame.MOUSEWHEEL:
                if estado == "glossario_palavra":
                    # evento.y: +1 (para cima), -1 (para baixo)
                    lista = verbetes_por_letra.get(letra_selecionada or "", [])
                    area_h = altura - 220
                    itens_por_pagina = max(5, (area_h - 30) // 44)
                    max_scroll = max(0, len(lista) - itens_por_pagina)
                    indice_scroll_palavras = max(0, min(indice_scroll_palavras - evento.y, max_scroll))
finally:
    pygame.quit()
    limpar_cache_libras()
    sys.exit()
