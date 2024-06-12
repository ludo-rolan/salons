# -*- coding: utf-8 -*-
from fabric.api import *
from fabric.operations import put , get , local as localrun
from fabric.context_managers import lcd
from fabric.contrib.project import rsync_project
from subprocess import call

#from dogapi.fab import setup as setup_dg, notify as notify_dg
#setup_dg("c204ed9f436978f3fb08c47ff236da4d")

## Pour synchroniser : 
# fab preprod generate_css_for_subdirectories
# fab local loaddb fix_db_domains

## Pour synchroniser un seul site du reseau avec X le numero du site :
# fab preprod getdb:dbfile=site_X.sql.gz    
# fab local loaddb:dbfile=site_X.sql fix_db_domains


################################
# Initialisation à la docker style 
#
# 1 - Setup ssl certificate pour telecharger les images wpk ( MAC )
# screen ~/Library/Containers/com.docker.docker/Data/com.docker.driver.amd64-linux/tty
# entrer > root
# mkdir -p /etc/docker/certs.d/pp.webpick.info:5000
# cp /Users/%TON_CHEMINVERSPROJET%//certs/domain.crt /etc/docker/certs.d/pp.webpick.info\:5000/ca.crt
# Avec docker toolbox : fab local init_ca_machine
# 2 - Copy les volumes mysql dans ./dockers/volumes
# 3 - cp ./wp-config.docker.rw.php wp-config.php
# Setup db credentials sur wp-config.php ( user user= root , password = root , host = db )
# Login to docker with : fab local docker_login
# 4 - Enjoy : docker-compose up -d


######################################
# Running tests by theme 
#  - To run unit testing using docker :
# 1 - before the first run you must pull the docker image, you may need to setup the ssl certificate as explained above 
#  	docker pull pp.webpick.info:5000/wpk/phpfpm   
# 2- add on the config file "wordpress-tests-lib/wp-tests-config.php" the config below:
# 	define( 'DB_NAME', 'wordpress_tests' );
# 	define( 'DB_USER', 'wp' );
# 	define( 'DB_PASSWORD', 'wp' );
# 	define( 'DB_HOST', 'db' );
# 3- then run the commane
#  fab theme_tests:theme={$theme}
#  @args : $theme -> the name of the theme folder 
#  Each theme folder should contain : phpunit.xml to startup tests.
#
######################################
# Running fonctionnal tests 
# - first install casperjs
# brew install casperjs
# then simply run the  commande:  
# fab local func_tests
# 
# ###################################### Install Codeception ######################################
# 
# Pull the last docker image
# docker pull pp.webpick.info:5000/wpkphp
# In case it doesn't work, setup the ssl certificate 
###### screen ~/Library/Containers/com.docker.docker/Data/com.docker.driver.amd64-linux/tty
###### entrer > root
###### mkdir -p /etc/docker/certs.d/pp.webpick.info:5000
###### cp /Users/%TON_CHEMINVERSPROJET%//certs/domain.crt /etc/docker/certs.d/pp.webpick.info\:5000/ca.crt
# Create a new Database and name it 'wordpress_tests'
# Export this database and place it in the folder ./backup 
 

import os
import glob

import datetime


if env.ssh_config_path and os.path.isfile(os.path.expanduser(env.ssh_config_path)):
    env.use_ssh_config = True
else:
    env.use_ssh_config = False


import logging
logging.basicConfig()

# all blogs definitions
blogs_def = {

1 : { 'theme':'reworldmedia' , 'name':'network'  ,'is_master' : True, 'url_live' : 'network.viepratique.fr' } ,
2 : { 'theme':'gourmand' , 'name':'gourmand' , 'url_live' : 'gourmand.viepratique.fr' } ,
3 : { 'theme':'sante' , 'name':'sante' , 'url_live' : 'sante.viepratique.fr' },
4 : { 'theme':'feminin'  ,'name':'feminin'  , 'url_live' : 'www.viepratique.fr' } , 
5 :  { 'theme':'mariefrance'   , 'name':'mariefrance'   , 'url_live' : 'www.mariefrance.fr' } ,
6 :  { 'theme' :'onepage' ,  'name' :'content' , 'url_live':'content.viepratique.fr'} ,
7 :  { 'theme' :'asia' ,'name' :'asia' , 'url_live':'www.mariefranceasia.com'} ,
8 :  { 'theme' :'deco' ,'name' :'deco' , 'url_live':'www.lejournaldelamaison.fr'} ,
9 :  { 'theme' :'automoto' ,'name' :'automoto' , 'url_live':'www.auto-moto.com'} ,
10 :  { 'theme' :'gourmandasia' ,'name' :'gourmandasia' , 'url_live':'www.gourmandasia.com'},
11 :  { 'theme' :'beasia' ,'name' :'beasia' , 'url_live':'asia.be.com'},
12 :  { 'theme' :'telemag' ,'name' :'telemag' , 'url_live':'news.telemagazine.fr'},
#13 :  { 'theme' :'union' ,'name' :'union' , 'url_live':'union.viepratique.fr'}
14 :  { 'theme' :'automoto' ,'name' :'derapages' , 'url_live':'lesderapages.auto-moto.com'},
15 :  { 'theme' :'rdv' ,'name' :'rdv' , 'url_live':'www.reprisedevolee.com'}
}
latest_blog = len(blogs_def)

def set_blog(id_blog):
    id_blog = int(id_blog)
    env.id_blog = id_blog
    env.theme = blogs_def[env.id_blog]['theme']
    
    env.blog_name = 'name' in blogs_def[id_blog] and blogs_def[id_blog]['name'] or env.theme
    if id_blog ==1:
        env.url_local= env.hosts[0] 
    else:
        env.url_local= '%s.%s' % ( env.blog_name ,  env.hosts[0]  )
    env.url_live= get_blog_url(id_blog , env.hosts[0])
    env.local_theme = 'wp-content/themes/%s' % env.theme

def get_blog_url(id_blog , host ):
    return 'url_live' in blogs_def[id_blog] and  blogs_def[id_blog]['url_live'] or "%s.%s" % ( blogs_def[id_blog]['name'] , host )

env.blogs = blogs_def.keys()


env.basepath = '/'



env.config = 'config'


env.mysqldump =  'mysqldump'
env.mysql =  'mysql'
env.dbhost = 'localhost'
env.dbport = '3306'
env.mongohost = 'localhost:27017'

env.phpunit = 'phpunit'


env.dbignore = [  ] # set this up later

env.wd = os.getcwd()

env.local_dbbackup = 'backup'

env.theme_path = ''

env.project= 'Reworlmadia network'

def link_uploads():
    env_run( 'mkdir -p %s/wp-content/uploads && chmod -R 777 %s/wp-content/uploads' % ( env.deploy_to, env.deploy_to ) )
    if 'uploads_dir' in env:
        env_run(  'ln -sfn  %s  %s/wp-content/uploads/%s' % (  env.uploads_dir , env.deploy_to , env.uploads_symlink ) )

def init_be():
    localrun("git submodule add -b light git@github.com:snicks1/reworldmedia-network.git wp-content/themes/be" )
    print ("You shoud update the wp-config.php and virtualhosts...")
    #localrun("cd wp-content/themes/be && git checkout ligh" )

def init_sporever(repo='web-pick'):
    localrun("git submodule add git@github.com:"+repo+"/sporever.git wp-content/themes/sporever" )
    localrun("cd wp-content/themes/sporever && git submodule init && git submodule update" )
    
def clone_project(project='' , user='webpick'):
    env_run ('cd %s/wp-content/themes && git clone ssh://git@pp.webpick.info:2229/%s/%s.git %s' % (env.deploy_to , user , project , project  ) )


def generate_css() :  
    themes_directory = "/wp-content/themes/" 
    # get the absolute path of the current directory
    absolute_path = os.getcwd()
    themes_directory = absolute_path+themes_directory

    generate_css_for_subdirectories(themes_directory)
    print ("compile des sass est realise")

