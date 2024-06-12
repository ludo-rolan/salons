# Load env 
source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.config.sh"



# create and Load env files from local
$(cp -n ${ROOT_DIR}/.env ${ROOT_DIR}/.env.local)
$(ln -sfn ${ROOT_DIR}/.env ${SCRIPT_DIR}/.env.dev) 
$(ln -sfn ${ROOT_DIR}/.env.local ${SCRIPT_DIR}/.env.local)

if [ -f .env ]
then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi
if [ -f .env.local ]
then
  export $(cat .env.local | sed 's/#.*//g' | xargs)
fi



case "$1" in
    "watch")
        case "$2" in
            "afmm")
                logMsg "Running AFMM sass Watch..."
                sass --watch --no-source-map  "${CODE_DIR}/$STYLESHEET_DIR_AFMM/scss/main.scss:${CODE_DIR}/$STYLESHEET_DIR_AFMM/css/main.min.css" --style compressed
                ;;
            "aftg")
                logMsg "Running AFTG sass Watch..."
                sass --watch --no-source-map  "${CODE_DIR}/$STYLESHEET_DIR_AFTG/scss/main.scss:${CODE_DIR}/$STYLESHEET_DIR_AFTG/css/main.min.css" --style compressed
                ;;
        esac;;
    "build")
        case "$2" in
            "afmm")
                sass --no-source-map  "${CODE_DIR}/$STYLESHEET_DIR_AFMM/scss/main.scss:${CODE_DIR}/$STYLESHEET_DIR_AFMM/css/main.min.css" --style compressed
                logMsg "SCSS build is complete..."
                logMsg "Check the output dir.. ${CODE_DIR}/$STYLESHEET_DIR_AFMM/css/"
                ;;
            "aftg")
                sass --no-source-map  "${CODE_DIR}/$STYLESHEET_DIR_AFTG/scss/main.scss:${CODE_DIR}/$STYLESHEET_DIR_AFTG/css/main.min.css" --style compressed
                logMsg "SCSS build is complete..."
                logMsg "Check the output dir.. ${CODE_DIR}/$STYLESHEET_DIR_AFTG/css/"
                ;;
        esac
esac
