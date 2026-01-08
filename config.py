import os
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "gateway01.eu-central-1.prod.aws.tidbcloud.com"),
    "user": os.environ.get("DB_USER", "4VwoLkw238RMNqP.root"),
    "password": os.environ.get("DB_PASSWORD", "6D9izpwaUWPYTfMn"),
    "database": os.environ.get("DB_NAME", "ola_ride_insights"),
    "port": int(os.environ.get("DB_PORT", 4000))
}