import pygame
import sys
import os

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
    global botao_jogar, botao_sair, botao_fullscreen, botao_tentar, seta_x, seta_y, seta_rect

    botao_jogar = pygame.Rect(largura // 2 - 150, altura // 2 - 120, 300, 70)
    botao_sair = pygame.Rect(largura // 2 - 150, altura // 2 - 30, 300, 70)
    botao_fullscreen = pygame.Rect(largura // 2 - 150, altura // 2 + 60, 300, 70)
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
botao_tentar = pygame.Rect(0, 0, 0, 0)

# Seta para avançar
seta_x = 0
seta_y = 0
seta_tamanho = 50
seta_rect = pygame.Rect(0, 0, 0, 0)

atualizar_imagens()
atualizar_layout()

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

    if estado == "menu":
        titulo_menu = fonte_titulo.render("Detetive das Virtudes", True, BRANCO)
        instrucao_menu = fonte_texto.render("Clique em Jogar para começar ou Sair para fechar o jogo.", True, BRANCO)
        pygame.draw.rect(tela, AZUL, botao_jogar)
        pygame.draw.rect(tela, VERMELHO, botao_sair)

        texto_jogar = fonte_opcoes.render("Jogar", True, BRANCO)
        texto_sair = fonte_opcoes.render("Sair", True, BRANCO)
        texto_fullscreen = fonte_opcoes.render("Tela Cheia", True, BRANCO)

        pygame.draw.rect(tela, AZUL, botao_jogar)
        pygame.draw.rect(tela, VERMELHO, botao_sair)
        pygame.draw.rect(tela, VERDE if fullscreen else AZUL, botao_fullscreen)

        tela.blit(titulo_menu, (largura // 2 - titulo_menu.get_width() // 2, 120))
        tela.blit(instrucao_menu, (largura // 2 - instrucao_menu.get_width() // 2, 190))
        tela.blit(texto_jogar, (botao_jogar.x + 120, botao_jogar.y + 20))
        tela.blit(texto_sair, (botao_sair.x + 125, botao_sair.y + 20))
        tela.blit(texto_fullscreen, (botao_fullscreen.x + 70, botao_fullscreen.y + 20))
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
            render_texto_quebrado(casos[caso_atual]["opcoes"][i], fonte_opcoes, BRANCO, tela, botao["rect"].x + 20, botao["rect"].y + 15, botao["rect"].width - 40, fonte_opcoes.get_height() + 6)
        
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
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if estado == "menu":
                if botao_jogar.collidepoint(mouse_x, mouse_y):
                    estado = "caso"
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

pygame.quit()
sys.exit()
