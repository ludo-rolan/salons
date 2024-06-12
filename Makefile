
#############################
# Dockers
#############################

up:
	cp -f app/wp-config-local.php app/wp-config.php
	docker-compose up -d
	
killall:
	sudo docker kill $$(sudo docker ps -q)

start:
	docker-compose start

stop:
	docker-compose stop

status:
	docker-compose ps

docker-rebuild:
	docker-compose stop
	docker-compose pull
	docker-compose rm --force app
	docker-compose build --no-cache --pull
	docker-compose up -d --force-recreate

#############################
# MySQL
#############################

mysql-backup:
	bash ./scripts/backup.sh mysql

mysql-restore:
	bash ./scripts/restore.sh mysql

#############################
# SCSS
#############################

sass-watch: 
	bash ./scripts/scss.sh watch $(filter-out $@,$(MAKECMDGOALS))

sass-build: 
	bash ./scripts/scss.sh build $(filter-out $@,$(MAKECMDGOALS))
af-preprod:
	ssh  wpk@af-preprod.pilotsystems.net './deploy_af.sh; exit; bash -l'
af-prod:
	ssh  wpk@af-front.pilotsystems.net './deploy_af.sh; exit; bash -l'
