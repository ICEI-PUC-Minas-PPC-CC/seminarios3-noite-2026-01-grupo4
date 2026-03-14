import pygame
import sys

# iniciar o pygame
pygame.init()

# tamanho da janela
largura = 800
altura = 600

# criar janela
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Detetive das Virtudes")

# fonte para escrever textos
fonte = pygame.font.SysFont("arial", 30)

# dados do caso (por enquanto direto no código)
titulo = "Caso: O brinquedo perdido"

descricao = "Uma criança encontra um brinquedo no parque."

opcoes = [
    "Levar o brinquedo para casa",
    "Perguntar de quem é o brinquedo",
    "Esconder o brinquedo"
]

resposta_correta = 1  # posição da resposta correta

feedback = ""  # mensagem que aparece depois da escolha


# posições dos botões
botoes = []

for i in range(len(opcoes)):
    x = 200
    y = 300 + i * 70
    largura_botao = 400
    altura_botao = 50

    retangulo = pygame.Rect(x, y, largura_botao, altura_botao)

    botoes.append(retangulo)


# loop principal do jogo
rodando = True

while rodando:

    # cor de fundo
    tela.fill((240, 240, 240))

    # desenhar título
    texto_titulo = fonte.render(titulo, True, (0, 0, 0))
    tela.blit(texto_titulo, (200, 50))

    # desenhar descrição
    texto_desc = fonte.render(descricao, True, (0, 0, 0))
    tela.blit(texto_desc, (150, 150))

    # desenhar botões
    for i in range(len(botoes)):

        pygame.draw.rect(tela, (100, 150, 255), botoes[i])

        texto_opcao = fonte.render(opcoes[i], True, (255, 255, 255))

        tela.blit(texto_opcao, (botoes[i].x + 10, botoes[i].y + 10))

    # mostrar feedback
    if feedback != "":
        texto_feedback = fonte.render(feedback, True, (0, 120, 0))
        tela.blit(texto_feedback, (250, 500))

    # verificar eventos
    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:

            mouse = pygame.mouse.get_pos()

            for i in range(len(botoes)):

                if botoes[i].collidepoint(mouse):

                    if i == resposta_correta:
                        feedback = "Correto! Virtude: Honestidade"
                    else:
                        feedback = "Resposta incorreta"

    pygame.display.update()

pygame.quit()
sys.exit()