def generate_css_for_subdirectories(themes_directory):
    compass_command  = "compass"
    compass_option   = "compile --force "
    sass_directory   = "/assets/bootstrap-sass/"
    file_to_compile  = "sass/colors.scss"
    sass_compile_command =  compass_command+' '+compass_option+' '+ file_to_compile


    # get subdirectories of themes
    themes = next(os.walk(themes_directory))[1]

    # loop throught themes
    for theme in themes :
        current_directory = themes_directory+theme
        if(current_directory.endswith('themes/deco',2)) :
            generate_css_for_subdirectories(current_directory+'/')
            continue

        bootstrap_sass_dir = themes_directory+theme+sass_directory 
        # check if the directory and the sass file exist
        if os.path.isdir(bootstrap_sass_dir) and os.path.exists(bootstrap_sass_dir+file_to_compile):
            print (bootstrap_sass_dir+file_to_compile)
            command = "cd " + bootstrap_sass_dir +" && " + sass_compile_command
            #run the command 
            call(command, shell=True)
            print ('------')


def rebase(repo='abdellatif' , branch='master'):
    localrun("git fetch %s && git diff master %s/%s" %  ( repo , repo , branch ) )
    response = prompt("Is code review OK ? [y]");
    if response == 'y' :
        localrun("git rebase %s/%s" %  ( repo , branch ) )
        #test_sites()

        localrun("git push" )
        print ('You should deploy now fab env deploy')
    else :
        print ('Not Merging %s / %s' % ( repo , branch ))


def rebasedev(repo='idriss' , branch='master'):
    master_dev = '%s_%s' % ( repo , branch )
    # fetch
    localrun("git pull -f %s %s:%s" % ( repo , branch ,  master_dev )  )
    # rebase dev to master
    localrun("git checkout %s && git rebase master && git checkout master" % ( master_dev )  )
    # show diff 
    localrun("git diff master %s" %  ( master_dev ) )
    response = prompt("Is code review OK ? [y]");
    if response == 'y' :
        localrun("git rebase %s" %  ( master_dev ) )
        localrun("git push")
    else:
        print ('Not Merging %s' % ( master_dev ))


def old_deploy(hashfrom=False):
    if hashfrom:
        # need to get revision
        localrun ('git log --pretty="%s" %s^..HEAD > CHANGELOG.txt' % ( "%ci => %cn : %s" , hashfrom )  )
    localrun ('git shortlog -n --since="0am"  > REPORT.txt' )
    #env_run ('git add CHANGELOG.txt && git commit -m "Mise a jour changelog" && git push ')
    if 'dandelion_file' in env:
        dandelion = '--config=%s.yml' % env.dandelion_file
    else :
        dandelion = ''
    localrun ('dandelion %s deploy' % dandelion )
    send_report()


def init_config(environnement='pp'):
    env_run( 'cp -f %s/wp-config.%s.php  %s/wp-config.php' % ( env.deploy_to , environnement , env.deploy_to  ) )


def init_project_config(theme):
	env_run( 'cp -f %s/wp-content/themes/%s/wp-config.*.php  %s/' % ( env.deploy_to , theme , env.deploy_to  ) )
	env_run( 'cp -f %s/wp-content/themes/%s/%s_fab.py  %s/' % ( env.deploy_to , theme , theme, env.deploy_to  ) )
	env_run( 'cp -f %s/wp-content/themes/%s/%s_config.pp.py  %s/%s_config.py' % ( env.deploy_to , theme , theme, env.deploy_to , theme ) )


def deploy(server='' , do_notify = True , hash= ''):
    if 'dandelion_file' in env:
        dandelion = '--config=%s.yml' % env.dandelion_file
    else :
        dandelion = ''

    import re
    
    if server:
        server="DEPLOY_TO=%s" % server
    #fh = StringIO();
    #localrun("dandelion --config=dandelion_be.yml status", stdout=fh)
    if do_notify:
        fh = localrun("%s dandelion %s status"  % (server , dandelion )  , capture=True)
        m = re.search('^Remote revision:\s+([a-f0-9]{40})$',fh, re.M)
    else:
        m=True

    if not m:
        abort('Can\'t find revision from dandelion')
    else:
        if do_notify:
            hashfrom = m.group(1)
            #print(hashfrom)
            # need to get revision
            localrun ('git log --pretty="%s" %s^..HEAD > CHANGELOG-%s.txt'  % ( "%ci => %cn : %s" , hashfrom , env.name)  )
            generate_daily_report( env.wd )
        localrun ('%s dandelion %s deploy %s'  %  (server , dandelion , hash )  )
        
        if (hasattr(env, 'cache_mo')): 
        	clean_mo_cache(env.cache_mo)
        	
        refresh_cdn()
        
        if do_notify:
            notify()

def deploy_revision():
	send_a_file('%sconfig/sparse-checkout' % env.theme_path , '%s/.git/info/sparse-checkout' % env.deploy_to)
	env_run ('cd %s && git fetch && git log master..origin/master > CHANGELOG.txt' % env.deploy_to)
	env_run ('cd %s && git pull -r origin master' % env.deploy_to)
    
	clean_mo_cache(env.cache_mo)
	refresh_cdn()


	notify_release()


def deploy_git():
	send_a_file('%sconfig/sparse-checkout' % env.wd , '%s/.git/info/sparse-checkout' % env.deploy_to)
	
	env_run ('cd %s && git fetch && git log %s..origin/%s > CHANGELOG.txt' %( env.deploy_to, env.branch, env.branch))
	
	env_run ('cd %s && git pull -r origin ' % env.deploy_to)
    
	clean_mo_cache(env.cache_mo)
	refresh_cdn()

	notify_git()


def notify_git():
	if env.name == 'prod' :
		destinataires = 'rw_depot@googlegroups.com,jparola@reworldmediafactory.fr,hbaillet@reworldmediafactory.fr,ccanzi@reworldmediafactory.fr,techrem@ig-1.net,lauzanneau@reworldmediafactory.fr'
		deploy_dir = env.deploy_to

	else :
		destinataires = 'rw_depot@googlegroups.com'
		deploy_dir =  env.deploy_to 

	env_run ('mail -s "Deployement sur environnement %s" %s < %s/CHANGELOG.txt || echo "Cant notify"' % ( env.name , destinataires, deploy_dir))





def init_deploy_core_dirs():
	if env.name == 'prod' :
		branch = 'master'
	else:
		branch = 'preprod' 
	
	env_run ('cd %s && mkdir release && cd release && git init && git remote add -f origin git@github.com:web-pick/reworldmedia-network.git' % env.deploy_to )
	env_run ('cd %s/release && git config core.sparseCheckout true' % env.deploy_to )
	send_a_file('%swp-content/themes/reworldmedia/sparse-checkout' %env.wd , '%s/release/.git/info/sparse-checkout' % env.deploy_to)
	env_run ('cd %s/release && git pull origin %s' % (env.deploy_to, branch) )
	env_run('ln -sfn %s/uploads %s/release/wp-content/uploads' % (env.deploy_to, env.deploy_to) )
	
	env_run ('cd %s && mkdir backup && cd backup && git init && git remote add -f origin git@github.com:web-pick/reworldmedia-network.git' % env.deploy_to )
	env_run ('cd %s/backup && git config core.sparseCheckout true' % env.deploy_to )
	send_a_file('%swp-content/themes/reworldmedia/sparse-checkout' %env.wd , '%s/backup/.git/info/sparse-checkout' % env.deploy_to)
	env_run ('cd %s/backup && git pull origin %s' % (env.deploy_to, branch) )
	env_run('ln -sfn %s/uploads %s/backup/wp-content/uploads' % (env.deploy_to, env.deploy_to) )

def init_pp_config():
	send_a_file('%swp-config.pp.rw.php' % env.wd , '%s/release/wp-config.php' % env.deploy_to)
	send_a_file('%swp-config.pp.rw.php' % env.wd , '%s/backup/wp-config.php' % env.deploy_to)

