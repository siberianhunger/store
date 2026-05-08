from app.db import get_db


PRODUCTS = [
    ("baikal-shoreline-pebble", "Baikal Shoreline Pebble", "Береговая галька Байкала", "A rounded grey-brown pebble with a quiet matte surface, suited for a desk tray or shelf.", "Округлая серо-коричневая галька с матовой поверхностью. Хорошо смотрится на полке, рабочем столе или в небольшой интерьерной композиции.", 1800, "media/catalog_samples/stone1.png", 4, 124, "Lake Baikal shoreline", "water-smoothed", "grey", 1),
    ("selenga-grey-stone", "Selenga Grey Stone", "Селенгинский серый камень", "Compact grey stone with soft edges and subtle tonal variation from the Selenga delta area.", "Небольшой серый камень с мягкими краями и спокойными переходами тона. Найден в районе дельты Селенги.", 2100, "media/catalog_samples/stone2.png", 3, 148, "Selenga delta, Baikal region", "natural matte", "grey", 1),
    ("olkhon-stripe-stone", "Olkhon Stripe Stone", "Ольхонский камень с полосами", "A narrow decorative stone with layered striping and a clean vertical silhouette.", "Узкий декоративный камень со слоистым рисунком и собранным вертикальным силуэтом.", 2600, "media/catalog_samples/stone3.png", 2, 161, "Olkhon Island area", "water-smoothed", "striped", 1),
    ("listvyanka-smooth-stone", "Listvyanka Smooth Stone", "Гладкий камень из Листвянки", "Balanced oval stone with a smooth hand feel and warm taupe-brown coloring.", "Овальный камень с гладкой фактурой и теплым серо-коричневым оттенком. Лаконичный акцент для спокойного интерьера.", 1900, "media/catalog_samples/stone4.png", 5, 132, "Listvyanka shore", "smooth", "brown", 0),
    ("deep-water-granite", "Deep Water Granite", "Гранит темной воды", "Dense speckled stone with charcoal notes and a naturally weighted feel.", "Плотный камень с природным краплением и угольно-серым тоном. Увесистый, с выразительной минеральной фактурой.", 2900, "media/catalog_samples/stone5.png", 2, 188, "Southern Baikal shore", "natural matte", "dark", 1),
    ("mist-vein-pebble", "Mist Vein Pebble", "Светлая галька с прожилками", "Pale grey pebble marked by soft vein lines, useful as a small decorative accent.", "Светло-серая галька с тонкими мягкими прожилками. Подходит как небольшой спокойный акцент.", 2300, "media/catalog_samples/stone6.png", 3, 139, "Baikal shallows", "water-smoothed", "veined", 0),
    ("siberian-taupe-stone", "Siberian Taupe Stone", "Серо-бежевый сибирский камень", "Warm taupe stone with an even profile and understated surface markings.", "Теплый серо-бежевый камень с ровным профилем и деликатными природными отметинами.", 2000, "media/catalog_samples/stone7.png", 4, 151, "Baikal region", "smooth", "brown", 0),
    ("cedar-shadow-pebble", "Cedar Shadow Pebble", "Темная байкальская галька", "Dark compact pebble with a deep natural tone that pairs well with wood and linen.", "Компактная темная галька глубокого природного оттенка. Хорошо сочетается с деревом, льном и холодной керамикой.", 2400, "media/catalog_samples/stone8.png", 3, 169, "Western Baikal shore", "natural matte", "dark", 0),
    ("angara-river-stone", "Angara River Stone", "Камень у истока Ангары", "Taller stone with an elongated profile and cool grey surface character.", "Вытянутый камень с прохладной серой поверхностью и мягко сглаженным речным силуэтом.", 2200, "media/catalog_samples/stone9.png", 4, 142, "Angara headwaters", "water-smoothed", "grey", 1),
    ("silver-lichen-pebble", "Silver Lichen Pebble", "Серебристая галька", "Light stone with silver-grey movement and soft rounded shoulders.", "Светлый камень с серебристо-серыми переливами и мягкими округлыми краями.", 2500, "media/catalog_samples/stone10.png", 3, 156, "Lake Baikal shoreline", "smooth", "grey", 0),
    ("brown-reed-stone", "Brown Reed Stone", "Теплый тростниковый камень", "Warm brown stone with a slim stance and naturally varied surface color.", "Теплый коричневый камень с тонким силуэтом и живой неоднородной поверхностью.", 1850, "media/catalog_samples/stone11.png", 5, 127, "Reed beds, Baikal shore", "natural matte", "brown", 0),
    ("stormline-baikal-stone", "Stormline Baikal Stone", "Темный штормовой камень", "Strong dark-grey stone with a clean outline and quiet mineral flecks.", "Выразительный темно-серый камень с чистым контуром и спокойными минеральными вкраплениями.", 2750, "media/catalog_samples/stone12.png", 2, 176, "Northern Baikal shore", "water-smoothed", "dark", 1),
    ("birch-bank-pebble", "Birch Bank Pebble", "Светлая береговая галька", "Soft beige-grey pebble with a gentle curve and minimal markings.", "Мягкая бежево-серая галька с плавным изгибом и почти незаметным природным рисунком.", 1950, "media/catalog_samples/stone13.png", 4, 130, "Baikal birch bank", "smooth", "pale", 0),
    ("taiga-vein-stone", "Taiga Vein Stone", "Таежный камень с прожилками", "Veined decorative stone with fine linear detail and a cool neutral base.", "Декоративный камень с тонкими линейными прожилками и прохладной нейтральной основой.", 2650, "media/catalog_samples/stone14.png", 2, 163, "Taiga shore path", "natural matte", "veined", 0),
    ("quiet-bay-pebble", "Quiet Bay Pebble", "Галька тихой бухты", "Small rounded stone with muted brown-grey color and a calm, simple form.", "Небольшая округлая галька приглушенного коричнево-серого оттенка. Простая форма без лишнего визуального шума.", 1750, "media/catalog_samples/stone15.png", 6, 118, "Sheltered Baikal bay", "water-smoothed", "brown", 0),
    ("frost-edge-stone", "Frost Edge Stone", "Камень ледяной кромки", "Cool pale stone with crisp edge detail and soft winter-grey coloring.", "Прохладный светлый камень с четкой кромкой и мягким зимне-серым тоном.", 2550, "media/catalog_samples/stone16.png", 3, 154, "Eastern Baikal shore", "smooth", "pale", 1),
]


def seed_products():
    db = get_db()
    for product in PRODUCTS:
        (
            slug,
            name_en,
            name_ru,
            description_en,
            description_ru,
            price_cents,
            image_path,
            stock,
            weight_grams,
            origin,
            finish,
            color_family,
            is_featured,
        ) = product
        db.execute(
            """
            INSERT INTO products (
                slug, name, name_en, name_ru, description, description_en, description_ru,
                price_cents, image_path, stock,
                weight_grams, origin, finish, color_family, is_featured
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                name = excluded.name,
                name_en = excluded.name_en,
                name_ru = excluded.name_ru,
                description = excluded.description,
                description_en = excluded.description_en,
                description_ru = excluded.description_ru,
                price_cents = excluded.price_cents,
                image_path = excluded.image_path,
                stock = excluded.stock,
                weight_grams = excluded.weight_grams,
                origin = excluded.origin,
                finish = excluded.finish,
                color_family = excluded.color_family,
                is_featured = excluded.is_featured
            """,
            (
                slug,
                name_en,
                name_en,
                name_ru,
                description_en,
                description_en,
                description_ru,
                price_cents,
                image_path,
                stock,
                weight_grams,
                origin,
                finish,
                color_family,
                is_featured,
            ),
        )
    db.commit()
