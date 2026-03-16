import pygame
import sys

# iniciar o pygame
pygame.init()

# tamanho da janela
largura = 1920
altura = 1080

# criar janela
tela = pygame.display.set_mode((largura, altura))
fundo = pygame.image.load("seminarios3-noite-2026-01-grupo4/src/backgrounds/urso.png")
fundo = pygame.transform.scale(fundo, (1920 , 1080))
pygame.display.set_caption("Detetive das Virtudes - Tarso de Coimbra")

# fonte para escrever textos
fonte = pygame.font.SysFont("arial", 14)

# dados do caso 1
titulo = "Caso: O brinquedo perdido"

descricao = "Voce encontra um urso no parque, após sua mãe te chamar para ir para casa. Voce deve decidir o que fazer com ele."

opcoes = [
    "1-Levar o brinquedo para casa, ninguém está olhando",
    "2-Perguntar para as crianças no parque de quem é o brinquedo",
    "3-Esconder o brinquedo para que ninguém mais o encontre",
]

# índice da opção correta (0 = primeira opção)
resposta_correta = 1  # corresponde à opção 2

feedback = "virtude é como um tesouro que você carrega dentro do peito e que brilha toda vez que você faz o que é certo, mesmo quando ninguém está olhando. Não esconder o urso ou levar para casa te faz ser honesto em nao pegar ou esconder o que nao é seu. "  # mensagem que aparece depois da escolha


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

    # desenhar fundo
    tela.blit(fundo, (0, 0))


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