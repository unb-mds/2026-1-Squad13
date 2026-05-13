FROM node:20-slim

WORKDIR /app

# Copia os arquivos de dependências
COPY package.json package-lock.json ./

# Instala as dependências
RUN npm install

# Copia o restante do código
COPY . .

# Expõe a porta do Vite
EXPOSE 5173

# Comando para rodar em modo desenvolvimento
# O --host é necessário para o Vite aceitar conexões vindas de fora do container (como do seu navegador)
CMD ["npm", "run", "dev", "--", "--host"]
