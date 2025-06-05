from airflow.hooks.base import BaseHook

conn = BaseHook.get_connection('minio_conn')
print("Проверяем параметры подключения:")
print(f"Extra: {conn.extra_dejson}")
print(f"Login (должен быть пустым): {conn.login}")
print(f"Password (должен быть пустым): {conn.password}")