# Git e GitHub

## O que é Git
Git é um sistema de controle de versão distribuído (DVCS), projetado para lidar eficientemente com projetos de qualquer tamanho. O Git permite que várias pessoas trabalhem em um projeto simultaneamente, rastreando as mudanças em cada parte do código ao longo do tempo.
Em termos simples, o Git permite que você mantenha um histórico de alterações em seu código, facilitando a colaboração em equipe e o gerenciamento de projetos. Cada contribuição é registrada como um "commit", que contém uma descrição da alteração e uma referência única (hash).

## O que é GitHub
GitHub, por outro lado, é uma plataforma de hospedagem de código que utiliza o Git. Fundado em 2008, o GitHub fornece um ambiente colaborativo para desenvolvedores trabalharem em projetos, facilitando o compartilhamento, colaboração e controle de versão. É especialmente popular devido à sua interface amigável e a uma série de recursos que vão além do controle de versão.

## Instalação e Configuração do Git no Windows:
Acesse o site oficial do Git para Windows.
Clique no botão "Download" para baixar o instalador.
Instalação:
Execute o instalador baixado.
Siga as instruções na tela, aceitando as configurações padrão, a menos que você tenha uma razão específica para alterá-las.
Configuração Inicial:
Após a instalação, abra o "Git Bash" (um terminal Git para Windows).
Configure seu nome de usuário e endereço de e-mail:
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"

## Instalação e Configuração do Git no Linux:
### Instalação via Terminal:
#### Em distribuições baseadas no Debian (como Ubuntu):
sudo apt-get update
sudo apt-get install git

#### Em distribuições baseadas no Red Hat (como Fedora):
sudo yum install git

### Configuração Inicial:
Abra um terminal e configure seu nome de usuário e endereço de e-mail:
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"

## Principais comandos Git

### git init
Inicia um novo repositório Git no diretório atual.

### git clone [URL]
Clona um repositório Git existente para o diretório local.

### git add .
Adiciona alterações ao índice (staging area) para prepará-las para o commit.

### git commit -m "mensagem"
Realiza um commit com as alterações adicionadas, incluindo uma mensagem que descreve as mudanças feitas.

### git status
Exibe o estado atual do repositório, indicando quais arquivos foram modificados, adicionados ou removidos.

### git log
Mostra o histórico de commits do repositório.

### git branch
Lista todas as branches locais e destaca a branch atual.

### git branch [nome-da-branch]
Cria uma nova branch.

### git checkout [nome-da-branch]
Altera para uma branch específica.

### git merge [branch]
Combina as alterações de uma branch para a branch atual.

### git pull
Atualiza o repositório local com as alterações do repositório remoto.

### git push [remote] [branch]
Envia os commits locais para o repositório remoto.

### git remote -v
Lista os repositórios remotos configurados.

### git fetch
Recupera as últimas alterações do repositório remoto, mas não faz merge automaticamente.

### git reset [arquivo]
Desfaz as alterações no arquivo especificado, removendo-o do índice.

### git rm [arquivo]
Remove um arquivo do repositório e o inclui no próximo commit.

### git diff
Mostra as diferenças entre as alterações que ainda não foram adicionadas ao índice.

### git remote add [nome-remoto] [URL]
Adiciona um repositório remoto com um nome específico.

### git push add origin main
Executado para efetuar push das alterações locais para o repositório online.