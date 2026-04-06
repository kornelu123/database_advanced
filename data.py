import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:@localhost/postgres")


VOIVODESHIPS = [
    "Dolnośląskie", "Kujawsko-pomorskie", "Lubelskie", "Lubuskie",
    "Łódzkie", "Małopolskie", "Mazowieckie", "Opolskie", "Podkarpackie",
    "Podlaskie", "Pomorskie", "Śląskie", "Świętokrzyskie", "Warmińsko-mazurskie",
    "Wielkopolskie", "Zachodniopomorskie"
]

CATEGORIES = [
    ("Elektronika", "laptop", "Sprzęt elektroniczny, komputery, telefony, RTV, AGD"),
    ("Ubrania", "tshirt", "Odzież męska, damska, dziecięca, dodatki"),
    ("Książki", "book", "Książki, podręczniki, komiksy, czasopisma"),
    ("Meble", "couch", "Meble domowe, biurowe, wyposażenie wnętrz"),
    ("Sport", "bicycle", "Sprzęt sportowy, rowery, akcesoria fitness"),
    ("Zwierzęta", "paw", "Artykuły dla zwierząt, akcesoria, karma"),
    ("Dzieci", "baby", "Zabawki, artykuły dziecięce, wózki, ubranka"),
    ("Motoryzacja", "car", "Części samochodowe, akcesoria, opony"),
    ("Nieruchomości", "building", "Mieszkania, domy, pokoje, biura"),
    ("Praca", "briefcase", "Oferty pracy, ogłoszenia pracowników"),
    ("Usługi", "tools", "Usługi remontowe, korepetycje, kosmetyka")
]

CITIES = [
    ("Wrocław", "Dolnośląskie", "50"), ("Wałbrzych", "Dolnośląskie", "58"),
    ("Legnica", "Dolnośląskie", "59"), ("Jelenia Góra", "Dolnośląskie", "58"),
    ("Lubin", "Dolnośląskie", "59"), ("Głogów", "Dolnośląskie", "67"),
    ("Bydgoszcz", "Kujawsko-pomorskie", "85"), ("Toruń", "Kujawsko-pomorskie", "87"),
    ("Włocławek", "Kujawsko-pomorskie", "87"), ("Grudziądz", "Kujawsko-pomorskie", "86"),
    ("Inowrocław", "Kujawsko-pomorskie", "88"),
    ("Lublin", "Lubelskie", "20"), ("Chełm", "Lubelskie", "22"),
    ("Zamość", "Lubelskie", "22"), ("Biała Podlaska", "Lubelskie", "21"),
    ("Puławy", "Lubelskie", "24"),
    ("Zielona Góra", "Lubuskie", "65"), ("Gorzów Wielkopolski", "Lubuskie", "66"),
    ("Nowa Sól", "Lubuskie", "67"), ("Żary", "Lubuskie", "68"),
    ("Łódź", "Łódzkie", "90"), ("Piotrków Trybunalski", "Łódzkie", "97"),
    ("Pabianice", "Łódzkie", "95"), ("Zgierz", "Łódzkie", "95"),
    ("Skierniewice", "Łódzkie", "96"),
    ("Kraków", "Małopolskie", "30"), ("Tarnów", "Małopolskie", "33"),
    ("Nowy Sącz", "Małopolskie", "33"), ("Oświęcim", "Małopolskie", "32"),
    ("Zakopane", "Małopolskie", "34"),
    ("Warszawa", "Mazowieckie", "00"), ("Radom", "Mazowieckie", "26"),
    ("Płock", "Mazowieckie", "09"), ("Siedlce", "Mazowieckie", "08"),
    ("Ostrołęka", "Mazowieckie", "07"),
    ("Opole", "Opolskie", "45"), ("Kędzierzyn-Koźle", "Opolskie", "47"),
    ("Brzeg", "Opolskie", "49"), ("Nysa", "Opolskie", "48"),
    ("Rzeszów", "Podkarpackie", "35"), ("Przemyśl", "Podkarpackie", "37"),
    ("Stalowa Wola", "Podkarpackie", "37"), ("Mielec", "Podkarpackie", "39"),
    ("Tarnobrzeg", "Podkarpackie", "39"),
    ("Białystok", "Podlaskie", "15"), ("Łomża", "Podlaskie", "18"),
    ("Suwałki", "Podlaskie", "16"), ("Augustów", "Podlaskie", "16"),
    ("Gdańsk", "Pomorskie", "80"), ("Gdynia", "Pomorskie", "81"),
    ("Słupsk", "Pomorskie", "76"), ("Tczew", "Pomorskie", "83"),
    ("Wejherowo", "Pomorskie", "84"),
    ("Katowice", "Śląskie", "40"), ("Częstochowa", "Śląskie", "42"),
    ("Gliwice", "Śląskie", "44"), ("Zabrze", "Śląskie", "41"),
    ("Bielsko-Biała", "Śląskie", "43"), ("Rybnik", "Śląskie", "44"),
    ("Kielce", "Świętokrzyskie", "25"), ("Ostrowiec Świętokrzyski", "Świętokrzyskie", "27"),
    ("Starachowice", "Świętokrzyskie", "27"), ("Skarżysko-Kamienna", "Świętokrzyskie", "26"),
    ("Olsztyn", "Warmińsko-mazurskie", "10"), ("Elbląg", "Warmińsko-mazurskie", "82"),
    ("Ełk", "Warmińsko-mazurskie", "19"), ("Giżycko", "Warmińsko-mazurskie", "11"),
    ("Poznań", "Wielkopolskie", "60"), ("Kalisz", "Wielkopolskie", "62"),
    ("Konin", "Wielkopolskie", "62"), ("Piła", "Wielkopolskie", "64"),
    ("Leszno", "Wielkopolskie", "64"),
    ("Szczecin", "Zachodniopomorskie", "70"), ("Koszalin", "Zachodniopomorskie", "75"),
    ("Stargard", "Zachodniopomorskie", "73"), ("Świnoujście", "Zachodniopomorskie", "72")
]

