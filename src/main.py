# Refatoração completa do jogoo
import pygame
import sys
import random

class Config:
    LARGURA_INICIAL = 1280
    ALTURA_INICIAL = 720
    CORES = {
        'PRETO': (0, 0, 0),
        'BRANCO': (255, 255, 255),
        'AZUL': (100, 150, 255),
        'VERDE': (0, 255, 0),
        'VERMELHO': (255, 0, 0),
        'CONFETES': [(0,255,0), (255,255,0), (255,0,255), (0,255,255), (255,128,0)]
    }
    FONTES = {
        'TITULO': ('arial', 40, True),
        'TEXTO': ('arial', 24, False),
        'OPCOES': ('arial', 18, False)
    }
    BACKGROUNDS = {
        'caso': 'src/backgrounds/lamen.jpg',
        'virtude': 'src/backgrounds/virtude.jpg',
        'responsabilidade': 'src/backgrounds/responsabilidade.jpg',
        'generosidade': 'src/backgrounds/generosidade.jpg'
    }

class Caso:
    def __init__(self, titulo, descricao, opcoes, resposta_correta, virtude, explicacao, licoes_erradas):
        self.titulo = titulo
        self.descricao = descricao
        self.opcoes = opcoes
        self.resposta_correta = resposta_correta
        self.virtude = virtude
        self.explicacao = explicacao
        self.licoes_erradas = licoes_erradas

