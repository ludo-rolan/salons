#++++++++++++++++++++++++++++++++++++++
# MySQL Docker container
#++++++++++++++++++++++++++++++++++++++

# MariaDB 10.2 ubuntu bionic release
FROM mariadb:10.2

ADD conf/mysql.conf /etc/mysql/conf.d/z99-docker.cnf
RUN chown mysql:mysql /etc/mysql/conf.d/z99-docker.cnf \
    && chmod 0644 /etc/mysql/conf.d/z99-docker.cnf