def deploy_release():
	deploy_dir = '%s/current' % env.deploy_to 
	if env.name == 'prod' :
		branch = 'master'
	else:
		branch = 'preprod' 
	send_a_file('%ssparse-checkout' % env.theme_path , '%s/.git/info/sparse-checkout' % deploy_dir)
	env_run ('cd %s && git fetch && git log %s..origin/%s > CHANGELOG.txt' % (deploy_dir, branch, branch))
	env_run ('cd %s && git pull -r origin %s' % (deploy_dir, branch))
	#switch dirs names 
	#env_run ('cd %s && mv release  _backup && mv backup release && mv _backup backup ' % env.deploy_to)
	# symlink
	#env_run('ln -sfn %srelease/ %scurrent' % (env.deploy_to, env.deploy_to))
	notify_release()


	
def rollback_release():
	env_run('ln -sfn %sbackup/ %scurrent' % (env.deploy_to, env.deploy_to))

def notify_release():
	if env.name == 'prod' :
		destinataires = 'rw_depot@googlegroups.com,jparola@reworldmediafactory.fr,hbaillet@reworldmediafactory.fr,ccanzi@reworldmediafactory.fr,techrem@ig-1.net,lauzanneau@reworldmediafactory.fr'
		deploy_dir = env.deploy_to

	else :
		destinataires = 'rw_depot@googlegroups.com'
		deploy_dir = '%s/current' % env.deploy_to 

	env_run ('mail -s "Deployement sur environnement %s" %s < %s/CHANGELOG.txt || echo "Cant notify"' % ( env.name , destinataires, deploy_dir))


def clean_mo_cache(dircache):
	env_run( 'rm -f %s/*.mo.php ' % dircache )

def generate_daily_report(source='.'):
    old = os.getcwd()
    # http://docs.fabfile.org/en/latest/api/core/context_managers.html#fabric.context_managers.lcd
    lcd( source )
    localrun ( 'git --no-pager shortlog --numbered --since="0am" HEAD > REPORT.txt' )
    lcd( old )




def refresh_cdn():
    import time 
    from time import sleep
    sleep (3)
    if 'to_screen' in env:
        for site in env.to_screen:
            localrun ('open https://%s/?newcdn=%s'  % ( site , time.time() )   )

def upload_report():
    send_file('REPORT.txt')

def send_file(file_name='REPORT.txt',file_dist=''):
	if file_dist =='':
		file_dist = file_name

	if 'project_path' in env:
		project_path = env.project_path
	else:
		project_path = env.deploy_to	

	put ( '%s/%s' %  ( env.wd, file_name ) , '%s%s' %   ( project_path, file_dist )  )



def remove_file(file_dist):
	

	if 'project_path' in env:
		project_path = env.project_path
	else:
		project_path = env.deploy_to	

	run ( 'rm %s%s' %   ( project_path, file_dist )  )


def get_file(file_name,file_dist=''):


	if 'project_path' in env:
		project_path = env.project_path
	else:
		project_path = env.deploy_to

	if file_dist =='':
		file_dist = file_name
	get ( '%s/%s' %  ( project_path, file_dist ) , '%s/%s' % ( env.wd, file_name  )  )



def send_a_file(origin_file, destination_file):
    put ( '%s' %  origin_file , '%s' %  destination_file )


def notify():
    put ( '%s/CHANGELOG-%s.txt' %  ( env.wd , env.name  ) , '%sCHANGELOG.txt' %  env.deploy_to )
    upload_report()
    if env.name == 'prod' :
    	destinataires = 'rw_depot@googlegroups.com,jparola@reworldmediafactory.fr,hbaillet@reworldmediafactory.fr,ccanzi@reworldmediafactory.fr,techrem@ig-1.net'
    else :
    	destinataires = 'rw_depot@googlegroups.com'
    env_run ('mail -s "Deployement sur environnement %s" %s < %sCHANGELOG.txt || echo "Cant notify"' % ( env.name , destinataires, env.deploy_to))
def send_report():
    put ( '%s/REPORT.txt' %  env.wd , '%sREPORT.txt' % env.deploy_to )
    env_run ('mail -s "Rapport des commits de la journee sur %s" rw_depot@googlegroups.com < %sREPORT.txt || echo "Cant notify" ' % ( env.name , env.deploy_to))


def env_run(command):
    if env.name == 'local' or env.name == 'local_win' :
        localrun(command)
    elif env.name == 'docker' :
    	localrun("docker exec -ti %s sh -c '%s'" % ( env.container , command) ) 
    else:
        run(command)    



def setup_only():
    env.setup_only=True

    env.local_deploy_to = '.'   
    env.local_dbbackup = '%s/backup' % (  env.local_deploy_to  )


from config import *



def union():
    global blogs_def
    blogs_def = {
        1 : { 'theme':'union' , 'name':'union'  ,'is_master' : True, 'url_live' : 'www.union.fr' } ,
      
    }
    from config import upreprod_env, uprod_env, ulocal_env
    global preprod_env , prod_env, local_env
    preprod_env = upreprod_env
    prod_env = uprod_env
    local_env = ulocal_env

    
def set_config(env_config):

    for key in env_config:
        env[key] = env_config[key]

    if 'dbbackup' not in env:
    	if 'deploy_to' in env:
        	env.dbbackup = '%s/backup' % env.deploy_to

    for key in [ 'mysqlimport' , 'mysqldump' ] :
        if key not in env :
            env[key] = key

    """
    env.name = env_config[name
    env.user = env_config.user
    env.group= env_config.group
    env.deploy_to = env_config.deploy_to
    env.dbname = env_config.dbname
    env.dbuser = env_config.dbuser
    env.dbpass = env_config.dbpass
    env.hosts = env_config.hosts
    env.deploy_path =  env.deploy_to
    """
    
    env.blogs = blogs_def.keys()
    print (env_config)



#@task
def local():
    if 'local_env' in env:
        set_config(env.local_env)
    else:
        set_config(local_env)

def preprod():
	if 'preprod_env' in env:
		set_config(env.preprod_env)
	else:
		set_config(preprod_env)

def isoprod():
    if 'isoprod_env' in env:
        set_config(env.isoprod_env)
    else:
        set_config(isoprod_env)


def prod():
    if 'prod_env' in env:
        set_config(env.prod_env)
    else:
        set_config(prod_env)

def docker():
    if 'docker_env' in env:
        set_config(env.docker_env)
    else:
        set_config(docker_env)




def test_me():
    env_run("echo 'test %s'" % env.name)

    """
    Commun targets
    envrun should use decide if we run local or remote command
    """

"""
Database manipulation
"""
def savedb():
    env_run ('mkdir -p %s' % (env.dbbackup) )
    if len(env.dbignore):
        ignore = ' --ignore-table=%s.' % ( env.dbname )
    else:
        ignore =''
    env_run ( 'cd %s && %s --opt --lock-tables=false -h %s -u %s --password=%s %s%s %s > latest-db.sql ' % ( env.dbbackup , env.mysqldump ,  env.dbhost , env.dbuser ,  env.dbpass , ignore  , ignore.join( env.dbignore)  , env.dbname  )  )



