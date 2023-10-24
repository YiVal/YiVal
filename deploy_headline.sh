export all_proxy="http://127.0.0.1:7890"
export ngrok=True
ngrok config add-authtoken 2X9kfOcpqusXG9ZmjaxmvkFD9WU_7UyCY6nY3uETkAWSnEfh5
nohup poetry run yival run /root/code/YiVal/demo/configs/headline_generation_improve.yml > out&