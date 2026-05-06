from app.db import get_db


PRODUCTS = [
    ("baikal-shoreline-pebble", "Baikal Shoreline Pebble", "Байкальская береговая галька", "A rounded grey-brown pebble with a quiet matte surface, suited for a desk tray or shelf.", "Округлая серо-коричневая галька с матовой поверхностью для полки, рабочего стола или небольшой композиции.", 1800, "media/catalog_samples/stone1.png", 4, 124, "Lake Baikal shoreline", "water-smoothed", "grey", 1),
    ("selenga-grey-stone", "Selenga Grey Stone", "Серый камень Селенги", "Compact grey stone with soft edges and subtle tonal variation from the Selenga delta area.", "Компактный серый камень с мягкими краями и спокойными переходами оттенка из района дельты Селенги.", 2100, "media/catalog_samples/stone2.png", 3, 148, "Selenga delta, Baikal region", "natural matte", "grey", 1),
    ("olkhon-stripe-stone", "Olkhon Stripe Stone", "Полосатый камень Ольхона", "A narrow decorative stone with layered striping and a clean vertical silhouette.", "Узкий декоративный камень со слоистыми полосами и аккуратным вертикальным силуэтом.", 2600, "media/catalog_samples/stone3.png", 2, 161, "Olkhon Island area", "water-smoothed", "striped", 1),
    ("listvyanka-smooth-stone", "Listvyanka Smooth Stone", "Гладкий камень Листвянки", "Balanced oval stone with a smooth hand feel and warm taupe-brown coloring.", "Сбалансированный овальный камень с гладкой фактурой и теплым серо-коричневым оттенком.", 1900, "media/catalog_samples/stone4.png", 5, 132, "Listvyanka shore", "smooth", "brown", 0),
    ("deep-water-granite", "Deep Water Granite", "Гранит глубокой воды", "Dense speckled stone with charcoal notes and a naturally weighted feel.", "Плотный камень с краплением, угольными нотами цвета и ощутимой природной тяжестью.", 2900, "media/catalog_samples/stone5.png", 2, 188, "Southern Baikal shore", "natural matte", "dark", 1),
    ("mist-vein-pebble", "Mist Vein Pebble", "Галька с туманными прожилками", "Pale grey pebble marked by soft vein lines, useful as a small decorative accent.", "Светло-серая галька с мягкими линиями прожилок для спокойного декоративного акцента.", 2300, "media/catalog_samples/stone6.png", 3, 139, "Baikal shallows", "water-smoothed", "veined", 0),
    ("siberian-taupe-stone", "Siberian Taupe Stone", "Сибирский тауповый камень", "Warm taupe stone with an even profile and understated surface markings.", "Теплый серо-бежевый камень с ровным профилем и сдержанными природными отметинами.", 2000, "media/catalog_samples/stone7.png", 4, 151, "Baikal region", "smooth", "brown", 0),
    ("cedar-shadow-pebble", "Cedar Shadow Pebble", "Галька кедровой тени", "Dark compact pebble with a deep natural tone that pairs well with wood and linen.", "Темная компактная галька глубокого природного оттенка, хорошо сочетается с деревом и льном.", 2400, "media/catalog_samples/stone8.png", 3, 169, "Western Baikal shore", "natural matte", "dark", 0),
    ("angara-river-stone", "Angara River Stone", "Камень истока Ангары", "Taller stone with an elongated profile and cool grey surface character.", "Вытянутый камень с прохладной серой поверхностью и спокойным речным характером.", 2200, "media/catalog_samples/stone9.png", 4, 142, "Angara headwaters", "water-smoothed", "grey", 1),
    ("silver-lichen-pebble", "Silver Lichen Pebble", "Галька серебристого лишайника", "Light stone with silver-grey movement and soft rounded shoulders.", "Светлый камень с серебристо-серыми переходами и мягкими округлыми краями.", 2500, "media/catalog_samples/stone10.png", 3, 156, "Lake Baikal shoreline", "smooth", "grey", 0),
    ("brown-reed-stone", "Brown Reed Stone", "Камень бурого тростника", "Warm brown stone with a slim stance and naturally varied surface color.", "Теплый коричневый камень с тонким силуэтом и естественно неоднородной поверхностью.", 1850, "media/catalog_samples/stone11.png", 5, 127, "Reed beds, Baikal shore", "natural matte", "brown", 0),
    ("stormline-baikal-stone", "Stormline Baikal Stone", "Байкальский штормовой камень", "Strong dark-grey stone with a clean outline and quiet mineral flecks.", "Выразительный темно-серый камень с чистым контуром и спокойными минеральными вкраплениями.", 2750, "media/catalog_samples/stone12.png", 2, 176, "Northern Baikal shore", "water-smoothed", "dark", 1),
    ("birch-bank-pebble", "Birch Bank Pebble", "Галька березового берега", "Soft beige-grey pebble with a gentle curve and minimal markings.", "Мягкая бежево-серая галька с плавным изгибом и минимальными природными отметинами.", 1950, "media/catalog_samples/stone13.png", 4, 130, "Baikal birch bank", "smooth", "pale", 0),
    ("taiga-vein-stone", "Taiga Vein Stone", "Таежный камень с прожилками", "Veined decorative stone with fine linear detail and a cool neutral base.", "Декоративный камень с тонкими прожилками и прохладной нейтральной основой.", 2650, "media/catalog_samples/stone14.png", 2, 163, "Taiga shore path", "natural matte", "veined", 0),
    ("quiet-bay-pebble", "Quiet Bay Pebble", "Галька тихой бухты", "Small rounded stone with muted brown-grey color and a calm, simple form.", "Небольшая округлая галька приглушенного коричнево-серого цвета и простой спокойной формы.", 1750, "media/catalog_samples/stone15.png", 6, 118, "Sheltered Baikal bay", "water-smoothed", "brown", 0),
    ("frost-edge-stone", "Frost Edge Stone", "Камень морозной кромки", "Cool pale stone with crisp edge detail and soft winter-grey coloring.", "Прохладный светлый камень с четкой кромкой и мягким зимне-серым оттенком.", 2550, "media/catalog_samples/stone16.png", 3, 154, "Eastern Baikal shore", "smooth", "pale", 1),
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
