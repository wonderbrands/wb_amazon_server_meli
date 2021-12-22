while true
do
    python /home/ubuntu/meli/get_access_token_meli_oficiales.py
    sleep  21600
    echo  $(date +%Y-%m-%d) $(date +%T)"|Se ha recuperado access_token_oficiales de Meli" >> /home/ubuntu/meli/meli_token_oficiales.log
done

