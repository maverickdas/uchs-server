# UCHS
This is the repository for our Final Year Design Lab project - Universal Community Helpline Service

# Server side code

App code is in `/src`

# For local dev testing

1. Setup SQL cloud proxy
    ```
    ./cloud_sql_proxy -instances=INSTANCE_CONNECTION_NAME=tcp:PORT_NO
    ```
2. Change  `/src/app.yaml` with relevant port numbers and INSTANCE\_CONNECTION\_NAME
3. Run 
    ```
    python main.py
    ```

# To deploy

1. Navigate to `/src`
    ```
    cd src/
    ```
2. Run:
    ```
    gcloud app deploy
    ```
