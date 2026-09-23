# Gabriel Lima Marcelino

**Revenue Operations & Engenharia de Dados** · Florianópolis, Brasil · Aberto a posições remotas e internacionais

[Currículo](resume/curriculo.pt-BR.md) · [Case studies](case-studies/) · [Código](projects/) · [LinkedIn](https://www.linkedin.com/in/gabriellimamarcelino) · limamarcelinog@gmail.com

*[English version](README.md) — a documentação principal deste portfólio está em inglês.*

---

Eu construo a infraestrutura de dados em que os times de receita realmente operam — do evento bruto que uma plataforma emite até o número com o qual um diretor decide.

A maior parte de quem trabalha com Revenue Operations para no relatório. Eu cuido da cadeia inteira: ingestão, modelagem no PostgreSQL, camada semântica, os dashboards que consomem isso, e o processo comercial do outro lado. Também já gerenciei os squads que vivem desses números, e é por isso que eu construo para a pergunta que está sendo feita, não para a métrica que é fácil de calcular.

---

## O que eu faço

**Plataformas de dados de receita.** Modelagem em camadas (bruto → tratado → confiável) em PostgreSQL/Supabase, views materializadas e RPCs desenhadas para o padrão de leitura, estratégia de cache, e uma camada semântica para que cada métrica tenha exatamente uma definição em todos os times.

**Operação comercial.** Modelagem de funil do primeiro contato até o sucesso do cliente, atribuição multicanal, definição de indicadores comerciais, lógica de comissionamento, metas e forecast, e as réguas de reengajamento que devolvem ao pipeline o lead que o funil deixou cair.

**Entrega.** Dashboards em React/TypeScript para diretoria, vendas, pré-vendas, marketing e CS — porque plataforma de dados que ninguém lê não está pronta.

**Disciplina de engenharia sobre dados de produção.** Somente leitura por padrão, análise de impacto explícita, migration com rollback e plano de validação antes de qualquer coisa ser aplicada. O método está escrito: [prática de engenharia de banco](case-studies/database-engineering-practice.md).

---

## Trabalho em destaque

### Revenue data platform — o sistema pelo qual meu trabalho é avaliado

**[Ler o case study →](case-studies/revenue-data-platform.md)**

A infraestrutura de dados comerciais de uma empresa de tech education. Cada lead seguido desde o anúncio que o produziu, passando por qualificação, agendamento e call de vendas, até o aluno matriculado e sua jornada de sucesso — em um modelo só, com uma definição por métrica, em vez de cinco times exportando cinco versões da mesma pergunta.

Modelagem em camadas (bruto → tratado → confiável) em PostgreSQL/Supabase · resolução de identidade entre cinco sistemas de origem · camada semântica em SQL · contratos de RPC com autorização aplicada no banco · cache por fato-dia · dashboards em React e TypeScript para diretoria, vendas, pré-vendas, marketing e CS.

A parte operacional também é minha: definição dos indicadores comerciais, lógica de comissionamento, dois squads comerciais e as réguas de reengajamento que devolvem ao pipeline as etapas paradas do funil.

*Construído dentro de uma empresa — o código é proprietário. O case study cobre a arquitetura, os trade-offs por trás dela e a minha contribuição.*

### Também

| Case study | O que é |
|---|---|
| [Multi-channel marketing attribution](case-studies/marketing-attribution.md) | Ligar investimento de Meta, Google e LinkedIn Ads ao funil de conversão, até o nível de criativo — uma regra de atribuição escrita, em vez de cinco plataformas reivindicando a mesma conversão |
| [Customer health & churn prevention](case-studies/customer-health-and-churn.md) | Modelo de healthscore com score de registro corrigível por humano, e a aplicação interna que tornou o CS proativo |
| [Database engineering practice](case-studies/database-engineering-practice.md) | Como eu mudo um banco de produção sem quebrá-lo — o protocolo pelo qual trabalho, e o que ele pegou |

---

## Código

Projetos que eu desenhei e escrevi, onde o repositório é meu para compartilhar.

| Projeto | Stack | O que é |
|---|---|---|
| [**Funil comercial — modelagem e diagnóstico**](projects/funnel-analytics/) | PostgreSQL · SQL · Python | Modelo em camadas (bronze → prata → ouro) sobre dados públicos do funil de uma empresa real, e um diagnóstico escrito de onde o funil vaza: 23% dos leads convertendo abaixo da linha de base, 14,5% sem atribuição e convertendo o dobro do resto, e uma série temporal que não pode ser lida como tendência porque o time comercial não existia nos seis primeiros meses |
| [**Auditoria de calls de vendas com LLM**](projects/call-audit-llm/) | Python · Claude API · Pydantic | Avaliação de calls por rubrica onde a engenharia está nas travas, não na chamada do modelo: âncoras comportamentais para o modelo classificar em vez de julgar, toda nota obrigada a citar trecho verificado contra a transcrição, o ruído do próprio avaliador medido e publicado, e uma agregação que se recusa a ranquear vendedor com pouca amostra ou com diferença dentro da margem de erro |
| [Lucreiai](projects/lucreiai.md) | React Native · Expo · Supabase · TypeScript | App de unit economics para briqueiros: lucro real por peça depois de taxa, frete e reforma — não a margem bruta que as pessoas presumem |
| [Desperta](projects/desperta.md) | Swift · iOS · AlarmKit · Vision | Alarme que só desliga depois que você levanta de verdade, validado pela câmera |
| [Database engineering system](projects/database-engineering-system.md) | PostgreSQL · Supabase · agentes de IA | Sistema de agentes especialistas que audita e evolui um banco de produção sob um protocolo rígido |

---

## O que eu não publico

Pipelines, métricas ou regras de negócio de empresa não sobem — nem com os dados trocados. A lógica é propriedade intelectual, e trocar o dado não muda isso. O trabalho feito dentro de empresas aparece aqui como case study: o problema, a arquitetura, os trade-offs e a minha contribuição, sem código proprietário. Sem credenciais, sem dado de cliente, sem projeto de tutorial.

É por isso que os case studies acima não têm repositório anexado. É uma escolha deliberada, e o raciocínio está no [roadmap](roadmap.md#what-i-do-not-publish-and-why), junto com [o que estou construindo a seguir](roadmap.md).

---

## Contato

- **E-mail** limamarcelinog@gmail.com
- **LinkedIn** [gabriellimamarcelino](https://www.linkedin.com/in/gabriellimamarcelino)
- **Localização** Florianópolis, Santa Catarina, Brasil — disponível para trabalho remoto em outros fusos
