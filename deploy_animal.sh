export all_proxy="http://127.0.0.1:7890"
export ngrok=True
export MIDJOURNEY_TOKEN=7ab0c4ac-4be4-419d-8656-ddb251383e17

echo $MIDJOURNEY_TOKEN
ngrok config add-authtoken 2X9jVaDoicYCGJD9kZB9iWPT1iw_rKx37a8pBqXPbj7EcTWy
nohup yival run demo/configs/animal_story.yml > animal_out&