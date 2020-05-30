# UCHS
This is the server-side code for our Final Year Design Lab project - Universal Community Helpline Service.

We are using MySQL (via [Cloud SQL](https://cloud.google.com/sql/docs/mysql)) for all our database needs on the server end.

Our client side Android application code is at https://github.com/Scjatto/UCHSClient.

# Server side code

App code is in `/src`

# For local dev testing

1. Setup SQL cloud proxy
    ```
    ./cloud_sql_proxy -instances=INSTANCE_CONNECTION_NAME=tcp:PORT_NO
    ```

    or, if in Windows, run:
    ```
    start_db_proxy.bat
    ```
2. Change  `/src/app.yaml` with relevant port numbers and INSTANCE\_CONNECTION\_NAME
3. Run 
    ```
    python main.py
    ```

# For deployment

1. Navigate to `/src`
    ```
    cd src/
    ```
2. Run:
    ```
    gcloud app deploy
    ```

# For unit-testing

1. Navigate to `/src`
    ```
    cd src/
    ```
2. Run:
    ```
    pytest -v tests
    ```
# Credits
Cheers to Team A.V.A.A.S :sunglasses:!
[**A**ttri][1],
[**V**ishal][2],
[**A**runima][3],
[**A**bhirup][4] and
[**S**oham][5]

Also, thanks to Prof. Eekian Wong, who was very engaging and supportive :fire:.

<!-- Icons -->
[0.1]: http://i.imgur.com/9I6NRUm.png

[1]: https://github.com/attrighosal
[2]: https://github.com/Alyigne
[3]: https://github.com/arunimanandy
[4]: http://github.com/maverickdas
[5]: https://github.com/Scjatto
