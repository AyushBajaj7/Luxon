import random
import urllib.parse
from app import create_app, db
from app.models import Category, Subcategory, Product, User
from werkzeug.security import generate_password_hash

app = create_app()

CLOUDINARY_URLS = {
    "apple_watch": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771409/xndnasr1pnlzhc1evawx.jpg",
    "baccarat_vase": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771410/vpzbqvadmkbjjeike6bg.jpg",
    "balenciaga_hoodie": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771410/niydydlqnphl5c2ko6jw.jpg",
    "cartier_tank": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771411/if1zmafxldxckhdwfdjk.jpg",
    "chanel_flap_bag": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771412/ajc31kzfetuktbqy5z1f.jpg",
    "creed_aventus": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771413/ucn3gezraiqmobisqw1k.jpg",
    "gucci_sneakers": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771414/iccavdlxttqx6ceuzsnp.jpg",
    "hermes_birkin": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771415/z7jyyut5lzzgox2lgt7u.jpg",
    "iphone_15_pro": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771416/mmuhiokfyzfztmtewpjl.jpg",
    "louboutin_pumps": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771417/pvr6gfmagngnuowggdrr.jpg",
    "louis_vuitton_bag": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771418/anfvlqmnv7rnrzqvdffj.jpg",
    "macbook_pro": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771419/jkuhni1aleri0ktin6ra.jpg",
    "omega_speedmaster": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771420/vtqwlpti8rg2ddphylsp.jpg",
    "rolex_submariner": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771421/m5b3cyvuccfgvilanfoe.jpg",
    "samsung_s24": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771422/uavk17h1bevurim6johd.jpg",
    "sony_headphones": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771423/guaov2imc7s4rc8a98ux.jpg",
    "tom_ford_suit": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780771424/co0bjmmhriasnwdgjhie.jpg",
    "s26_ultra_dragon": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780812540/luxon_products/cgrw4yxxjp46frsqys2i.jpg",
    "s26_ultra_dragon_2": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780812793/luxon_products/ybho8zp2sgcw9smpd3ug.jpg",
    "iphone_17_titanium": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780812543/luxon_products/nle06mxnv7itssbkqge8.jpg",
    "rog_zephyrus": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780812545/luxon_products/kblr0svku26pdaskjibv.jpg",
    "razer_blade": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780812546/luxon_products/v7jboed9xva5yqm0kds4.jpg",
    "beolab_90": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780812547/luxon_products/uadd6opa8f606gbyzmdk.jpg",
    "sennheiser_he1": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780812549/luxon_products/sjwtyi0wh7266ezxzloz.jpg",
    "tag_heuer_e4": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780812550/luxon_products/bu8209kv7vh1xch7k6ub.jpg",
    "hublot_big_bang": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780812551/luxon_products/b6v3cvexsw3o4iwn9ize.jpg",
    "vertu_signature": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815467/luxon_products/p9xvyvv6pa2xhvp2jjg8.jpg",
    "montblanc_summit": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815468/luxon_products/ytxttky6naqjm5s82f5q.jpg",
    "patek_nautilus": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815469/luxon_products/f6lg1uvzkzowfjepjl2z.jpg",
    "ap_royal_oak": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815470/luxon_products/nnhdf9j96xc9u9kicuqm.jpg",
    "richard_mille": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815471/luxon_products/yciovgpovfbz0360i7rd.jpg",
    "vacheron_overseas": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815471/luxon_products/auetuarhgrtdz00lv53c.jpg",
    "hermes_kelly": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815472/luxon_products/kpctwcjem5hv8tbcetsk.jpg",
    "dior_lady": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815473/luxon_products/xzqstzlocwgmuiylalqs.jpg",
    "bottega_cassette": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815474/luxon_products/qrchv0kexv8sdsjxoi6m.jpg",
    "fendi_peekaboo": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815474/luxon_products/ttwvbr1rm4zsu4sixx2a.jpg",
    "goyard_st_louis": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815475/luxon_products/rb08e2jqyy7mfakv3wjy.jpg",
    "prada_galleria": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815476/luxon_products/vomqnono83ewpb6pvvw5.jpg",
    "rolex_daytona_plat": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815477/luxon_products/e8nqkelopljqcaxpq3xs.jpg",
    "jlc_reverso": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815478/luxon_products/cdlnqegm209tuxgbe6oq.jpg",
    "lange_1": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815478/luxon_products/qgzviuwtgg7othcmnyjb.jpg",
    "john_lobb_oxfords": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780815480/luxon_products/pghwerbmwnqaqu8ayo79.jpg",
    "celine_triomphe": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780816034/luxon_products/fz0kozhmr2pxyigstn0b.jpg",
    "loro_piana_coat": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780816036/luxon_products/cj8pwhgh2ajhxasjvoyo.jpg",
    "brunello_sweater": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780816037/luxon_products/raavz7ha7dowuomhwkwb.jpg",
    "kiton_suit": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780816037/luxon_products/lko4axlps38qpahmrpcb.jpg",
    "brioni_jacket": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780816038/luxon_products/d2pzx9j6ahaflmdg0on4.jpg",
    "gucci_cardigan": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780816040/luxon_products/swt57c7icdwopiwuboqg.jpg",
    "balenciaga_shirt": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780816423/luxon_products/jdi1icg3kjwidp3yd2ds.jpg",
    "burberry_trench": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780816424/luxon_products/yndbyopx5i6qryixdakg.jpg",
    "berluti_shoes": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780816425/luxon_products/gidj6yjwwgwyfoceiinm.jpg",
    "manolo_pumps": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780816426/luxon_products/vjitdbhepynvohknua9a.jpg",
    "jimmy_choo_mule": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780816427/luxon_products/udavr0tmoaxjnjgj6jsu.jpg",
    "hermes_sandals": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780816428/luxon_products/bbj55ikbomngqzqozjpd.jpg"
}