def savedb_partial():
    env_run ('mkdir -p %s' % (env.dbbackup) )
    prefix = 'wp_%s_' % env.id_blog
    tables = [ 
        '%scommentmeta' % prefix ,
        '%scomments' % prefix ,
        '%slinks' % prefix ,
        #'%soptions' % prefix ,
        '%spostmeta' % prefix ,
        '%sposts' % prefix ,
        '%sterm_relationships' % prefix ,
        '%sterm_taxonomy' % prefix ,
        '%sterms' % prefix ,
        '%sninja_forms' % prefix , 
        '%sninja_forms_fav_fields' % prefix ,
        '%sninja_forms_fields' % prefix ,
        '%sninja_forms_subs' % prefix ,
        '%squizz_answer' % prefix ,
        '%squizz_copyright' % prefix , 
        '%squizz_entry' % prefix ,
        '%squizz_entry_answer' % prefix ,
        '%squizz_home' % prefix ,
        '%squizz_partners' % prefix ,
        '%squizz_partners_by_quizz' % prefix ,
        '%squizz_question' % prefix ,
        '%squizz_quizz' % prefix ,
        '%squizz_subscriber' % prefix ,
        '%squizz_subscriber_partners' % prefix ,
        '%squizz_winners' % prefix ,
        '%ssam_ads' % prefix , 
        '%ssam_blocks' % prefix , 
        '%ssam_errors' % prefix , 
        '%ssam_places' % prefix , 
        '%ssam_stats' % prefix , 
        '%ssam_zones' % prefix ,
        'wp_users' , 
        'wp_usermeta'
    ]
    tables = ' '.join(tables)
    env_run ( 'mkdir -p %s/dump && chmod -R 777 %s/dump' % ( env.dbbackup , env.dbbackup ) )  
    env_run ( 'cd %s && %s --tab=dump --opt --lock-tables=false -h %s -u %s --password=%s %s %s ' % ( env.dbbackup , env.mysqldump , env.dbhost , env.dbuser ,  env.dbpass , env.dbname , tables )  )
    fix_tables(prefix)
    
def savedb_blog(id_blog):
    env_run ('mkdir -p %s' % (env.dbbackup) )
    prefix = 'wp_%s_' % id_blog
    tables = [ 
        '%scommentmeta' % prefix ,
        '%scomments' % prefix ,
        '%slinks' % prefix ,
        #'%soptions' % prefix ,
        '%spostmeta' % prefix ,
        '%sposts' % prefix ,
        '%sterm_relationships' % prefix ,
        '%sterm_taxonomy' % prefix ,
        '%sterms' % prefix ,
        '%sninja_forms' % prefix , 
        '%sninja_forms_fav_fields' % prefix ,
        '%sninja_forms_fields' % prefix ,
        '%sninja_forms_subs' % prefix ,
        '%squizz_answer' % prefix ,
        '%squizz_copyright' % prefix , 
        '%squizz_entry' % prefix ,
        '%squizz_entry_answer' % prefix ,
        '%squizz_home' % prefix ,
        '%squizz_partners' % prefix ,
        '%squizz_partners_by_quizz' % prefix ,
        '%squizz_question' % prefix ,
        '%squizz_quizz' % prefix ,
        '%squizz_subscriber' % prefix ,
        '%squizz_subscriber_partners' % prefix ,
        '%squizz_winners' % prefix ,
        '%ssam_ads' % prefix , 
        '%ssam_blocks' % prefix , 
        '%ssam_errors' % prefix , 
        '%ssam_places' % prefix , 
        '%ssam_stats' % prefix , 
        '%ssam_zones' % prefix ,
        'wp_users' , 
        'wp_usermeta'
    ]
    tables = ' '.join(tables)
    env_run ( 'mkdir -p %s/dump && chmod -R 777 %s/dump' % ( env.dbbackup , env.dbbackup ) )  
    #print ( 'cd %s/dump && %s --opt --lock-tables=false -h %s -u %s --password=%s %s %s > %s-db.sql' % ( env.dbbackup , env.mysqldump , env.dbhost , env.dbuser ,  env.dbpass , env.dbname , tables, id_blog )  )
    #
    env_run ('cd %s/dump && %s --opt --lock-tables=false -h %s -u %s  --password=%s %s $(%s  -h %s -u %s --password=%s   -D %s -Bse "show tables like \'wp_%s_%%\'") > %s-db.sql && tar cvzf  %s-db.sql.tar.gz %s-db.sql ' % ( env.dbbackup , env.mysqldump , env.dbhost , env.dbuser ,  env.dbpass , env.dbname , env.mysql, env.dbhost, env.dbuser, env.dbpass , env.dbname, id_blog, id_blog, id_blog, id_blog ) )


def savedb_table(table):
    env_run ('mkdir -p %s' % (env.dbbackup) )

    env_run ( 'mkdir -p %s/dump && chmod -R 777 %s/dump' % ( env.dbbackup , env.dbbackup ) )  
    env_run ( 'cd %s/dump && %s --opt --lock-tables=false -h %s -u %s --password=%s %s %s > %s.sql && tar cvzf  %s.sql.tar.gz %s.sql ' % ( env.dbbackup , env.mysqldump , env.dbhost , env.dbuser ,  env.dbpass , env.dbname , table, table, table, table )  )





def fix_tables(prefix):
    # rename sql file to change prefixes
    env_run ( "cd %s/dump &&  mv wp_users.sql %s_users.sql && mv wp_users.txt %s_users.txt" % (  env.dbbackup, env.blog_name , env.blog_name )  )
    env_run ( "cd %s/dump &&  mv wp_usermeta.sql %s_usermeta.sql && mv wp_usermeta.txt %s_usermeta.txt" % ( env.dbbackup, env.blog_name , env.blog_name )  )
    env_run ( "cd %s/dump &&  for f in wp_*; do mv $f $(echo $f | sed 's/^%s/%s_/g'); done" % (  env.dbbackup , prefix , env.blog_name )  )
    
    # rename sql file contents to change tables
    env_run ( "cd %s/dump &&  sed -i -e  's/%s/%s_/g; s/wp_/%s_/g'   *.sql && rm -f *.sql-e" % ( env.dbbackup, prefix , env.blog_name , env.blog_name )  )



def loaddb(passwd='' , dbfile='network.sql'):
    env_run ( 'cd %s && [ -f %s.gz ] && gunzip %s.gz || echo "No file to unzip done"' % ( env.dbbackup , dbfile , dbfile ) )
    
    if passwd:
        env.dbpass=passwd
    env_run ( 'cd %s && %s --host=%s -u %s --password=%s %s < %s' % ( env.dbbackup  , env.mysql , env.dbhost ,  env.dbuser ,  env.dbpass , env.dbname , dbfile )  )


def run_db(passwd=''):
    if passwd:
        env.dbpass=passwd
    env_run ( '%s --host=%s -u %s --password=%s %s' % ( env.mysql ,  env.dbhost ,env.dbuser ,  env.dbpass , env.dbname  )  )

def fix_blogs():
    app_hostname= env.hosts[0]
    for blog in range ( 2 , latest_blog+1 ):
        print ("blog %s" % blog)
        condition_blog = " where blog_id=%s " % blog
        set_blog(blog)
        query = "update wp_blogs set domain= '%s.%s' %s " %  (  env.theme , app_hostname , condition_blog )
        print (query)
        env_run (  '%s --host=%s -u %s --password=%s %s -e "%s" || echo "Query failed, table doesnt exists, deleted website.."' % ( env.mysql , env.dbhost , env.dbuser ,  env.dbpass , env.dbname , query )  )


def fix_domain():
        
    # fix the url
    app_hostname= env.app_url
    origin_domain = env.load_from


    table = 'wp_options'      

    query = "delete from %s  where option_name like '%%transient%%'" %  (  table )
    print (query)
    env_run (  '%s --host=%s -u %s --password=%s %s -e "%s" || echo "Query failed, table doesnt exists, deleted website.."' % ( env.mysql , env.dbhost , env.dbuser ,  env.dbpass , env.dbname , query )  )
    
    
    query = "update %s set option_value= replace ( option_value , '%s' , '%s' ) where option_name='home' or option_name='siteurl' or option_name='domain' " %  (  table , origin_domain , app_hostname )
    print (query)
    env_run (  '%s --host=%s -u %s --password=%s %s -e "%s" || echo "Query failed, table doesnt exists, deleted website.."' % ( env.mysql ,  env.dbhost , env.dbuser ,  env.dbpass , env.dbname , query )  )
             
        

