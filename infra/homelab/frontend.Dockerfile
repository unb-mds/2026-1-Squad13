# Estágio 1: Build da aplicação React
FROM node:20-alpine AS builder
WORKDIR /app
# Copia dependências a partir do contexto da raiz do projeto
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend ./

# Injeta o prefixo relativo para que as requisições de API usem a porta 8888
ENV VITE_API_URL=/api
RUN npm run build

# Estágio 2: Imagem final leve com Nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Copia a configuração do nginx mapeando a partir do diretório de infra
COPY infra/homelab/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8888
CMD ["nginx", "-g", "daemon off;"]
