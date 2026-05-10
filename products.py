PRODUCTS = {
    "vape_1": {
        "id": "vape_1",
        "category": "vapes",
        "name": "Lost Mary BM600 — Watermelon Ice",
        "description": "600 puffs · 20mg nicotine · 2ml · Draw-activated",
        "price": 150,
        "photo": "https://i.imgur.com/placeholder1.jpg",
    },
    "vape_2": {
        "id": "vape_2",
        "category": "vapes",
        "name": "Elf Bar 600 — Blueberry Sour Raspberry",
        "description": "600 puffs · 20mg nicotine · 2ml · Pre-filled",
        "price": 140,
        "photo": "https://i.imgur.com/placeholder2.jpg",
    },
    "vape_3": {
        "id": "vape_3",
        "category": "vapes",
        "name": "SKE Crystal Bar — Cola Ice",
        "description": "600 puffs · 20mg nicotine · Mesh coil",
        "price": 145,
        "photo": "https://i.imgur.com/placeholder3.jpg",
    },
    "snus_1": {
        "id": "snus_1",
        "category": "snus",
        "name": "Zyn Cool Mint — Strong (9mg)",
        "description": "20 pouches · 9mg/pouch · Tobacco-free · Slim format",
        "price": 200,
        "photo": "https://i.imgur.com/placeholder4.jpg",
    },
    "snus_2": {
        "id": "snus_2",
        "category": "snus",
        "name": "VELO Freeze X-Strong",
        "description": "20 pouches · 11mg/pouch · Intense cooling sensation",
        "price": 210,
        "photo": "https://i.imgur.com/placeholder5.jpg",
    },
    "snus_3": {
        "id": "snus_3",
        "category": "snus",
        "name": "On! Citrus — Regular (4mg)",
        "description": "20 mini pouches · 4mg/pouch · Discreet & dry",
        "price": 180,
        "photo": "https://i.imgur.com/placeholder6.jpg",
    },
}

CATEGORIES = {
    "vapes": "💨 Одноразовые вейпы",
    "snus":  "🟢 Никотиновые паучи",
}

def get_by_category(category: str) -> list:
    return [p for p in PRODUCTS.values() if p["category"] == category]

def get_product(product_id: str) -> dict | None:
    return PRODUCTS.get(product_id)