def fix_db_domains():
        
    # fix the url
    app_hostname= env.hosts[0]
    for blog in env.blogs:

        
        condition_blog = " where blog_id=%s " % blog
        
        set_blog(blog)
        if env.load_from=='live':
            origin_domain = env.url_live
        else:
            origin_domain = env.load_from

        # there is no main blog.. wp_1_options does not exist
        if blog and int(blog) >1:
            table = 'wp_%s_options' % blog
        else:
            main_site = origin_domain
            table = 'wp_options'      

        query = "delete from %s  where option_name like '%%transient%%'" %  (  table )
        
        print (query)

        mysql_cmd  = '%s --port=%s' % ( env.mysql , env.dbport )

        env_run (  '%s --host=%s -u %s --password=%s %s -e "%s" || echo "Query failed, table doesnt exists, deleted website.."' % (mysql_cmd,  env.dbhost , env.dbuser ,  env.dbpass , env.dbname , query )  )
        
        query = "DELETE a,b,c FROM wp_%s_posts a LEFT JOIN wp_%s_term_relationships b ON (a.ID = b.object_id) LEFT JOIN wp_%s_postmeta c ON (a.ID = c.post_id) WHERE a.post_type = 'revision'" %  (  blog, blog, blog )
        if blog and int(blog) >1:
            print (query) 
            #env_run (  '%s --host=%s -u %s --password=%s %s -e "%s" || echo "Query failed, table doesnt exists, deleted website.."' % (mysql_cmd,  env.dbhost, env.dbuser ,  env.dbpass , env.dbname , query )  )

        query = "update %s set option_value= replace ( option_value , '%s' , '%s' ) where option_name='home' or option_name='siteurl' or option_name='domain' " %  (  table , origin_domain ,env.url_local )
        
        print (query)
        env_run (  '%s --host=%s -u %s --password=%s %s -e "%s" || echo "Query failed, table doesnt exists, deleted website.."' % (mysql_cmd, env.dbhost, env.dbuser ,  env.dbpass , env.dbname , query )  )
             
        # and live blog url
        query = "update wp_blogs set domain= replace ( domain , '%s' , '%s' ) %s " %  (   origin_domain , env.url_local , condition_blog   )
        print (query)
        env_run (  '%s --host=%s -u %s --password=%s %s -e "%s" || echo "Query failed, table doesnt exists, deleted website.."' % (mysql_cmd,env.dbhost, env.dbuser ,  env.dbpass , env.dbname , query )  )

    query = "update wp_site set domain= replace ( domain , '%s' , '%s' ) " %  ( main_site , app_hostname  )
    print (query)
    env_run (  '%s --host=%s -u %s --password=%s %s -e "%s"' % ( mysql_cmd, env.dbhost, env.dbuser ,  env.dbpass , env.dbname , query )  )
 
"""
Production deployement
"""

def getdb(dbfile=''):
    if dbfile=='':
        dbfile='network.sql.gz'
    get ('%s/%s' % (env.dbbackup , dbfile )  , '%s/%s' % ( env.local_dbbackup , dbfile )   )

def putdb(dbfile=''):
    if dbfile=='':
        dbfile='latest-db.sql'
    env_run ('mkdir -p %s' % (env.dbbackup) )
    put ( '%s/%s' % ( env.local_dbbackup , dbfile  ) , '%s/%s' % (env.dbbackup , dbfile )   )

def get_images():
    get ('%s/wp-content/uploads/2014' % (env.wd )  , 'wp-content/uploads/')

"""
TESTING
"""
# Run test on the Docker env
def theme_tests(theme_name='', envir=''):
	if theme_name=='':
	    for blog in env.blogs:
	    	id_blog = int(blog)
	    	if os.path.exists('./tests/unit-%s' % blogs_def[id_blog]['name'] ):
	    		if envir=='deploy_env':
	    			localrun( '/vendor/bin/codecept run unit-%s' % blogs_def[id_blog]['name'] )
	    		else:
	    			localrun( 'docker exec reworldmedianetwork_app_1 /bin/bash -c "cd /data/vhosts/reworldmedia/ ; /vendor/bin/wpcept run unit-%s "' % blogs_def[id_blog]['name'] )
	else:
		localrun( 'docker exec reworldmedianetwork_app_1 /bin/bash -c "cd /data/vhosts/reworldmedia/ ; /vendor/bin/wpcept run unit-%s "' % theme_name )

# Run test directly in env
def unit_tests(theme="reworldmedia"):
	print ("Testing %s Theme" % theme)
	test_dir = "%s/wordpress-tests-lib/" % env.deploy_to
	env_run("cd wp-content/themes/%s/ && WP_TESTS_DIR=%s %s --tap -v" % (  theme, test_dir , env.phpunit) )
	print ("Testing Plugin Test Phalcon")
	env_run("cd wp-content/plugins/tests-phalcon/ && WP_TESTS_DIR=%s  %s --tap -v" %  ( test_dir , env.phpunit)  )

def test_sites(siteenv=''):
    from selenium import webdriver
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

    
    screens_path = '%s/screens_tests' %  env.wd 
    localrun('mkdir -p %s' %  screens_path )
    import re
    bad_sites=[]
    from time import sleep
    to_screen = 'to_screen%s' % siteenv

    for site in getattr( env , to_screen ) :
        if( 'browser_stack' in env ) :
            cfg = env.browser_stack
            #print cfg
            browser = webdriver.Remote(
                command_executor=cfg['command_executor'],
                desired_capabilities=cfg['desired_cap'] )
        else:
            browser = webdriver.phantomjs.webdriver.WebDriver()
        
        name_screen = re.sub (r'\/|\?|=' , '' , site )
        badscreenshot = '%s/#BADSITE%s.jpg' %  (screens_path , name_screen )
        url_to_screen =  'http://%s' %  ( site )
        print ('Url to screen %s as %s ' % ( url_to_screen , name_screen ))
        try:
            browser.get(  url_to_screen )
        except Exception as e:
            print ("COULDNT GET BROWSER TO %s : %s" % ( url_to_screen ,   str(e)  ) )
            exit(1)
        try:
            content = browser.find_element_by_tag_name("body").text
            assert ( "Fatal error:" not in content ) , 'Fatal ERROR in Content'
            assert ("Notice:" not in content ) , 'Notice in Content'
            assert ("Warning:" not in content)  , 'Warning in Content'
            assert ("Parse error: syntax error," not in content)  , 'Parse Error in Content' 
            
            browser.maximize_window()
            # scroll to view images.. lazy load
            for size in [ 500 , 1000 , 1500 , 2000 , 2500 , 3500 , 4000 , 5000 , 6000 , 0 ] :
                browser.execute_script("window.scrollTo(0, %s)" % size)
                sleep(0.20)

            # let the responsive work..
            sleep(1)
            screenshot = '%s/%s-%s-%s.jpg' %  (screens_path, env.name , name_screen, 'max'  )  
            browser.save_screenshot(screenshot)

            for width in [ 480 , 770 ] :
                browser.set_window_size(width , 500 )
                sleep(1)
                screenshot = '%s/%s-%s-%s.jpg' %  (screens_path, env.name , name_screen, width  )  
                browser.save_screenshot(screenshot)


        except Exception as e:
            bad_sites.append(site)
            try:
                browser.save_screenshot(badscreenshot)
            except:
                print ("COULDNT TAKE SCREENSHOT %s " % badscreenshot)
            browser.quit()
            print ("Error Detected in %s : %s " % ( url_to_screen , str(e) ))
            exit(1)

    browser.quit()            
    if len(bad_sites):
        print ("bad Sites : %s" % (  ','.join(bad_sites )))
        exit(1)



# load extra tasks
import os.path

if os.path.exists('./wp-content/themes/be') : 
    import sys
    sys.path.append('./wp-content/themes/be')
    from be_fab import *

    def be():
        global blogs_def
        blogs_def = {
            1 : { 'theme':'be' , 'name':'be'  ,'is_master' : True, 'url_live' : 'www.be.com' } ,
            2 : { 'theme':'be' , 'name':'asia' , 'url_live' : 'asia.be.com' } ,
            3 : { 'theme':'be' , 'name':'bresil' , 'url_live' : 'bresil.be.com' } ,
        }
        env.project= 'Be'
        env.blogs = blogs_def.keys()
        from config import bepreprod_env, beprod_env, belocal_env
        global preprod_env , isoprod_env, prod_env, local_env
        preprod_env = bepreprod_env
        print (preprod_env)
        prod_env = beprod_env
        print (local_env)
        local_env = belocal_env
        env.theme_path = 'wp-content/themes/be'