class DetetiveDasVirtudes:
    def __init__(self):
        pygame.init()
        self.largura = Config.LARGURA_INICIAL
        self.altura = Config.ALTURA_INICIAL
        self.tela = pygame.display.set_mode((self.largura, self.altura), pygame.RESIZABLE)
        pygame.display.set_caption("Detetive das Virtudes")
        self.cores = Config.CORES
        self.fontes = {
            k: pygame.font.SysFont(*Config.FONTES[k]) for k in Config.FONTES
        }
        self.backgrounds = {k: pygame.image.load(v) for k, v in Config.BACKGROUNDS.items()}
        self.casos = self.carregar_casos()
        self.estado = 'caso'
        self.caso_atual = 0
        self.feedback = ''
        self.botao_errado_index = -1
        self.botao_correto_index = -1
        self.mostrar_icone_correto = False
        self.piscar_erro = False
        self.piscar_timer = 0
        self.piscar_index = -1
        self.confetes = []
        self.botoes = self.criar_botoes()
        self.clock = pygame.time.Clock()

    def carregar_casos(self):
        return [
            Caso(
                "Caso 1: O brinquedo perdido",
                "Você encontra um urso de pelúcia no parque. Ninguém está vendo. O que você faz?",
                [
                    "Levar o brinquedo para casa, ninguém está olhando",
                    "Procurar o dono ou avisar alguém",
                    "Esconder o brinquedo para que ninguém o encontre"
                ],
                1,
                "Honestidade",
                "A honestidade é fazer o certo mesmo quando ninguém está olhando. Procurar o dono mostra que você valoriza a verdade. Cada ato honesto constrói um caráter forte!",
                [
                    "Levar algo que não é seu é roubo. Isso machuca quem perdeu o objeto e prejudica sua própria alma.",
                    "",
                    "Esconder o brinquedo é desonesto e impede que o dono encontre o que perdeu."
                ]
            ),
            Caso(
                "Caso 2: A moeda encontrada",
                "Você encontra uma moeda de ouro no chão da escola. Ninguém viu você pegá-la. O que você faz?",
                [
                    "Guardar a moeda para si mesmo, é uma sorte",
                    "Procurar o dono ou entregar à diretoria",
                    "Dar a moeda para um colega que precisa"
                ],
                1,
                "Honestidade",
                "Devolver o que não é seu mostra honestidade. A pessoa que perdeu provavelmente está triste procurando. Sua honestidade a fará feliz!",
                [
                    "Guardar algo que achou não é honesto. Seria roubo, mesmo se achou no chão.",
                    "",
                    "Dar a moeda para outro colega não resolve o erro. O certo é procurar o dono."
                ]
            ),
            Caso(
                "Caso 3: Material escolar organizado",
                "Você percebe que seu material escolar está bagunçado e misturado com o de um colega. O que você faz?",
                [
                    "Deixa tudo como está, não é problema seu",
                    "Organiza seu material e devolve o que é do colega",
                    "Guarda o material do colega junto com o seu para não perder"
                ],
                1,
                "Responsabilidade",
                "Ser responsável é cuidar do que é seu e respeitar o que é dos outros. Organizar e devolver o material mostra maturidade e respeito.",
                [
                    "Não se importar pode causar confusão e prejudicar o colega. Responsabilidade é agir certo mesmo em pequenas coisas.",
                    "",
                    "Guardar o material do colega junto com o seu pode causar mais confusão."
                ]
            ),
            Caso(
                "Caso 4: Ajudando um colega",
                "Um colega esqueceu o lanche e está triste. O que você faz?",
                [
                    "Oferece parte do seu lanche para ele se sentir melhor",
                    "Finge que não viu e come sozinho",
                    "Ri da situação para animar o colega"
                ],
                0,
                "Generosidade",
                "A generosidade é compartilhar o que temos, mesmo que seja pouco. Um gesto generoso pode alegrar o dia de alguém!",
                [
                    "",
                    "Ignorar o colega não ajuda. Generosidade é dividir e se importar com o outro.",
                    "Rir da situação pode magoar ainda mais. O melhor é ajudar."
                ]
            )
        ]

    def run(self):
        while True:
            self.clock.tick(60)
            self.handle_events()
            self.render()
            pygame.display.update()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                self.largura, self.altura = event.w, event.h
                self.tela = pygame.display.set_mode((self.largura, self.altura), pygame.RESIZABLE)
                self.botoes = self.criar_botoes()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse(event.pos)

    def handle_mouse(self, pos):
        mouse_x, mouse_y = pos
        if self.estado == 'caso':
            for i, botao in enumerate(self.botoes):
                if botao.collidepoint(mouse_x, mouse_y):
                    if i == self.casos[self.caso_atual].resposta_correta:
                        self.feedback = f"Correto! Virtude: {self.casos[self.caso_atual].virtude}"
                        self.botao_correto_index = i
                        self.mostrar_icone_correto = True
                        self.confetes = self.gerar_confetes()
                    else:
                        self.piscar_erro = True
                        self.piscar_timer = pygame.time.get_ticks()
                        self.piscar_index = i
                        self.botao_errado_index = i
                        self.feedback = ''
                    break
            _, _, _, seta_rect = self.get_seta_rect()
            if self.feedback and "Correto" in self.feedback and seta_rect.collidepoint(mouse_x, mouse_y):
                self.estado = 'virtude'
                self.botao_correto_index = -1
                self.mostrar_icone_correto = False
                self.confetes = []
        elif self.estado == 'virtude':
            _, _, _, seta_rect = self.get_seta_rect()
            if seta_rect.collidepoint(mouse_x, mouse_y):
                self.caso_atual += 1
                if self.caso_atual >= len(self.casos):
                    pygame.quit()
                    sys.exit()
                else:
                    self.resetar_caso()
        elif self.estado == 'resposta_incorreta':
            botao_tentar = self.get_botao_tentar()
            if botao_tentar.collidepoint(mouse_x, mouse_y):
                self.resetar_caso()

    def criar_botoes(self):
        botoes = []
        margem_x = int(self.largura * 0.04)
        margem_y = int(self.altura * 0.14)
        largura_botao = int(self.largura * 0.38)
        altura_botao = int(self.altura * 0.07)
        espacamento = int(self.altura * 0.09)
        for i in range(len(self.casos[self.caso_atual].opcoes)):
            x = margem_x
            y = margem_y + i * espacamento
            botoes.append(pygame.Rect(x, y, largura_botao, altura_botao))
        return botoes

    def get_seta_rect(self):
        seta_tamanho = int(min(self.largura, self.altura) * 0.045)
        seta_x = self.largura - seta_tamanho * 2
        seta_y = self.altura - seta_tamanho * 2
        return seta_x, seta_y, seta_tamanho, pygame.Rect(seta_x - seta_tamanho, seta_y - seta_tamanho, seta_tamanho * 2, seta_tamanho * 2)

    def get_botao_tentar(self):
        largura_botao = int(self.largura * 0.23)
        altura_botao = int(self.altura * 0.08)
        x = self.largura // 2 - largura_botao // 2
        y = self.altura // 2 + int(self.altura * 0.18)
        return pygame.Rect(x, y, largura_botao, altura_botao)

    def desenhar_seta(self):
        seta_x, seta_y, seta_tamanho, _ = self.get_seta_rect()
        pontos = [
            (seta_x + seta_tamanho, seta_y),
            (seta_x - seta_tamanho, seta_y - seta_tamanho),
            (seta_x - seta_tamanho, seta_y + seta_tamanho),
        ]
        pygame.draw.polygon(self.tela, self.cores['VERDE'], pontos)
        pygame.draw.polygon(self.tela, self.cores['BRANCO'], pontos, 3)

    def resetar_caso(self):
        self.estado = 'caso'
        self.feedback = ''
        self.botao_errado_index = -1
        self.botao_correto_index = -1
        self.mostrar_icone_correto = False
        self.piscar_erro = False
        self.piscar_index = -1
        self.confetes = []
        self.botoes = self.criar_botoes()

    def gerar_confetes(self):
        caixa_largura = int(self.largura*0.45)
        caixa_altura = int(self.altura*0.25)
        caixa_x = self.largura // 2 - caixa_largura // 2
        caixa_y = int(self.altura*0.18)
        return [
            {
                'x': random.randint(caixa_x, caixa_x+caixa_largura),
                'y': caixa_y + random.randint(0, 10),
                'cor': random.choice(self.cores['CONFETES']),
                'vel': random.uniform(2, 6),
                'raio': random.randint(6, 12)
            }
            for _ in range(30)
        ]

    def render(self):
        self.tela.blit(self.get_fundo_atual(), (0, 0))
        if self.estado == 'caso':
            self.render_caso()
        elif self.estado == 'virtude':
            self.render_virtude()
        elif self.estado == 'resposta_incorreta':
            self.render_erro()

    def get_fundo_atual(self):
        if self.estado in ("caso", "resposta_incorreta"):
            if self.caso_atual == 2:
                img = self.backgrounds['responsabilidade']
            elif self.caso_atual == 3:
                img = self.backgrounds['generosidade']
            else:
                img = self.backgrounds['caso']
        else:
            img = self.backgrounds['virtude']
        iw, ih = img.get_width(), img.get_height()
        tw, th = self.largura, self.altura
        scale = min(tw/iw, th/ih)
        new_w, new_h = int(iw*scale), int(ih*scale)
        surf = pygame.transform.smoothscale(img, (new_w, new_h))
        fundo = pygame.Surface((tw, th))
        fundo.fill(self.cores['PRETO'])
        fundo.blit(surf, ((tw-new_w)//2, (th-new_h)//2))
        # Salva área útil da imagem para uso nos elementos
        self.area_util_img = pygame.Rect((tw-new_w)//2, (th-new_h)//2, new_w, new_h)
        return fundo

    def render_caso(self):
        caso = self.casos[self.caso_atual]
        area = self.area_util_img
        self.render_texto_multilinha(caso.titulo, self.fontes['TITULO'], self.cores['BRANCO'], area.x + int(area.width * 0.02), area.y + int(area.height * 0.03), int(area.width*0.96))
        self.render_texto_multilinha(caso.descricao, self.fontes['TEXTO'], self.cores['BRANCO'], area.x + int(area.width * 0.02), area.y + int(area.height * 0.08), int(area.width*0.96))
        for i, botao in enumerate(self.botoes):
            cor = self.cores['AZUL']
            if self.botao_correto_index == i:
                cor = self.cores['VERDE']
            elif self.botao_errado_index == i:
                if self.piscar_erro and self.piscar_index == i:
                    cor = self.cores['VERMELHO'] if (pygame.time.get_ticks()//100)%2 == 0 else self.cores['AZUL']
                else:
                    cor = self.cores['VERMELHO']
            # Reposiciona botões para área útil
            botao_x = area.x + int(area.width * 0.04)
            botao_y = area.y + int(area.height * 0.14) + i * int(area.height * 0.09)
            botao_w = int(area.width * 0.38)
            botao_h = int(area.height * 0.07)
            botao_rect = pygame.Rect(botao_x, botao_y, botao_w, botao_h)
            pygame.draw.rect(self.tela, cor, botao_rect, border_radius=10)
            self.render_texto_multilinha(caso.opcoes[i], self.fontes['OPCOES'], self.cores['BRANCO'], botao_rect.x + int(botao_rect.width*0.03), botao_rect.y + int(botao_rect.height*0.25), botao_rect.width - int(botao_rect.width*0.1))
            if self.mostrar_icone_correto and self.botao_correto_index == i:
                self.desenhar_icone_visto(botao_rect.right - int(botao_rect.height*1.1), botao_rect.y + int(botao_rect.height*0.1), int(botao_rect.height*0.8))
        if self.feedback and "Correto" in self.feedback:
            self.render_feedback_correto()
        if self.piscar_erro and pygame.time.get_ticks() - self.piscar_timer > 500:
            self.piscar_erro = False
            self.botao_errado_index = self.piscar_index
            self.estado = 'resposta_incorreta'

    def render_virtude(self):
        caso = self.casos[self.caso_atual]
        area = self.area_util_img
        self.render_texto_multilinha(f"Virtude: {caso.virtude}", self.fontes['TITULO'], self.cores['BRANCO'], area.x + int(area.width * 0.02), area.y + int(area.height * 0.03), int(area.width*0.96))
        self.render_texto_multilinha(caso.explicacao, self.fontes['TEXTO'], self.cores['BRANCO'], area.x + int(area.width * 0.02), area.y + int(area.height * 0.08), int(area.width*0.96))
        self.desenhar_seta()

    def render_erro(self):
        overlay = pygame.Surface((self.largura, self.altura))
        overlay.set_alpha(200)
        overlay.fill(self.cores['PRETO'])
        self.tela.blit(overlay, (0, 0))
        caixa_largura = int(self.largura*0.45)
        caixa_altura = int(self.altura*0.38)
        caixa_x = self.largura // 2 - caixa_largura // 2
        caixa_y = self.altura // 2 - caixa_altura // 2
        pygame.draw.rect(self.tela, self.cores['PRETO'], (caixa_x, caixa_y, caixa_largura, caixa_altura), border_radius=12)
        pygame.draw.rect(self.tela, self.cores['VERMELHO'], (caixa_x, caixa_y, caixa_largura, caixa_altura), 5, border_radius=12)
        # Título centralizado
        self.render_texto_multilinha(
            "Resposta Incorreta!", self.fontes['TITULO'], self.cores['VERMELHO'],
            caixa_x, caixa_y + int(caixa_altura*0.07), caixa_largura, altura_caixa=int(caixa_altura*0.18), centralizar_h=True, centralizar_v=True
        )
        caso = self.casos[self.caso_atual]
        licao = caso.licoes_erradas[self.botao_errado_index] if self.botao_errado_index >= 0 and self.botao_errado_index < len(caso.licoes_erradas) else "Escolha uma opção válida."
        # Lição centralizada
        self.render_texto_multilinha(
            licao, self.fontes['TEXTO'], self.cores['BRANCO'],
            caixa_x + int(caixa_largura*0.05), caixa_y + int(caixa_altura*0.3),
            int(caixa_largura*0.9), altura_caixa=int(caixa_altura*0.5), centralizar_h=True, centralizar_v=True
        )
        botao_tentar = self.get_botao_tentar()
        pygame.draw.rect(self.tela, (0, 150, 0), botao_tentar, border_radius=10)
        self.render_texto_multilinha(
            "Tentar Novamente", self.fontes['OPCOES'], self.cores['BRANCO'],
            botao_tentar.x, botao_tentar.y + int(botao_tentar.height*0.25),
            botao_tentar.width, altura_caixa=int(botao_tentar.height*0.5), centralizar_h=True, centralizar_v=True
        )

    def render_feedback_correto(self):
        caixa_largura = int(self.largura*0.45)
        caixa_altura = int(self.altura*0.25)
        caixa_x = self.largura // 2 - caixa_largura // 2
        caixa_y = int(self.altura*0.18)
        pygame.draw.rect(self.tela, self.cores['PRETO'], (caixa_x, caixa_y, caixa_largura, caixa_altura), border_radius=12)
        pygame.draw.rect(self.tela, self.cores['VERDE'], (caixa_x, caixa_y, caixa_largura, caixa_altura), 5, border_radius=12)
        # Título centralizado
        self.render_texto_multilinha(
            "Parabéns! Você acertou!",
            self.fontes['TITULO'], self.cores['VERDE'],
            caixa_x, caixa_y + int(caixa_altura*0.08),
            caixa_largura, altura_caixa=int(caixa_altura*0.22), centralizar_h=True, centralizar_v=True
        )
        caso = self.casos[self.caso_atual]
        # Explicação centralizada
        self.render_texto_multilinha(
            caso.explicacao, self.fontes['TEXTO'], self.cores['BRANCO'],
            caixa_x + int(caixa_largura*0.05), caixa_y + int(caixa_altura*0.45),
            int(caixa_largura*0.9), altura_caixa=int(caixa_altura*0.5), centralizar_h=True, centralizar_v=True
        )
        for c in self.confetes:
            pygame.draw.circle(self.tela, c['cor'], (int(c['x']), int(c['y'])), c['raio'])
            c['y'] += c['vel']
            if c['y'] > caixa_y + caixa_altura:
                c['y'] = caixa_y + random.randint(0, 10)
                c['x'] = random.randint(caixa_x, caixa_x+caixa_largura)
        self.desenhar_seta()

    def render_texto_multilinha(self, texto, fonte, cor, x, y, largura_max, altura_caixa=None, centralizar_h=False, centralizar_v=False, espacamento=6):
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ''
        for palavra in palavras:
            nova = palavra if linha_atual == '' else linha_atual + ' ' + palavra
            if fonte.size(nova)[0] > largura_max:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
            else:
                linha_atual = nova
        if linha_atual:
            linhas.append(linha_atual)
        altura_total = sum(fonte.size(linha)[1] for linha in linhas) + espacamento * (len(linhas)-1)
        if altura_caixa and centralizar_v:
            y = y + (altura_caixa - altura_total)//2
        for linha in linhas:
            rendered = fonte.render(linha, True, cor)
            x_linha = x
            if centralizar_h:
                x_linha = x + (largura_max - rendered.get_width())//2
            self.tela.blit(rendered, (x_linha, y))
            y += rendered.get_height() + espacamento

    def desenhar_icone_visto(self, x, y, tamanho):
        espessura = max(3, tamanho // 10)
        pygame.draw.lines(self.tela, self.cores['VERDE'], False, [
            (x, y + tamanho//2),
            (x + tamanho//3, y + tamanho),
            (x + tamanho, y)
        ], espessura)

if __name__ == "__main__":
    DetetiveDasVirtudes().run()