import json

CATEGORIES = [
    {"name": "Fashion", "subs": ["Watches", "Bags", "Clothing", "Shoes"]},
    {"name": "Premium Tech", "subs": ["Smartphones", "Laptops", "Audio", "Smartwatches"]},
    {"name": "Lifestyle", "subs": ["Home Decor", "Fragrances", "Accessories", "Art"]}
]

PRODUCTS_DATA = json.loads('''[
    {
        "name": "Rolex Submariner Date 41mm",
        "brand": "Rolex",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Watches",
        "price": 850000,
        "img_key": "rolex_submariner",
        "desc": "The quintessential divers' watch. Features a unidirectional rotatable bezel and solid-link Oyster bracelet.",
        "featured": true,
        "is_cloudinary": true
    },
    {
        "name": "Omega Speedmaster Moonwatch",
        "brand": "Omega",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Watches",
        "price": 450000,
        "img_key": "omega_speedmaster",
        "desc": "The iconic chronograph that went to the moon. Master Chronometer certified.",
        "featured": false,
        "is_cloudinary": true
    },
    {
        "name": "Cartier Tank Must",
        "brand": "Cartier",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Watches",
        "price": 280000,
        "img_key": "cartier_tank",
        "desc": "A timeless classic with a leather strap and signature Roman numerals.",
        "featured": true,
        "is_cloudinary": true
    },
    {
        "name": "Louis Vuitton Neverfull MM",
        "brand": "Louis Vuitton",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 145000,
        "img_key": "louis_vuitton_bag",
        "desc": "Spacious and elegant, crafted in classic Monogram canvas.",
        "featured": true,
        "is_cloudinary": true
    },
    {
        "name": "Chanel Classic Flap Bag",
        "brand": "Chanel",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 485000,
        "img_key": "chanel_flap_bag",
        "desc": "The iconic quilted leather bag with CC turn-lock and chain strap.",
        "featured": true,
        "is_cloudinary": true
    },
    {
        "name": "Hermes Birkin 35 Togo",
        "brand": "Hermes",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 850000,
        "img_key": "hermes_birkin",
        "desc": "The highly coveted Birkin 35 in gold Togo leather.",
        "featured": true,
        "is_cloudinary": true
    },
    {
        "name": "Balenciaga Oversized Hoodie",
        "brand": "Balenciaga",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Clothing",
        "price": 65000,
        "img_key": "balenciaga_hoodie",
        "desc": "Premium cotton hoodie with signature oversized fit and embroidered logo.",
        "featured": false,
        "is_cloudinary": true
    },
    {
        "name": "Tom Ford Slim Fit Wool Suit",
        "brand": "Tom Ford",
        "cat": "Fashion",
        "gender": "Men",
        "sub": "Clothing",
        "price": 285000,
        "img_key": "tom_ford_suit",
        "desc": "Impeccably tailored two-piece suit in premium Italian wool.",
        "featured": false,
        "is_cloudinary": true
    },
    {
        "name": "Christian Louboutin So Kate Pumps",
        "brand": "Christian Louboutin",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Shoes",
        "price": 75000,
        "img_key": "louboutin_pumps",
        "desc": "Iconic stiletto pumps in patent leather with signature red sole.",
        "featured": true,
        "is_cloudinary": true
    },
    {
        "name": "Gucci Ace Leather Sneakers",
        "brand": "Gucci",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Shoes",
        "price": 62000,
        "img_key": "gucci_sneakers",
        "desc": "Classic low-top leather sneaker with signature Web stripe.",
        "featured": false,
        "is_cloudinary": true
    },
    {
        "name": "Caviar iPhone 17 Pro Max Pure Gold",
        "brand": "Caviar",
        "cat": "Premium Tech",
        "sub": "Smartphones",
        "price": 2500000,
        "img_key": "iphone_15_pro",
        "desc": "18-karat solid gold chassis with intricate engravings.",
        "featured": true,
        "is_cloudinary": true
    },
    {
        "name": "Samsung Galaxy S26 Ultra 1TB",
        "brand": "Samsung",
        "cat": "Premium Tech",
        "sub": "Smartphones",
        "price": 159999,
        "img_key": "samsung_s24",
        "desc": "The ultimate Android experience with Quantum AI and titanium build.",
        "featured": false,
        "is_cloudinary": true
    },
    {
        "name": "MacBook Pro 16 M5 Ultra",
        "brand": "Apple",
        "cat": "Premium Tech",
        "sub": "Laptops",
        "price": 449900,
        "img_key": "macbook_pro",
        "desc": "Unprecedented power with the M5 Ultra chip. 128GB Unified Memory.",
        "featured": true,
        "is_cloudinary": true
    },
    {
        "name": "Sony WH-1000XM6 Wireless",
        "brand": "Sony",
        "cat": "Premium Tech",
        "sub": "Audio",
        "price": 34990,
        "img_key": "sony_headphones",
        "desc": "Next-generation spatial audio and noise cancellation.",
        "featured": false,
        "is_cloudinary": true
    },
    {
        "name": "Apple Watch Ultra 3",
        "brand": "Apple",
        "cat": "Premium Tech",
        "sub": "Smartwatches",
        "price": 89900,
        "img_key": "apple_watch",
        "desc": "The most rugged and capable Apple Watch. Aerospace-grade titanium.",
        "featured": false,
        "is_cloudinary": true
    },
    {
        "name": "Baccarat Harmonie Crystal Vase",
        "brand": "Baccarat",
        "cat": "Lifestyle",
        "sub": "Home Decor",
        "price": 45000,
        "img_key": "baccarat_vase",
        "desc": "Exquisite crystal vase with sweeping vertical lines. Made in France.",
        "featured": false,
        "is_cloudinary": true
    },
    {
        "name": "Creed Aventus Eau de Parfum 100ml",
        "brand": "Creed",
        "cat": "Lifestyle",
        "sub": "Fragrances",
        "price": 35000,
        "img_key": "creed_aventus",
        "desc": "A sophisticated blend for individuals who savor a life well-lived.",
        "featured": true,
        "is_cloudinary": true
    },
    {
        "name": "Caviar Samsung S26 Ultra Golden Dragon",
        "brand": "Caviar",
        "cat": "Premium Tech",
        "sub": "Smartphones",
        "price": 1800000,
        "img_key": "s26_ultra_dragon",
        "is_cloudinary": true,
        "desc": "Custom Samsung S26 Ultra featuring 24K gold bas-relief of a dragon and rubies."
    },
    {
        "name": "Caviar Samsung S26 Ultra Golden Dragon (Edition II)",
        "brand": "Caviar",
        "cat": "Premium Tech",
        "sub": "Smartphones",
        "price": 1850000,
        "img_key": "s26_ultra_dragon_2",
        "is_cloudinary": true,
        "desc": "Second exclusive edition of the Samsung S26 Ultra featuring a distinct 24K gold bas-relief of a dragon."
    },
    {
        "name": "Vertu Signature Touch",
        "brand": "Vertu",
        "cat": "Premium Tech",
        "sub": "Smartphones",
        "price": 950000,        "img_key": "vertu_signature",
        "is_cloudinary": true,

        "desc": "Handcrafted in England with calf leather, ruby button, and titanium frame."
    },
    {
        "name": "Apple iPhone 17 Pro Max 1TB Titanium",
        "brand": "Apple",
        "cat": "Premium Tech",
        "sub": "Smartphones",
        "price": 199900,
        "img_key": "iphone_17_titanium",
        "is_cloudinary": true,
        "desc": "Aero-grade titanium, 1TB storage, revolutionary Quantum camera system."
    },
    {
        "name": "Asus ROG Zephyrus G16 (2026)",
        "brand": "Asus",
        "cat": "Premium Tech",
        "sub": "Laptops",
        "price": 289000,
        "img_key": "rog_zephyrus",
        "is_cloudinary": true,
        "desc": "OLED display, RTX 5090, liquid metal cooling in a CNC-milled chassis."
    },
    {
        "name": "Razer Blade 18 (2026)",
        "brand": "Razer",
        "cat": "Premium Tech",
        "sub": "Laptops",
        "price": 399000,
        "img_key": "razer_blade",
        "is_cloudinary": true,
        "desc": "The ultimate desktop replacement with Mini-LED and ultra-thin design."
    },
    {
        "name": "Bang & Olufsen Beolab 90",
        "brand": "Bang & Olufsen",
        "cat": "Premium Tech",
        "sub": "Audio",
        "price": 7500000,
        "img_key": "beolab_90",
        "is_cloudinary": true,
        "desc": "The ultimate home speaker with incredible power and acoustic lens technology."
    },
    {
        "name": "Focal Grande Utopia EM Evo",
        "brand": "Focal",
        "cat": "Premium Tech",
        "sub": "Audio",
        "price": 15000000,
        "desc": "Reference high-fidelity loudspeakers. Handcrafted in France.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826738/luxon_products/qpxmidk2qxmbjempv5oa.png",
        "is_cloudinary": true
    },
    {
        "name": "Sennheiser HE 1",
        "brand": "Sennheiser",
        "cat": "Premium Tech",
        "sub": "Audio",
        "price": 4500000,
        "img_key": "sennheiser_he1",
        "is_cloudinary": true,
        "desc": "The world's most expensive headphones. Electrostatic driver with tube amplifier base."
    },
    {
        "name": "Devialet Phantom I 108 dB",
        "brand": "Devialet",
        "cat": "Premium Tech",
        "sub": "Audio",
        "price": 289000,
        "desc": "Implosive sound center. 14k gold-leaf side plates.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826739/luxon_products/rbmm56rsb0jueam4ahxt.png",
        "is_cloudinary": true
    },
    {
        "name": "Tag Heuer Connected Calibre E4",
        "brand": "Tag Heuer",
        "cat": "Premium Tech",
        "sub": "Smartwatches",
        "price": 145000,
        "img_key": "tag_heuer_e4",
        "is_cloudinary": true,
        "desc": "Luxury smartwatch combining watchmaking elegance with cutting-edge tech."
    },
    {
        "name": "Hublot Big Bang e Gen 3",
        "brand": "Hublot",
        "cat": "Premium Tech",
        "sub": "Smartwatches",
        "price": 485000,
        "img_key": "hublot_big_bang",
        "is_cloudinary": true,
        "desc": "Black ceramic case smartwatch featuring Wear OS and Hublot's signature design."
    },
    {
        "name": "Montblanc Summit 3",
        "brand": "Montblanc",
        "cat": "Premium Tech",
        "sub": "Smartwatches",
        "price": 110000,        "img_key": "montblanc_summit",
        "is_cloudinary": true,

        "desc": "Titanium case with hand-crafted leather strap. The height of Swiss luxury tech."
    },
    {
        "name": "Patek Philippe Nautilus 5711/1A",
        "brand": "Patek Philippe",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Watches",
        "price": 9500000,        "img_key": "patek_nautilus",
        "is_cloudinary": true,

        "desc": "The most sought-after steel sports watch in the world. Blue dial."
    },
    {
        "name": "Audemars Piguet Royal Oak Jumbo",
        "brand": "Audemars Piguet",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Watches",
        "price": 6800000,        "img_key": "ap_royal_oak",
        "is_cloudinary": true,

        "desc": "Extra-thin Royal Oak with the iconic tapisserie dial."
    },
    {
        "name": "Richard Mille RM 65-01",
        "brand": "Richard Mille",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Watches",
        "price": 25000000,        "img_key": "richard_mille",
        "is_cloudinary": true,

        "desc": "Highly complex automatic split-seconds chronograph in Carbon TPT."
    },
    {
        "name": "Vacheron Constantin Overseas",
        "brand": "Vacheron Constantin",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Watches",
        "price": 2400000,        "img_key": "vacheron_overseas",
        "is_cloudinary": true,

        "desc": "Elegant sports watch with blue lacquered dial and interchangeable straps."
    },
    {
        "name": "A. Lange & S\u00f6hne Lange 1",
        "brand": "A. Lange & S\u00f6hne",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Watches",
        "price": 3800000,
        "desc": "German watchmaking masterpiece with outsize date and off-center dial.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826740/luxon_products/bazjvrpknxd3tz0yzrkk.png",
        "is_cloudinary": true
    },
    {
        "name": "Jaeger-LeCoultre Reverso Tribute",
        "brand": "Jaeger-LeCoultre",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Watches",
        "price": 950000,        "img_key": "jlc_reverso",
        "is_cloudinary": true,

        "desc": "Iconic Art Deco design with a reversible case mechanism."
    },
    {
        "name": "Rolex Daytona Platinum",
        "brand": "Rolex",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Watches",
        "price": 7500000,        "img_key": "rolex_daytona_plat",
        "is_cloudinary": true,

        "desc": "Cosmograph Daytona in 950 platinum with ice-blue dial and chestnut cerachrom bezel."
    },
    {
        "name": "Hermes Kelly 25 Sellier Epsom",
        "brand": "Hermes",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 1200000,        "img_key": "hermes_kelly",
        "is_cloudinary": true,

        "desc": "Structured and elegant Kelly bag in durable Epsom leather."
    },
    {
        "name": "Bottega Veneta Cassette Bag",
        "brand": "Bottega Veneta",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 225000,        "img_key": "bottega_cassette",
        "is_cloudinary": true,

        "desc": "Padded intrecciato woven leather cross-body bag."
    },
    {
        "name": "Dior Lady Dior Medium",
        "brand": "Dior",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 450000,        "img_key": "dior_lady",
        "is_cloudinary": true,

        "desc": "The iconic bag featuring Cannage stitching and 'D.I.O.R.' charms."
    },
    {
        "name": "Goyard Saint Louis GM",
        "brand": "Goyard",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 185000,        "img_key": "goyard_st_louis",
        "is_cloudinary": true,

        "desc": "Lightweight, reversible tote featuring the classic Goyardine canvas."
    },
    {
        "name": "Fendi Peekaboo ISeeU",
        "brand": "Fendi",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 385000,        "img_key": "fendi_peekaboo",
        "is_cloudinary": true,

        "desc": "Iconic bag with a twist lock and distinctive inner compartment."
    },
    {
        "name": "Prada Galleria Saffiano",
        "brand": "Prada",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 310000,        "img_key": "prada_galleria",
        "is_cloudinary": true,

        "desc": "Classic tote crafted from Prada's signature scratch-resistant Saffiano leather."
    },
    {
        "name": "Celine Triomphe Canvas Bag",
        "brand": "Celine",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 240000,        "img_key": "celine_triomphe",
        "is_cloudinary": true,

        "desc": "Vintage-inspired shoulder bag featuring the Triomphe clasp."
    },
    {
        "name": "Loro Piana Vicu\u00f1a Coat",
        "brand": "Loro Piana",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Clothing",
        "price": 1250000,
        "desc": "Incredibly rare and soft overcoat made entirely from Vicu\u00f1a wool.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826741/luxon_products/hnud31elnqp5znyhvzup.png",
        "is_cloudinary": true
    },
    {
        "name": "Brunello Cucinelli Cashmere Sweater",
        "brand": "Brunello Cucinelli",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Clothing",
        "price": 145000,        "img_key": "brunello_sweater",
        "is_cloudinary": true,

        "desc": "Hand-crafted cashmere sweater from the medieval village of Solomeo."
    },
    {
        "name": "Kiton Bespoke Suit",
        "brand": "Kiton",
        "cat": "Fashion",
        "gender": "Men",
        "sub": "Clothing",
        "price": 650000,        "img_key": "kiton_suit",
        "is_cloudinary": true,

        "desc": "The pinnacle of Neapolitan tailoring. Entirely handmade."
    },
    {
        "name": "Brioni Silk Dinner Jacket",
        "brand": "Brioni",
        "cat": "Fashion",
        "gender": "Men",
        "sub": "Clothing",
        "price": 420000,        "img_key": "brioni_jacket",
        "is_cloudinary": true,

        "desc": "Exquisite silk evening jacket tailored to perfection in Rome."
    },
    {
        "name": "Gucci GG Jacquard Cardigan",
        "brand": "Gucci",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Clothing",
        "price": 125000,        "img_key": "gucci_cardigan",
        "is_cloudinary": true,

        "desc": "Wool-blend cardigan featuring the iconic GG monogram pattern."
    },
    {
        "name": "Balenciaga Speedhunters T-Shirt",
        "brand": "Balenciaga",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Clothing",
        "price": 55000,        "img_key": "balenciaga_shirt",
        "is_cloudinary": true,

        "desc": "Oversized graphic tee inspired by vintage concert merchandise."
    },
    {
        "name": "Burberry Heritage Trench Coat",
        "brand": "Burberry",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Clothing",
        "price": 185000,        "img_key": "burberry_trench",
        "is_cloudinary": true,

        "desc": "The iconic waterproof gabardine trench coat crafted in England."
    },
    {
        "name": "John Lobb City II Oxfords",
        "brand": "John Lobb",
        "cat": "Fashion",
        "gender": "Men",
        "sub": "Shoes",
        "price": 145000,        "img_key": "john_lobb_oxfords",
        "is_cloudinary": true,

        "desc": "The benchmark for classic black calf leather Oxford shoes."
    },
    {
        "name": "Berluti Alessandro Galet",
        "brand": "Berluti",
        "cat": "Fashion",
        "gender": "Men",
        "sub": "Shoes",
        "price": 185000,        "img_key": "berluti_shoes",
        "is_cloudinary": true,

        "desc": "Seamless wholecut Oxford featuring Berluti's signature patina."
    },
    {
        "name": "Manolo Blahnik Hangisi Pumps",
        "brand": "Manolo Blahnik",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Shoes",
        "price": 85000,        "img_key": "manolo_pumps",
        "is_cloudinary": true,

        "desc": "Satin almond-toe pump featuring a crystal-embellished buckle."
    },
    {
        "name": "Jimmy Choo Bing 100",
        "brand": "Jimmy Choo",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Shoes",
        "price": 75000,        "img_key": "jimmy_choo_mule",
        "is_cloudinary": true,

        "desc": "Patent leather mule featuring a crystal-embellished strap."
    },
    {
        "name": "Hermes Oran Sandals",
        "brand": "Hermes",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Shoes",
        "price": 55000,        "img_key": "hermes_sandals",
        "is_cloudinary": true,

        "desc": "The iconic flat sandal with the distinctive 'H' cut-out."
    },
    {
        "name": "Balenciaga Track Sneakers",
        "brand": "Balenciaga",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Shoes",
        "price": 82000,
        "desc": "Complex, multi-layered high-performance style sneaker.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826742/luxon_products/fsty7plretiavsusohuz.png",
        "is_cloudinary": true
    },
    {
        "name": "Alexander McQueen Oversized Sneaker",
        "brand": "Alexander McQueen",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Shoes",
        "price": 45000,
        "desc": "Smooth calf leather lace-up sneaker with oversized rubber sole.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826744/luxon_products/apc0gjbwrbefkxgp2lrj.png",
        "is_cloudinary": true
    },
    {
        "name": "Lalique Bacchantes Vase",
        "brand": "Lalique",
        "cat": "Lifestyle",
        "sub": "Home Decor",
        "price": 280000,
        "desc": "Iconic crystal vase featuring sculpted priestesses of Bacchus.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826745/luxon_products/oajxchqtad9hkj8rmcii.png",
        "is_cloudinary": true
    },
    {
        "name": "Christofle Mood Flatware Set",
        "brand": "Christofle",
        "cat": "Lifestyle",
        "sub": "Home Decor",
        "price": 125000,
        "desc": "24-piece silver-plated flatware set housed in a decorative egg.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826746/luxon_products/tmonumvupihduymxtzsi.png",
        "is_cloudinary": true
    },
    {
        "name": "Hermes Avalon Throw Blanket",
        "brand": "Hermes",
        "cat": "Lifestyle",
        "sub": "Home Decor",
        "price": 135000,
        "desc": "Merino wool and cashmere jacquard woven blanket with 'H' pattern.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826747/luxon_products/wghaw40uzfeitjxtkeia.png",
        "is_cloudinary": true
    },
    {
        "name": "Fornasetti Profumi Candle",
        "brand": "Fornasetti",
        "cat": "Lifestyle",
        "sub": "Home Decor",
        "price": 25000,
        "desc": "Hand-poured candle in a ceramic vessel featuring Piero Fornasetti's art.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826748/luxon_products/f13fyhrojsnku8hp9mdj.png",
        "is_cloudinary": true
    },
    {
        "name": "Roja Parfums Elysium",
        "brand": "Roja Parfums",
        "cat": "Lifestyle",
        "sub": "Fragrances",
        "price": 45000,
        "desc": "A bright, refreshing, and incredibly complex luxury parfum.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826749/luxon_products/tsc12k4jlur5zoiwmsu6.png",
        "is_cloudinary": true
    },
    {
        "name": "Clive Christian No.1",
        "brand": "Clive Christian",
        "cat": "Lifestyle",
        "sub": "Fragrances",
        "price": 65000,
        "desc": "Recognized as the world's most expensive perfume. Pure sophistication.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826750/luxon_products/rlqkvgxlexsw5c50ku3w.png",
        "is_cloudinary": true
    },
    {
        "name": "Maison Francis Kurkdjian Baccarat Rouge 540",
        "brand": "MFK",
        "cat": "Lifestyle",
        "sub": "Fragrances",
        "price": 32000,
        "desc": "Luminous and sophisticated, laying on the skin like an amber, floral, and woody breeze.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826751/luxon_products/hojptildecrj9s2mtwoq.png",
        "is_cloudinary": true
    },
    {
        "name": "Amouage Interlude Man",
        "brand": "Amouage",
        "cat": "Lifestyle",
        "sub": "Fragrances",
        "price": 28000,
        "desc": "A spicy and woody fragrance inspired by chaos and disorder.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826751/luxon_products/hootymq7phi85ie5jre5.png",
        "is_cloudinary": true
    },
    {
        "name": "Cartier Love Bracelet",
        "brand": "Cartier",
        "cat": "Lifestyle",
        "sub": "Accessories",
        "price": 550000,
        "desc": "Iconic 18K yellow gold bracelet locked with a screwdriver.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826752/luxon_products/h6cwvzqwsnd5pnvuawox.png",
        "is_cloudinary": true
    },
    {
        "name": "Van Cleef & Arpels Alhambra Necklace",
        "brand": "VCA",
        "cat": "Lifestyle",
        "sub": "Accessories",
        "price": 225000,
        "desc": "Vintage Alhambra pendant featuring the iconic clover motif in onyx.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826753/luxon_products/r5bvu545th6tjiaif3uh.png",
        "is_cloudinary": true
    },
    {
        "name": "Bulgari B.zero1 Ring",
        "brand": "Bulgari",
        "cat": "Lifestyle",
        "sub": "Accessories",
        "price": 185000,
        "desc": "Bold ring inspired by the Colosseum, in 18K rose gold and black ceramic.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826754/luxon_products/yzgptkoapsoxvgkhfuiz.png",
        "is_cloudinary": true
    },
    {
        "name": "Tiffany & Co. HardWear Necklace",
        "brand": "Tiffany & Co.",
        "cat": "Lifestyle",
        "sub": "Accessories",
        "price": 350000,
        "desc": "Graduated link necklace in 18k gold.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826755/luxon_products/wv6vs1lmxko2ob4xdu4r.png",
        "is_cloudinary": true
    },
    {
        "name": "Original Abstract Canvas - Azure Depth",
        "brand": "Luxon Art Gallery",
        "cat": "Lifestyle",
        "sub": "Art",
        "price": 450000,
        "desc": "Unique 40x40 oil on canvas by emerging contemporary artist.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826756/luxon_products/jnawvvsupg6ffemtfeoo.png",
        "is_cloudinary": true
    },
    {
        "name": "Bronze Panther Sculpture",
        "brand": "Luxon Art Gallery",
        "cat": "Lifestyle",
        "sub": "Art",
        "price": 280000,
        "desc": "Art Deco style hand-cast bronze sculpture on marble base.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826757/luxon_products/dwp0i18xulu4vsbglg6c.png",
        "is_cloudinary": true
    },
    {
        "name": "Burberry Kids Trench",
        "brand": "Exclusive",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Accessories",
        "price": 50000,
        "desc": "An exclusive limited edition luxury piece.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826758/luxon_products/b72pfaj3y4bynw4da6wz.png",
        "is_cloudinary": true
    },
    {
        "name": "Gucci Kids Sneakers",
        "brand": "Exclusive",
        "cat": "Fashion",
        "gender": "Kids",
        "sub": "Bags",
        "price": 60000,
        "desc": "An exclusive limited edition luxury piece.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826759/luxon_products/lrsv7aernuscn2qhsf8h.png",
        "is_cloudinary": true
    },
    {
        "name": "Baby Dior Stroller",
        "brand": "Exclusive",
        "cat": "Fashion",
        "gender": "Kids",
        "sub": "Accessories",
        "price": 70000,
        "desc": "An exclusive limited edition luxury piece.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826760/luxon_products/obfyi01jzdvdp13qsr5n.png",
        "is_cloudinary": true
    },
    {
        "name": "Givenchy Kids Hoodie",
        "brand": "Exclusive",
        "cat": "Fashion",
        "gender": "Kids",
        "sub": "Bags",
        "price": 80000,
        "desc": "An exclusive limited edition luxury piece.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826761/luxon_products/qy80vjg6twykh9cxk7h3.png",
        "is_cloudinary": true
    },
    {
        "name": "Bvlgari Serpenti Necklace",
        "brand": "Bvlgari",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Accessories",
        "price": 450000,
        "desc": "18k rose gold necklace set with pavé diamonds mimicking a serpent.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826763/luxon_products/r8yqx5b5xwdpgss6klcu.png",
        "is_cloudinary": true
    },
    {
        "name": "Chopard Happy Diamonds Watch",
        "brand": "Chopard",
        "cat": "Watches",
        "gender": "Women",
        "sub": "Watches",
        "price": 850000,
        "desc": "Iconic watch featuring dancing diamonds inside the case.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826764/luxon_products/suwfu0dqp8go6tnpzjwp.png",
        "is_cloudinary": true
    },
    {
        "name": "Cartier Panthere Ring",
        "brand": "Cartier",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Accessories",
        "price": 320000,
        "desc": "Sculptural panther ring in yellow gold with emerald eyes.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826765/luxon_products/dopy14wdk0ti4n0v75ev.png",
        "is_cloudinary": true
    },
    {
        "name": "Rolex Daytona Rose Gold",
        "brand": "Rolex",
        "cat": "Watches",
        "gender": "Men",
        "sub": "Watches",
        "price": 4200000,
        "desc": "18ct Everose gold chronograph watch with a black dial.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826766/luxon_products/nrtobomyp3h0qauopqon.png",
        "is_cloudinary": true
    },
    {
        "name": "Fendi Baguette Bag",
        "brand": "Fendi",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 280000,
        "desc": "Classic FF canvas baguette shoulder bag with gold-tone hardware.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826767/luxon_products/cgdepo3wcb4ambyxjwlf.png",
        "is_cloudinary": true
    },
    {
        "name": "Saint Laurent Tuxedo",
        "brand": "YSL",
        "cat": "Fashion",
        "gender": "Men",
        "sub": "Clothing",
        "price": 350000,
        "desc": "Iconic 'Le Smoking' tailored grain de poudre tuxedo.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826768/luxon_products/vjg24zc9tavzxx1hcub3.png",
        "is_cloudinary": true
    },
    {
        "name": "Prada Cleo Bag",
        "brand": "Prada",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 210000,
        "desc": "Sleek brushed leather hobo bag with a curved silhouette.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826769/luxon_products/dmvgvg7khluigdgwmlpk.png",
        "is_cloudinary": true
    },
    {
        "name": "Balmain Blazer",
        "brand": "Balmain",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Clothing",
        "price": 180000,
        "desc": "Structured double-breasted wool blazer with embossed gold buttons.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826770/luxon_products/nqkz4pllnjvsx4j9ujyk.png",
        "is_cloudinary": true
    },
    {
        "name": "Valentino Rockstud Pumps",
        "brand": "Valentino",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Shoes",
        "price": 85000,
        "desc": "Patent leather stiletto heels adorned with signature pyramid studs.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826771/luxon_products/bvxtzy8srm9hkhqshr3u.png",
        "is_cloudinary": true
    },
    {
        "name": "Givenchy Antigona Bag",
        "brand": "Givenchy",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 195000,
        "desc": "Trapezoid-shaped medium duffel bag in glossy goatskin.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826773/luxon_products/kkiaufh0jt8qr7330jaw.png",
        "is_cloudinary": true
    },
    {
        "name": "Versace Medusa Belt",
        "brand": "Versace",
        "cat": "Fashion",
        "gender": "Men",
        "sub": "Accessories",
        "price": 45000,
        "desc": "Smooth calf leather belt featuring the iconic gold Medusa buckle.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826773/luxon_products/nv7kgt4jebjo2pl6wgyg.png",
        "is_cloudinary": true
    },
    {
        "name": "Hermes H Belt",
        "brand": "Hermes",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Accessories",
        "price": 75000,
        "desc": "Reversible leather belt strap with the classic H buckle.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826774/luxon_products/rjdvorlqhfrnha8q83pz.png",
        "is_cloudinary": true
    },
    {
        "name": "Burberry Cashmere Scarf",
        "brand": "Burberry",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Accessories",
        "price": 42000,
        "desc": "Classic vintage check scarf made from ultra-soft Scottish cashmere.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826775/luxon_products/c9mqghvtlxbf1bq6tucl.png",
        "is_cloudinary": true
    },
    {
        "name": "Tom Ford Aviator Sunglasses",
        "brand": "Tom Ford",
        "cat": "Fashion",
        "gender": "Men",
        "sub": "Accessories",
        "price": 38000,
        "desc": "Sleek metal aviator sunglasses with the signature T logo hinge.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826776/luxon_products/li5v0pcfsarc8wnxhroo.png",
        "is_cloudinary": true
    },
    {
        "name": "Louboutin Kate Pumps",
        "brand": "Louboutin",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Shoes",
        "price": 78000,
        "desc": "Classic pointed-toe stiletto pumps showcasing the iconic red sole.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826777/luxon_products/rdrxs1o1cnl7ack2cnpe.png",
        "is_cloudinary": true
    },
    {
        "name": "Maison Margiela Tabi Boots",
        "brand": "Maison Margiela",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Shoes",
        "price": 95000,
        "desc": "Avant-garde split-toe ankle boots in smooth calf leather.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826778/luxon_products/s4pkyhoudj2kyfkvxuns.png",
        "is_cloudinary": true
    },
    {
        "name": "Goyard Belvedere Bag",
        "brand": "Goyard",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 260000,
        "desc": "Saddle-shaped crossbody bag featuring Goyardine canvas.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826779/luxon_products/a8g2vngvvfx5cea7erha.png",
        "is_cloudinary": true
    },
    {
        "name": "Louis Vuitton Keepall",
        "brand": "Louis Vuitton",
        "cat": "Fashion",
        "gender": "Unisex",
        "sub": "Bags",
        "price": 220000,
        "desc": "Classic monogram canvas duffel bag perfect for weekend travel.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826780/luxon_products/pd2ptlzw8coijtfnvbok.png",
        "is_cloudinary": true
    },
    {
        "name": "Rimowa Cabin Suitcase",
        "brand": "Rimowa",
        "cat": "Lifestyle",
        "gender": "Unisex",
        "sub": "Accessories",
        "price": 110000,
        "desc": "Iconic grooved aluminum hard-shell carry-on luggage.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826781/luxon_products/juxetusjw4gobfzbd8qg.png",
        "is_cloudinary": true
    },
    {
        "name": "Dior Saddle Bag",
        "brand": "Dior",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 320000,
        "desc": "Equestrian-inspired handbag in blue Oblique jacquard canvas.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826782/luxon_products/pimbbx8zwynuezwbyovx.png",
        "is_cloudinary": true
    },
    {
        "name": "Bottega Veneta Jodie",
        "brand": "Bottega Veneta",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 215000,
        "desc": "Mini knotted hobo bag crafted in signature Intrecciato leather.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826783/luxon_products/wjpblpl8zxeu3kr5tlln.png",
        "is_cloudinary": true
    },
    {
        "name": "Jacquemus Le Chiquito",
        "brand": "Jacquemus",
        "cat": "Fashion",
        "gender": "Women",
        "sub": "Bags",
        "price": 65000,
        "desc": "Famous micro handbag with a highly exaggerated top handle.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826784/luxon_products/qf5omuuooykgiywaumud.png",
        "is_cloudinary": true
    },
    {
        "name": "Rolex Datejust 41",
        "brand": "Rolex",
        "cat": "Watches",
        "gender": "Men",
        "sub": "Watches",
        "price": 1100000,
        "desc": "Classic Oystersteel and white gold watch with a fluted bezel.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826785/luxon_products/yet95jid2n6ghs8cael3.png",
        "is_cloudinary": true
    },
    {
        "name": "Patek Philippe Aquanaut",
        "brand": "Patek Philippe",
        "cat": "Watches",
        "gender": "Men",
        "sub": "Watches",
        "price": 5500000,
        "desc": "Modern luxury sports watch with a rounded octagon steel case.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826786/luxon_products/bov21cv4uifia5dqka4y.png",
        "is_cloudinary": true
    },
    {
        "name": "Cartier Santos",
        "brand": "Cartier",
        "cat": "Watches",
        "gender": "Men",
        "sub": "Watches",
        "price": 750000,
        "desc": "Square-faced stainless steel watch with exposed screws on the bezel.",
        "img_key": "https://res.cloudinary.com/drzkhibqf/image/upload/v1780826787/luxon_products/sy2xrr2tlxfhybbjv1rw.png",
        "is_cloudinary": true
    }
]''')

