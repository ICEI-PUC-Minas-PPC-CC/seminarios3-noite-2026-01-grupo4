# 02 — Documento de Requisitos do Software

> **Grupo:** *(preencher)*  
> **Aplicação:** *(preencher)*  
> **Comunidade:** *(preencher)*

---

## 1. Visão Geral

(Descreva em poucas frases o que é a aplicação, para quem ela é destinada e qual problema ela resolve.)

## 2. Público-Alvo

| Campo | Informação |
| ------- | ----------- |
| Perfil dos usuários |Crianças do ensino fundamental, incluindo alunos com deficiência auditiva|
| Faixa etária |6 a 12 anos|
| Necessidades de acessibilidade |Interface visual, suporte a Libras, pouco uso de texto, feedback visual|
| Nível de familiaridade com tecnologia |Básico|

> **Lembrete (Tarso de Coimbra):** Os usuários podem ter deficiência auditiva/surdez. A interface deve ser **visual, intuitiva e de baixa complexidade**. Priorize elementos visuais (imagens, ícones, cores) sobre texto extenso.

## 3. Requisitos Funcionais

| ID | Requisito | Prioridade | Origem da demanda |
| ---- | ---------- | :----------: | ------------------ |
| RF01 | | *(Alta/Média/Baixa)* | *(Reunião com a comunidade em DD/MM)* |
| RF02 | Exibir casos com imagem, título e descrição curta|Alta | Lembrete (Tarso de Coimbra)|
| RF03 | | | |
| RF04 | | | |
| RF05 | | | |

## 4. Requisitos Não Funcionais

| ID | Requisito | Categoria |
| ---- | ---------- | ----------- |
| RNF01 | A aplicação deve ser acessível via instalador (.exe) para Windows | Acessibilidade |
| RNF02 | A interface deve ser simples e intuitiva | Usabilidade |
| RNF03 | A aplicação deve ter design visual atrativo e amigável| Usabilidade| |
| RNF04 |A aplicação deve funcionar sem necessidade de internet | Compatibilidade
| RNF05 | | |

## 5. Requisitos de Acessibilidade

- [X] Interface predominantemente visual (ícones, cores, imagens)
- [X] Textos curtos e objetivos
- [X] Botões grandes e identificáveis
- [X] Contraste adequado de cores
- [X] Compatível com Libras (se aplicável: vídeos, sinais, glossário)
- [X] Sem dependência de áudio para funcionalidades essenciais
- [ ] Outro: *(especificar)*

## 6. Tecnologias Escolhidas

| Componente | Tecnologia |
| ----------- | ----------- |
| Front-end |Pygame|
| Back-end (se houver) | |
| Banco de dados (se houver) | |
| Hospedagem | GitHub ou site da escola|
| Outras ferramentas | Pygame|

## 7. Protótipo / Wireframes

(Inclua esboços das telas principais ou links para protótipos — mesmo rascunhos simples em papel são válidos. Salvem imagens dos wireframes em `evidencias/prints/`.)
Tela inicial (botão “Jogar”)
Tela de caso (imagem + opções)
Tela de feedback (acerto/erro)
Tela final (mensagem de conclusão)
## 8. Escopo Mínimo Viável (MVP)

(Quais funcionalidades compõem a versão mínima que pode ser entregue à comunidade?)

- [X] *Exibir todas as virtudes citadas em casos com imagens*
- [X] *Sistema de escolha entre alternativas
- [X] *Feedback visual de acerto/erro*

## 9. Funcionalidades Desejáveis (se houver tempo)

- *(Funcionalidade extra 1)*
- *(Funcionalidade extra 2)*