if os.path.exists('./wp-content/themes/sporever') : 
    import sys
    sys.path.append('./wp-content/themes/sporever')
    from se_fab import *
    #@task
    def se():
        global blogs_def
        blogs_def = {
            1 : { 'theme':'sporever' , 'name':'sporever'  ,'is_master' : True, 'url_live' : 'www.sport365.fr' }
        }
        env.blogs = blogs_def.keys()
        env.project= 'Sporever'
        from config import sepreprod_env, seprod_env, selocal_env , sedocker_env
        global preprod_env , prod_env, local_env, docker_env
        preprod_env = sepreprod_env
        #print preprod_env
        prod_env = seprod_env
        print (local_env)
        local_env = selocal_env
        docker_env = sedocker_env
        env.theme_path = 'wp-content/themes/sporever'

if os.path.exists('./wp-content/themes/dubai-media') : 
    import sys
    sys.path.append('./wp-content/themes/dubai-media')
    from du_fab import *
    #@task
    def du():
        global blogs_def
        blogs_def = {
            1 : { 'theme':'dubai-media' , 'name':'dubai-media'  ,'is_master' : True }
        }
        env.blogs = blogs_def.keys()
        env.project= 'Dubai'
        from config import dupreprod_env, duprod_env, dulocal_env , dudocker_env
        global preprod_env , prod_env, local_env, docker_env
        preprod_env = dupreprod_env
        prod_env = duprod_env
        local_env = dulocal_env
        docker_env = dudocker_env
        env.theme_path = 'wp-content/themes/dubai-media/' 
        env.du_theme = '%s/%s' % ( env.wd,env.theme_path)
        env.sudo_docker= ''

if os.path.exists('./wp-content/themes/biba') : 
    import sys
    sys.path.append('./wp-content/themes/biba')
    from du_fab import *
    #@task
    def biba():
        global blogs_def
        blogs_def = {
            1 : { 'theme':'biba' , 'name':'biba'  ,'is_master' : True }
        }
        env.blogs = blogs_def.keys()
        env.project= 'Biba'
        from config import bibapreprod_env, bibaprod_env, bibalocal_env , bibadocker_env
        global preprod_env , prod_env, local_env, docker_env
        preprod_env = bibapreprod_env
        prod_env = bibaprod_env
        local_env = bibalocal_env
        docker_env = bibadocker_env
        env.theme_path = 'wp-content/themes/biba/' 
        env.biba_theme = '%s/%s' % ( env.wd,env.theme_path)
        env.sudo_docker= ''

if os.path.exists('./wp-content/themes/chasseur-francais') : 
    import sys
    sys.path.append('./wp-content/themes/chasseur-francais')
    from du_fab import *
    #@task
    def lcf():
        global blogs_def
        blogs_def = {
            1 : { 'theme':'chasseur-francais' , 'name':'LCF'  ,'is_master' : True }
        }
        env.blogs = blogs_def.keys()
        env.project= 'LCF'
        from config import lcfpreprod_env, lcfprod_env, lcflocal_env , lcfdocker_env
        global preprod_env , prod_env, local_env, docker_env
        preprod_env = lcfpreprod_env
        prod_env = lcfprod_env
        local_env = lcflocal_env
        docker_env = lcfdocker_env
        env.theme_path = 'wp-content/themes/chasseur-francais/' 
        env.lcf_theme = '%s/%s' % ( env.wd,env.theme_path)
        env.sudo_docker= ''

if os.path.exists('./wp-content/themes/coronavirus') : 
    import sys
    sys.path.append('./wp-content/themes/coronavirus')
    from du_fab import *
    #@task
    def corona():
        global blogs_def
        blogs_def = {
            1 : { 'theme':'coronavirus' , 'name':'CORONA'  ,'is_master' : True }
        }
        env.blogs = blogs_def.keys()
        env.project= 'CORONA'
        from config import coronapreprod_env, coronaprod_env, coronalocal_env , coronadocker_env
        global preprod_env , prod_env, local_env, docker_env
        preprod_env = coronapreprod_env
        prod_env = coronaprod_env
        local_env = coronalocal_env
        docker_env = coronadocker_env
        env.theme_path = 'wp-content/themes/coronavirus/' 
        env.corona_theme = '%s/%s' % ( env.wd,env.theme_path)
        env.sudo_docker= ''

if os.path.exists('./wp-content/themes/bienalacampagne') : 
    import sys
    sys.path.append('./wp-content/themes/bienalacampagne')
    from du_fab import *
    #@task
    def balc():
        global blogs_def
        blogs_def = {
            1 : { 'theme':'bienalacampagne' , 'name':'Bienalacampagne'  ,'is_master' : True }
        }
        env.blogs = blogs_def.keys()
        env.project= 'BALC'
        from config import balcpreprod_env, balcprod_env, balclocal_env , balcdocker_env
        global preprod_env , prod_env, local_env, docker_env
        preprod_env = balcpreprod_env
        prod_env = balcprod_env
        local_env = balclocal_env
        docker_env = balcdocker_env
        env.theme_path = 'wp-content/themes/bienalacampagne/' 
        env.balc_theme = '%s/%s' % ( env.wd,env.theme_path)
        env.sudo_docker= ''

if os.path.exists('./wp-content/themes/auto-sites') : 
    import sys
    sys.path.append('./wp-content/themes/auto-sites')
    from du_fab import *
    #@task
    def autosites():
        global blogs_def
        blogs_def = {
            1 : { 'theme':'auto-sites' , 'name':'Bienalacampagne'  ,'is_master' : True }
        }
        env.blogs = blogs_def.keys()
        env.project= 'BALC'
        from config import autositespreprod_env, autositesprod_env, autositeslocal_env , autositesdocker_env
        global preprod_env , prod_env, local_env, docker_env
        preprod_env = autositespreprod_env
        prod_env = autositesprod_env
        local_env = autositeslocal_env
        docker_env = autositesdocker_env
        env.theme_path = 'wp-content/themes/auto-sites/' 
        env.autosites_theme = '%s/%s' % ( env.wd,env.theme_path)
        env.sudo_docker= ''

    def autoplus():
        global blogs_def
        blogs_def = {
            1 : { 'theme':'auto-sites' , 'name':'autoplus'  ,'is_master' : True }
        }
        env.blogs = blogs_def.keys()
        env.project= 'BALC'
        from config import autopluspreprod_env, autoplusprod_env, autopluslocal_env , autoplusdocker_env
        global preprod_env , prod_env, local_env, docker_env
        preprod_env = autopluspreprod_env
        prod_env = autoplusprod_env
        local_env = autopluslocal_env
        docker_env = autoplusdocker_env
        env.theme_path = 'wp-content/themes/auto-sites/' 
        env.autoplus_theme = '%s/%s' % ( env.wd,env.theme_path)
        env.sudo_docker= ''




if os.path.exists('./wp-content/themes/modesettravaux') : 
    import sys
    sys.path.append('./wp-content/themes/modesettravaux')
    from du_fab import *
    #@task
    def modesettravaux():
        global blogs_def
        blogs_def = {
            1 : { 'theme':'modesettravaux' , 'name':'Bienalacampagne'  ,'is_master' : True }
        }
        env.blogs = blogs_def.keys()
        env.project= 'BALC'
        from config import modesettravauxpreprod_env, modesettravauxprod_env, modesettravauxlocal_env , modesettravauxdocker_env
        global preprod_env , prod_env, local_env, docker_env
        preprod_env = modesettravauxpreprod_env
        prod_env = modesettravauxprod_env
        local_env = modesettravauxlocal_env
        docker_env = modesettravauxdocker_env
        env.theme_path = 'wp-content/themes/modesettravaux/' 
        env.autosites_theme = '%s/%s' % ( env.wd,env.theme_path)
        env.sudo_docker= ''



