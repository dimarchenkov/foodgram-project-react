FROM nginx:mainline-alpine3.18
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY result_build /usr/share/nginx/html/frontend
COPY custom_404.html /usr/share/nginx/html
COPY docs /usr/share/nginx/html/api/docs