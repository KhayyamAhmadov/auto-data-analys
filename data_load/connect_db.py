from load_database import DatabaseManager


def get_connection_from_user():
    print("Dəstəklənən DB tipləri: sql server, mysql, postgresql, oracle, sqlite")
    db_type = input("DB tipi: ").strip().lower()

    if db_type == "sqlite":
        database = input("SQLite fayl yolu (məs: data.db): ").strip()
        return DatabaseManager(db_type="sqlite", database=database)

    host = input("Host: ").strip()
    port = input("Port (boş buraxıla bilər): ").strip() or None
    database = input("Database adı: ").strip()

    if db_type == "sql server":
        auth_choice = input("Authentication (sql/windows): ").strip().lower()
        if auth_choice == "windows":
            return DatabaseManager(
                db_type="sql server",
                host=host,
                port=port,
                database=database,
                authentication="windows"
            )
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        return DatabaseManager(
            db_type="sql server",
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            authentication="sql"
        )

    if db_type == "oracle":
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        service_name = input("Service name: ").strip()
        return DatabaseManager(
            db_type="oracle",
            host=host,
            port=port,
            username=username,
            password=password,
            service_name=service_name
        )

    # mysql / postgresql
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    return DatabaseManager(
        db_type=db_type,
        host=host,
        port=port,
        database=database,
        username=username,
        password=password
    )


def main():
    db_manager = get_connection_from_user()

    success, message = db_manager.test_connection()

    if not success:
        print(f"\nQoşulma alınmadı: {message}")
        return

    print("\nQoşulma uğurludur!")

    tables = db_manager.get_tables()

    if not tables:
        print("Bu bazada cədvəl tapılmadı.")
        db_manager.close()
        return

    print("\nMövcud cədvəllər:")
    for i, table in enumerate(tables, start=1):
        print(f"  {i}. {table}")

    choice = input("\nHansı cədvəldən data yükləmək istəyirsən? (nömrə): ").strip()

    try:
        index = int(choice) - 1
        table_name = tables[index]
    except (ValueError, IndexError):
        print("Yanlış seçim.")
        db_manager.close()
        return

    df = db_manager.get_table_data(table_name)

    print(f"\n'{table_name}' cədvəlindən {len(df)} sətir yükləndi.")
    print(df.head())

    db_manager.close()


if __name__ == "__main__":
    main()