if os.path.exists('./wp-content/themes/lamidesjardins') : 
    import sys
    sys.path.append('./wp-content/themes/lamidesjardins')
    from du_fab import *
    #@task
    def lami():
        global blogs_def
        blogs_def = {
            1 : { 'theme':'lamidesjardins' , 'name':'lamidesjardins'  ,'is_master' : True }
        }
        env.blogs = blogs_def.keys()
        env.project= 'LAMI'
        from config import lamipreprod_env, lamiprod_env, lamilocal_env , lamidocker_env
        global preprod_env , prod_env, local_env, docker_env
        preprod_env = lamipreprod_env
        prod_env = lamiprod_env
        local_env = lamilocal_env
        docker_env = lamidocker_env
        env.theme_path = 'wp-content/themes/lamidesjardins/' 
        env.lami_theme = '%s/%s' % ( env.wd,env.theme_path)
        env.sudo_docker= ''

if os.path.exists('./dzfoot') : 
    # import sys
    # sys.path.append('./wp-content/themes/dubai-media')
    # from du_fab import *
    #@task
    def dz():
        global blogs_def
        blogs_def = {
            1 : {'name':'Dzfoot'  ,'is_master' : True }
        }
        env.blogs = blogs_def.keys()
        env.project= 'Dzfoot'
        from config import dzprod_env
        global prod_env
        prod_env = dzprod_env
        env.wd = os.getcwd() + '/../dzfoot'
        env.sudo_docker= ''




def campus():
    global blogs_def
    blogs_def = {
        1 : { 'theme':'campus' , 'name':'campus'  ,'is_master' : True }
    }
    env.blogs = blogs_def.keys()
    env.project= 'Campus'
    from config import campuspreprod_env, campusprod_env, campuslocal_env , campusdocker_env
    global preprod_env , prod_env, local_env, docker_env
    preprod_env = campuspreprod_env
    prod_env = campusprod_env
    local_env = campuslocal_env
    docker_env = campusdocker_env
    env.theme_path = 'wp-content/themes/campus/' 
    env.campus_theme = '%s/%s' % ( env.wd,env.theme_path)
    env.sudo_docker= ''

def mf():
    global blogs_def
    blogs_def = {
        1 : { 'theme':'mf' , 'name':'mf'  ,'is_master' : True }
    }
    env.blogs = blogs_def.keys()
    env.project= 'mf'
    from config import mfprod_env
    global  prod_env
    prod_env['deploy_to'] = mfprod_env['deploy_to']
    prod_env['hosts'] = mfprod_env['hosts']
    prod_env['to_screen'] = mfprod_env['to_screen']


def deco():
    global blogs_def
    blogs_def = {
        1 : { 'theme':'deco' , 'name':'deco'  ,'is_master' : True }
    }
    env.blogs = blogs_def.keys()
    env.project= 'deco'
    from config import decoprod_env
    global  prod_env
    prod_env['deploy_to'] = decoprod_env['deploy_to']
    prod_env['hosts'] = decoprod_env['hosts']
    prod_env['to_screen'] = decoprod_env['to_screen']




def switchto(envcopy):
    # prod_env['deploy_to'] = envcopy['deploy_to']
    # prod_env['hosts'] = envcopy['hosts']
    # prod_env['to_screen'] = envcopy['to_screen']

    for v in envcopy :
        prod_env[v] = envcopy[v]


def switchto_theme(envcopy):
    prod_env['deploy_to'] = envcopy['deploy_to']
    prod_env['hosts'] = envcopy['hosts']
    prod_env['to_screen'] = envcopy['to_screen']
    prod_env['deploy_theme_to'] = envcopy['deploy_theme_to']


def f1i():
	switchto(f1iprod_env)
def am():
	switchto( amprod_env)
def drp():
	switchto( drpprod_env)
def proam():
	switchto( proamprod_env)
def gourmand():
	switchto( gourmandprod_env)
def gourmandasia():
	switchto( gourmandasiaprod_env)
def vpf():
	switchto( vpfprod_env)
def mfa():
	switchto( mfaprod_env)	
def rdv():
	switchto( rdvprod_env)	
def svj():
	switchto( svjprod_env)
def hmft():
	switchto( hmftprod_env)
def urban():
	switchto( urbanprod_env)
def pv():
	switchto( pvprod_env)
def resgreen():
	switchto( resgreenprod_env)
def velux():
	switchto( veluxprod_env)
def entrenous():
	switchto( entrenousprod_env)
def damideco():
    switchto( damidecoprod_env)
def diapason():
    switchto( diapasonprod_env)
def nlbo():
    switchto( nlboprod_env)
def peaches():
    switchto(peachesprod_env)
def melty():
    switchto(meltyprod_env)
def grazia():
    switchto(graziaprod_env)
def telestar():
    switchto(telestarprod_env)
def gaming():
    switchto(gamingprod_env)
def mtpro():
    switchto(mtproprod_env)
def sv():
    switchto(svprod_env)
def airofmelty():
    switchto(airofmeltyprod_env)
def trendy():
    switchto(trendyprod_env)


# Accepted Drivers
# PhantomJS ( DEFAULT )
# selenium_hub
# browser_stack 

def run_test( driver = '', env_name = ''):
    if driver == '':
        if 'test_driver_env' not in env:
            driver = 'PhantomJS'
        else:
            driver = env.test_driver_env
    if env_name == '':
        env_name = env.name
    localrun("cd functional_tests/ && python generique_suite.py %s %s " % ( driver, env_name) )

env.docker_registry="pp.webpick.info:5000"
env.docker_registry_login="wpk"
env.docker_registry_password="wpk@dock.123"
def docker_login():
    #init_ca_machine() if docker toolbox
    # or 
    # init_docker_mac_certs if docker mac
    env_run("docker login --password=%s --username=%s  %s"  %  (  env.docker_registry_password , env.docker_registry_login  ,env.docker_registry  )   )



def docker_db( container='reworldmedianetwork_db_1' , database= '' ):
    mysql_run = "docker run -it --link %s:mysql --rm mysql sh -c 'exec mysql -h\"$MYSQL_PORT_3306_TCP_ADDR\" -P\"$MYSQL_PORT_3306_TCP_PORT\" -uroot -p\"$MYSQL_ENV_MYSQL_ROOT_PASSWORD\" %s '" % ( container, database )
    env_run(mysql_run)


def docker_load_data( container='reworldmedianetwork_db_1' , database= 'reworldmediadb', dump='network.sql' ):
    mysql_run = "docker run -it --link %s:mysql --rm -v `pwd`/backup:/backup mysql sh -c 'exec mysql -h\"$MYSQL_PORT_3306_TCP_ADDR\" -P\"$MYSQL_PORT_3306_TCP_PORT\" -uroot -p\"$MYSQL_ENV_MYSQL_ROOT_PASSWORD\" %s < /backup/%s'" % ( container, database, dump )
    env_run(mysql_run)

# not tested
def docker_run_query( container='reworldmedianetwork_db_1' , database= 'reworldmediadb', query='' ):
    mysql_run = "docker run -it --link %s:mysql --rm -v `pwd`/backup:/backup mysql sh -c 'exec mysql -h\"$MYSQL_PORT_3306_TCP_ADDR\" -P\"$MYSQL_PORT_3306_TCP_PORT\" -uroot -p\"$MYSQL_ENV_MYSQL_ROOT_PASSWORD\" %s < /backup/%s'" % ( container, database, dump )
    env_run(mysql_run)

def build_debs():
    env_run("docker build -t debgen dockers/deb_generator"   )
    env_run("docker run --rm -v `pwd`/debs:/debs debgen"   )