TEST_USER = {
    "username": "demo",
    "display_name": "Użytkownik Demo",
    "email": "demo@example.com",
    "password": "demo123",
    "phone": "123456789",
    "city": "Warszawa"
}

SAMPLE_ITEMS = [
    {
        "title": "Laptop Lenovo ThinkPad",
        "description": "Używany, ale w bardzo dobrym stanie. 16GB RAM, 512GB SSD.",
        "condition": "bardzo dobry",
        "quantity": 1,
        "city_name": "Warszawa",
        "category_names": ["Elektronika"]
    },
    {
        "title": "Rower górski Kross",
        "description": "Rower używany sezon, rama 19 cali, przerzutki Shimano.",
        "condition": "dobry",
        "quantity": 1,
        "city_name": "Kraków",
        "category_names": ["Sport"]
    },
    {
        "title": "Komplet mebli do pokoju",
        "description": "Łóżko, szafa, biurko. Stan idealny.",
        "condition": "bardzo dobry",
        "quantity": 1,
        "city_name": "Wrocław",
        "category_names": ["Meble"]
    }
]


async def insert_voivodeships(conn):
    for name in VOIVODESHIPS:
        await conn.execute(
            "INSERT INTO voivodeships (name) VALUES ($1) ON CONFLICT (name) DO NOTHING",
            name
        )

async def insert_categories(conn):
    for name, icon, desc in CATEGORIES:
        await conn.execute(
            "INSERT INTO categories (name, icon_name, description) VALUES ($1, $2, $3) ON CONFLICT (name) DO NOTHING",
            name, icon, desc
        )

async def insert_cities(conn):
    voiv_map = {}
    rows = await conn.fetch("SELECT id, name FROM voivodeships")
    for row in rows:
        voiv_map[row["name"]] = row["id"]

    count = 0
    for city_name, voiv_name, prefix in CITIES:
        voiv_id = voiv_map.get(voiv_name)
        if voiv_id:
            await conn.execute(
                "INSERT INTO cities (voivodeship_id, name, postal_code_prefix) VALUES ($1, $2, $3) ON CONFLICT (voivodeship_id, name) DO NOTHING",
                voiv_id, city_name, prefix
            )
            count += 1

async def insert_test_user(conn):
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
    hashed = pwd_context.hash(TEST_USER["password"])
    await conn.execute(
        """
        INSERT INTO users (username, display_name, email, password_hash, phone, city)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (username) DO NOTHING
        """,
        TEST_USER["username"], TEST_USER["display_name"], TEST_USER["email"],
        hashed, TEST_USER["phone"], TEST_USER["city"]
    )

async def insert_sample_items(conn):
    user_row = await conn.fetchrow("SELECT id FROM users WHERE username = $1", "demo")
    if not user_row:
        return
    user_id = user_row["id"]

    cat_rows = await conn.fetch("SELECT id, name FROM categories")
    cat_map = {r["name"]: r["id"] for r in cat_rows}

    for item in SAMPLE_ITEMS:
        city_row = await conn.fetchrow("SELECT id FROM cities WHERE name = $1", item["city_name"])
        if not city_row:
            continue
        city_id = city_row["id"]

        item_row = await conn.fetchrow(
            """
            INSERT INTO items (user_id, title, description, condition, quantity, city_id, status)
            VALUES ($1, $2, $3, $4, $5, $6, 'active')
            RETURNING id
            """,
            user_id, item["title"], item["description"], item["condition"],
            item["quantity"], city_id
        )
        item_id = item_row["id"]

        for cat_name in item["category_names"]:
            cat_id = cat_map.get(cat_name)
            if cat_id:
                await conn.execute(
                    "INSERT INTO item_categories (item_id, category_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                    item_id, cat_id
                )

async def seed():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await insert_voivodeships(conn)
        await insert_categories(conn)
        await insert_cities(conn)
        await insert_test_user(conn)
        await insert_sample_items(conn)
    except Exception as e:
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed())
