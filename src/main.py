import pygame
import sys

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

# Fontes (maiores)
fonte_titulo = pygame.font.SysFont("arial", 40, bold=True)
fonte_texto = pygame.font.SysFont("arial", 24)
fonte_opcoes = pygame.font.SysFont("arial", 18)

# Carregar imagens
fundo_caso = pygame.image.load("src/backgrounds/lamen.jpg")
fundo_caso = pygame.transform.scale(fundo_caso, (largura, altura))

fundo_virtude = pygame.image.load("src/backgrounds/virtude.jpg")
fundo_virtude = pygame.transform.scale(fundo_virtude, (largura, altura))

# Dados dos casos
casos = [
    {
        "titulo": "Caso 1: O brinquedo perdido",
        "descricao": "Você encontra um urso de pelúcia no parque. Ninguém está vendo. O que você faz?",
        "opcoes": [
            "1-Levar o brinquedo para casa, ninguém está olhando",
            "2-Procurar o dono ou avisar alguém",
            "3-Esconder o brinquedo para que ninguém o encontre",
        ],
        "resposta_correta": 1,
        "virtude": "Honestidade",
        "explicacao": "A honestidade é fazer o certo mesmo quando ninguém está olhando. Procurar o dono mostra que você valoriza a verdade. Cada ato honesto constrói um caráter forte!",
        "licao_errada": "Levar algo que não é seu ou esconder é roubo. Isso machuca quem perdeu o objeto e prejudica sua própria alma."
    },
    {
        "titulo": "Caso 2: A moeda encontrada",
        "descricao": "Você encontra uma moeda de ouro no chão da escola. Ninguém viu você pegá-la. O que você faz?",
        "opcoes": [
            "1-Guardar a moeda para si mesmo, é uma sorte",
            "2-Procurar o dono ou entregar à diretoria",
            "3-Dar a moeda para um colega que precisa",
        ],
        "resposta_correta": 1,
        "virtude": "Honestidade",
        "explicacao": "Devolver o que não é seu mostra honestidade. A pessoa que perdeu provavelmente está triste procurando. Sua honestidade a fará feliz!",
        "licao_errada": "Guardar algo que achou não é honesto. Seria roubo, mesmo se achou no chão."
    }
]

# Estado do jogo
caso_atual = 0
estado = "caso"  # "caso", "virtude", "resposta_incorreta"
feedback = ""
botao_errado_index = -1

# Criar botões das opcoes
botoes = []
for i in range(len(casos[caso_atual]["opcoes"])):
    x = 50
    y = 150 + i * 80
    largura_botao = 500
    altura_botao = 60
    retangulo = pygame.Rect(x, y, largura_botao, altura_botao)
    botoes.append({"rect": retangulo})

# Seta para avançar
seta_x = 1800
seta_y = 900
seta_tamanho = 50
seta_rect = pygame.Rect(seta_x - seta_tamanho, seta_y - seta_tamanho, seta_tamanho * 2, seta_tamanho * 2)