# Generic builder
def build_docker(path="dockers/casperjs" , name="casperjs" , args=''):
	#localrun("cd %s cp -Rf keys %s " % ( env.wd , docker_path  ) )
	localrun("cd %s && docker build %s -t %s ." % ( path , args , name ) )
	# build docker

def deploy_image(image="wpk/phpfpm"):
	# push to registry
	push_registry(image , 'tag')
	push_registry(image)

def push_registry( image="wpk/phpfpm" , action='push', docker_tag=""):
	docker_flag=""
	# push to registry
	if docker_tag=="":
		docker_tag=image
	if action=='push':
		image=''
	else:
	    action='tag '
	    docker_tag='%s:latest' % docker_tag

	localrun("docker %s %s %s/%s" % ( action,  image , env.docker_registry , docker_tag  ) )


def casper_tests(service ="tester"):
	IP = localrun( "docker inspect -f '{{ .NetworkSettings.IPAddress }}' reworldmedianetwork_nginx_1" , True )
	localrun("WEB=%s docker-compose -f %s run --rm %s" % ( IP , "docker-casperjs.yml" , service ) )

def func_tests():
	localrun('casperjs test tests/ --includes=tests/test_config.js')

env.sonar="sonar-scanner"

def sonar_scan():
	localrun("%s" %  env.sonar ) 





def init_ca_machine(machine="default"):
    cert_path_tmp = "/home/docker/registmp" 
    cert_root = "/etc/docker/certs.d/"
    cert_path = "%s/%s/" % (cert_root , env.docker_registry ) 
    output = localrun('docker-machine ssh %s "sudo [ -d %s ] || echo todo"' % ( machine, cert_path   ) , True)
    if ( output == 'todo' ) :
        localrun('docker-machine ssh %s "mkdir -p %s"' % ( machine , cert_path_tmp  ))
        localrun('docker-machine ssh %s "sudo mkdir -p %s"' % ( machine ,  cert_root  ))
        localrun("docker-machine scp certs/*.crt %s:%s" % ( machine , cert_path_tmp ))
        localrun('docker-machine ssh %s "sudo mkdir -p %s && sudo mv %s %s"' % ( machine , cert_path_tmp , cert_path_tmp , cert_path ))
    else :
        print ("Certificates already copied")   

def diff(author='Abdellatif', days='6'):
    output = localrun("git log  --since='%s days ago'  --author=%s  --format='%s'" %  (  days , author , '%H'), True )
    output = output.replace("\n", " ")
    output = localrun('git show %s > /tmp/diff.diff && subl /tmp/diff.diff' % ( output ), True)

# create symlink to git pre-commit config file 
def precommit():
	env_run('chmod a+x  %s/git_hooks/pre-commit' % (env.wd) )
	env_run( 'rm -f %s/.git/hooks/pre-commit '  % (  env.wd  )  )
	env_run( 'ln -s  %s/git_hooks/pre-commit %s/.git/hooks/pre-commit '  % (  env.wd , env.wd )  )

	if 'theme_path' in env:
		env_run( 'rm -f %s/%s/.git/hooks/pre-commit '  % ( env.wd, env.theme_path )  )
		env_run( 'ln -s  %s/git_hooks/pre-commit %s/%s/.git/hooks/pre-commit '  % (  env.wd , env.wd, env.theme_path )  )



# create symlink to git pre-push config file 
def prepush():
	env_run('chmod a+x  %s/git_hooks/pre-push' % (env.wd) )
	env_run( 'ln -s  %s/git_hooks/pre-push %s/.git/hooks/pre-push '  % (  env.wd , env.wd )  )

def start_xdebug():
	localrun('ssh -R 9900:localhost:9900 root@localhost -p 2222')


def rw_start_docker():
	env_run( 'cp %s/wp-config.docker.rw.php %s/wp-config.php && docker-compose up ' % (  env.deploy_to , env.deploy_to ) )

def qa():
	local()
	rw_start_docker()

def rw_start_docker_with_rebuild():
    env_run( 'cp %s/wp-config.docker.rw.php %s/wp-config.php && docker-compose up --build' % (  env.deploy_to , env.deploy_to ) )



def co_theme():
	env_run( 'cd %s/%s  && git checkout . ' % (env.deploy_to , env.theme_path ) )


def co():

	if 'project_path' in env:
		project_path = env.project_path
	else:
		project_path = env.deploy_to	

	env_run( 'cd %s  && git checkout . ' % ( project_path  ) )


def rw_deploy_theme():
	
	if env.name == 'prod' :
		branch = 'master'
	else:
		branch = 'preprod'
	
	env_run ('cd %s/%s && git fetch && git log %s..origin/%s > REPORT.txt' % (env.deploy_to, env.theme_path, branch, branch))

	env_run ('cd %s/%s && git pull -r' % (env.deploy_to, env.theme_path) )
	
	rw_notify_theme()



def rw_notify_theme():

	env_run ('mail -s "Deployement  %s %s" rw_depot@googlegroups.com < %s/%s/REPORT.txt' % ( env.project, env.name , env.deploy_to , env.theme_path ))


  
def wpk_deploy(refresh='1'):
	#send_a_file('%s/config/sparse-checkout' % env.wd , '%s/.git/info/sparse-checkout' % env.deploy_to)
	if 'origin_core_branch' in env:
		origin_core_branch = env.origin_core_branch
	else:
		origin_core_branch = env.origin_branch
		
	if 'destination_core_branch' in env:
		destination_core_branch = env.destination_core_branch
	else:
		destination_core_branch = env.destination_branch

	env_run  ('cd %s && git fetch && git log %s..origin/%s > CHANGELOG.txt' % ( env.deploy_to, destination_core_branch ,origin_core_branch ) )
	env_run ('cd %s && git pull -r origin %s:%s' % ( env.deploy_to, origin_core_branch, destination_core_branch ) )
	
	if 'cache_mo' in env and env.cache_mo  != '' :
		clean_mo_cache(env.cache_mo)
	if refresh == '1' :
		refresh_cdn()
	if 'do_not_notify' not in env:
	 	wpk_notify(env.deploy_to)

def wpk_deploy_theme():
	env_run ('cd %s && git fetch && git log %s..origin/%s > CHANGELOG.txt' % ( env.deploy_theme_to, env.destination_branch,env.origin_branch ) )
	env_run ('cd %s && git pull -r origin %s:%s' % ( env.deploy_theme_to, env.origin_branch, env.destination_branch ) )
	if 'cache_mo' in env and env.cache_mo  != '' :
		clean_mo_cache(env.cache_mo)
	refresh_cdn()
	wpk_notify(env.deploy_theme_to)

def wpk_notify(deploy_dir):
	if 'notify' in env:
		destinataires = env.notify
		env_run ('mail -s "Deployement sur environnement %s" %s < %s/CHANGELOG.txt || echo "Cant notify"' % ( env.name , destinataires, deploy_dir))




def wpk_fetch_branch(branch='master_maj'):

	env_run ('cd %s && git fetch origin %s:branch' % ( env.deploy_to, branch, branch ) )

def wpk_switch_branch(branch):

	env_run ('cd %s && git checkout %s' % ( env.deploy_to,branch  ) )


def wpk_backup(branch=''):
	if branch == '' :	
		from datetime import datetime
		today  = datetime.today().strftime('%Y_%m_%d')
		branch = 'master_%s' % ( today )
	env_run ('cd %s && git branch %s master' % ( env.deploy_to, branch ) )

def wpk_maj_and_switch_branch(branch='master'):

	env_run ('cd %s && git fetch origin  %s:%s && git checkout %s' % ( env.deploy_to, branch, branch, branch ) )

def wpk_switch_backup(branch=''):
	if branch == '' :	
		from datetime import datetime
		today  = datetime.today().strftime('%Y_%m_%d')
		branch = 'master_%s' % ( today )
	env_run ('cd %s && git checkout %s' % ( env.deploy_to, branch ) )


def rphp(branch=''):
	env_run ('sudo /etc/init.d/php5-fpm restart ')
