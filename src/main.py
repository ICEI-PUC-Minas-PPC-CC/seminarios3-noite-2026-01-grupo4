import pygame
import sys
import os

# Iniciar pygame
pygame.init()

# Configurações da tela
largura = 1920
altura = 1080
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Detetive das Virtudes")

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AZUL = (100, 150, 255)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)

# Fontes
fonte_titulo = pygame.font.SysFont("arial", 40, bold=True)
fonte_texto = pygame.font.SysFont("arial", 24)
fonte_opcoes = pygame.font.SysFont("arial", 18)

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
        "imagem_caso": "src/backgrounds/CasoGirassois.png",
        "imagem_virtude": "src/backgrounds/EG.png.png",
        "opcoes": [
            "1-Pegar o baú inteiro para si mesmo",
            "2-Pegar apenas o que você acha que merece",
            "3-Deixar o baú onde está, respeitando a placa",
        ],
        "resposta_correta": 2,
        "virtude": "Coragem",
        "explicacao": "A coragem é enfrentar desafios e fazer o que é certo,esmo quando é difícil. Pegar apenas o que merece mostra que você tem a coragem de ser justo e honesto, mesmo quando ninguém está olhando.",
        "licao_errada": "Pegar tudo para si é ganância e falta deoragem para ser justo. Deixar o baú inteiro pode ser visto como covardia, pois você não tem a coragem de reivindicar o que é seu." 

    }
    
]

# Estado do jogo
caso_atual = 0
estado = "menu"
feedback = ""
botao_errado_index = -1

# Criar botões iniciais
botoes = []
for i in range(len(casos[caso_atual]["opcoes"])):
    x = 50
    y = 150 + i * 80
    largura_botao = 500
    altura_botao = 60
    retangulo = pygame.Rect(x, y, largura_botao, altura_botao)
    botoes.append({"rect": retangulo})

# Botões do menu principal
botao_jogar = pygame.Rect(largura // 2 - 150, altura // 2 - 80, 300, 70)
botao_sair = pygame.Rect(largura // 2 - 150, altura // 2 + 20, 300, 70)

# Seta para avançar
seta_x = 1800
seta_y = 900
seta_tamanho = 50
seta_rect = pygame.Rect(seta_x - seta_tamanho, seta_y - seta_tamanho, seta_tamanho * 2, seta_tamanho * 2)

# Botão "Tentar Novamente"
botao_tentar = pygame.Rect(largura // 2 - 150, altura // 2 + 150, 300, 60)

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
        x = 50
        y = 150 + i * 80
        largura_botao = 500
        altura_botao = 60
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

        tela.blit(titulo_menu, (largura // 2 - titulo_menu.get_width() // 2, 120))
        tela.blit(instrucao_menu, (largura // 2 - instrucao_menu.get_width() // 2, 190))
        tela.blit(texto_jogar, (botao_jogar.x + 120, botao_jogar.y + 20))
        tela.blit(texto_sair, (botao_sair.x + 125, botao_sair.y + 20))
    elif estado == "caso":
        texto_titulo = fonte_titulo.render(casos[caso_atual]["titulo"], True, BRANCO)
        tela.blit(texto_titulo, (20, 20))
        
        texto_desc = fonte_texto.render(casos[caso_atual]["descricao"], True, BRANCO)
        tela.blit(texto_desc, (20, 80))
        
        for i, botao in enumerate(botoes):
            cor = VERMELHO if botao_errado_index == i else AZUL
            pygame.draw.rect(tela, cor, botao["rect"])
            texto_opcao = fonte_opcoes.render(casos[caso_atual]["opcoes"][i], True, BRANCO)
            tela.blit(texto_opcao, (botao["rect"].x + 10, botao["rect"].y + 15))
        
        if feedback and "Correto" in feedback:
            texto_feedback = fonte_texto.render(feedback, True, VERDE)
            tela.blit(texto_feedback, (20, 480))
            desenhar_seta()
    
    elif estado == "virtude":
        titulo_virtude = f"Virtude: {casos[caso_atual]['virtude']}"
        texto_titulo = fonte_titulo.render(titulo_virtude, True, BRANCO)
        tela.blit(texto_titulo, (largura // 2 - 300, 80))
        
        linhas = casos[caso_atual]["explicacao"].split('\n')
        y = 300
        for linha in linhas:
            if linha.strip():  # Ignora linhas vazias
                texto = fonte_texto.render(linha, True, BRANCO)
                tela.blit(texto, (100, y))
                y += fonte_texto.get_height() + 20
        
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
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            if estado == "menu":
                if botao_jogar.collidepoint(mouse_x, mouse_y):
                    estado = "caso"
                elif botao_sair.collidepoint(mouse_x, mouse_y):
                    rodando = False
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