# Botão "Tentar Novamente"
botao_tentar = pygame.Rect(largura // 2 - 150, altura // 2 + 150, 300, 60)

# Função para desenhar seta
def desenhar_seta():
    pontos = [
        (seta_x + seta_tamanho, seta_y),
        (seta_x - seta_tamanho, seta_y - seta_tamanho),
        (seta_x - seta_tamanho, seta_y + seta_tamanho),
    ]
    pygame.draw.polygon(tela, VERDE, pontos)
    pygame.draw.polygon(tela, BRANCO, pontos, 3)

# Função para resetar o caso
def resetar_caso():
    global estado, feedback, botao_errado_index
    
    # Recriar botões
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
while rodando:
    # Escolher fundo
    if estado == "caso" or estado == "resposta_incorreta":
        fundo_atual = fundo_caso
    else:
        fundo_atual = fundo_virtude
    
    # Desenhar fundo
    tela.blit(fundo_atual, (0, 0))
    
    if estado == "caso":
        # Desenhar título (sem fundo)
        texto_titulo = fonte_titulo.render(casos[caso_atual]["titulo"], True, BRANCO)
        tela.blit(texto_titulo, (20, 20))
        
        # Desenhar descrição (sem fundo)
        texto_desc = fonte_texto.render(casos[caso_atual]["descricao"], True, BRANCO)
        tela.blit(texto_desc, (20, 80))
        
        # Desenhar botões
        for i, botao in enumerate(botoes):
            # Cor normal ou vermelha se foi clicado como errado
            cor = AZUL
            if botao_errado_index == i:
                cor = VERMELHO
            
            pygame.draw.rect(tela, cor, botao["rect"])
            texto_opcao = fonte_opcoes.render(casos[caso_atual]["opcoes"][i], True, BRANCO)
            tela.blit(texto_opcao, (botao["rect"].x + 10, botao["rect"].y + 15))
        
        # Desenhar feedback correto
        if feedback and "Correto" in feedback:
            texto_feedback = fonte_texto.render(feedback, True, VERDE)
            tela.blit(texto_feedback, (20, 480))
            desenhar_seta()
    
    elif estado == "virtude":
        # Desenhar título da virtude (sem fundo)
        titulo_virtude = f"Virtude: {casos[caso_atual]['virtude']}"
        texto_titulo = fonte_titulo.render(titulo_virtude, True, BRANCO)
        tela.blit(texto_titulo, (largura // 2 - 300, 80))
        
        # Desenhar explicação (sem fundo)
        linhas = casos[caso_atual]["explicacao"].split('\n')
        y = 300
        for linha in linhas:
            texto = fonte_texto.render(linha, True, BRANCO)
            tela.blit(texto, (100, y))
            y += fonte_texto.get_height() + 20
        
        # Seta para próximo caso
        desenhar_seta()
    
    elif estado == "resposta_incorreta":
        # Overlay escuro
        overlay = pygame.Surface((largura, altura))
        overlay.set_alpha(200)
        overlay.fill(PRETO)
        tela.blit(overlay, (0, 0))
        
        # Caixa de diálogo
        caixa_x = largura // 2 - 300
        caixa_y = altura // 2 - 200
        caixa_largura = 600
        caixa_altura = 400
        
        pygame.draw.rect(tela, PRETO, (caixa_x, caixa_y, caixa_largura, caixa_altura))
        pygame.draw.rect(tela, VERMELHO, (caixa_x, caixa_y, caixa_largura, caixa_altura), 5)
        
        # Título
        titulo_erro = fonte_titulo.render("Resposta Incorreta!", True, VERMELHO)
        tela.blit(titulo_erro, (caixa_x + 100, caixa_y + 30))
        
        # Mensagem de erro
        licao = casos[caso_atual]["licao_errada"]
        palavras = licao.split()
        y = caixa_y + 120
        
        # Quebrar texto em linhas
        linha_atual = ""
        for palavra in palavras:
            if len(linha_atual) + len(palavra) > 40:
                texto_linha = fonte_texto.render(linha_atual, True, BRANCO)
                tela.blit(texto_linha, (caixa_x + 30, y))
                y += fonte_texto.get_height() + 10
                linha_atual = palavra
            else:
                linha_atual += palavra + " "
        
        if linha_atual:
            texto_linha = fonte_texto.render(linha_atual, True, BRANCO)
            tela.blit(texto_linha, (caixa_x + 30, y))
        
        # Botão "Tentar Novamente"
        pygame.draw.rect(tela, (0, 150, 0), botao_tentar)
        texto_botao = fonte_opcoes.render("Tentar Novamente", True, BRANCO)
        tela.blit(texto_botao, (botao_tentar.x + 30, botao_tentar.y + 15))
    
    # Atualizar tela
    pygame.display.update()
    
    # Processar eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            if estado == "caso":
                # Verificar clique nos botões
                for i, botao in enumerate(botoes):
                    if botao["rect"].collidepoint(mouse_x, mouse_y):
                        # Respondeu corretamente
                        if i == casos[caso_atual]["resposta_correta"]:
                            feedback = f"Correto! Virtude: {casos[caso_atual]['virtude']}"
                        else:
                            # Respondeu incorretamente
                            botao_errado_index = i
                            estado = "resposta_incorreta"
                            feedback = ""
                        break
                
                # Verificar clique na seta
                if feedback and "Correto" in feedback and seta_rect.collidepoint(mouse_x, mouse_y):
                    estado = "virtude"
            
            elif estado == "virtude":
                # Verificar clique na seta
                if seta_rect.collidepoint(mouse_x, mouse_y):
                    # Avançar para próximo caso
                    caso_atual += 1
                    if caso_atual >= len(casos):
                        rodando = False
                    else:
                        resetar_caso()
            
            elif estado == "resposta_incorreta":
                # Verificar clique no botão "Tentar Novamente"
                if botao_tentar.collidepoint(mouse_x, mouse_y):
                    resetar_caso()


if __name__ == "__main__":
    main()

