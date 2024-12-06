FROM mysql:latest

# Set the root password for MySQL
ENV MYSQL_ROOT_PASSWORD 1234
ENV MYSQL_ROOT_HOST='%'

# Copy custom SQL scripts to be executed during initialization
COPY init.sql /docker-entrypoint-initdb.d/

# Expose the default MySQL port (3306)
EXPOSE 3306


# sudo docker exec -it wildforge-db mysql -u root -p -e "SHOW DATABASES;"
# sudo docker exec -it wildforge-db mysql -u root -p -e "USE WildforgeDB; SHOW TABLES;"