def get_placeholder(name):
    # Create a luxurious placeholder image
    encoded_name = urllib.parse.quote(name)
    return f"https://placehold.co/600x750/0F172A/D4AF37/webp?text={encoded_name}&font=Playfair+Display"

def seed_db():
    with app.app_context():
        print("Clearing database...")
        db.session.query(Product).delete()
        db.session.query(Subcategory).delete()
        db.session.query(Category).delete()
        db.session.commit()

        # Ensure admin exists
        admin = User.query.filter_by(email="admin@luxon.com").first()
        if not admin:
            admin = User(
                first_name="Admin",
                last_name="User",
                email="admin@luxon.com",
                password_hash=generate_password_hash("admin"),
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()

        print("Creating categories & products...")
        
        cat_map = {}
        sub_map = {}
        
        for c in CATEGORIES:
            cat = Category(name=c["name"])
            db.session.add(cat)
            db.session.flush()
            cat_map[c["name"]] = cat.id
            
            for sub in c["subs"]:
                subcategory = Subcategory(name=sub, category_id=cat.id)
                db.session.add(subcategory)
                db.session.flush()
                sub_map[sub] = subcategory.id

        for idx, p in enumerate(PRODUCTS_DATA):
            is_featured = p.get("featured", idx % 10 == 0) # Feature ~10%
            
            discount_pct = random.choice([0, 0, 0, 15, 20, 25]) if is_featured else random.choice([0, 0, 0, 0, 10, 15])
            
            price = p["price"]
            original_price = None
            if discount_pct > 0:
                original_price = int(price / (1 - (discount_pct/100.0)))
                original_price = round(original_price, -3)

            # Check if image is from Cloudinary
            if p.get("is_cloudinary"):
                img_val = p.get("img_key")
                image_url = img_val if img_val.startswith("http") else CLOUDINARY_URLS[img_val]
            else:
                image_url = get_placeholder(p["brand"] + "\n" + p["name"].split(' ')[-1])

            prod = Product(
                name=p["name"],
                description=p["desc"],
                price=price,
                original_price=original_price,
                stock=random.randint(2, 25),
                brand=p["brand"],
                gender=p.get("gender"),
                image_url=image_url,
                category_id=cat_map.get(p["cat"], list(cat_map.values())[0]),
                subcategory_id=sub_map.get(p["sub"], list(sub_map.values())[0]),
                is_featured=is_featured
            )
            db.session.add(prod)

        db.session.commit()
        print(f"Successfully seeded {len(PRODUCTS_DATA)} luxury products!")

if __name__ == "__main__":
    seed_db()
