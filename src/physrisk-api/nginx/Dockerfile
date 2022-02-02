FROM nginx:1.11.3

# remove the default NGINX configuration files
RUN rm /etc/nginx/nginx.conf

# copying the new NGINX configuration files from this directory to their appropriate locations in the NGINX image
COPY nginx.conf /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
COPY family_recipes.conf /etc/nginx/conf.d/