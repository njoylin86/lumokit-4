/* Shared menu + content data for all pages. Loaded as a normal <script>. */

window.OB_CATS = [
  { id: "brod",     label: "Bröd & Smörgåsar", emoji: "🥖", count: 5,
    image: "../../assets/food/sub-sandwich.jpg",
    note: "Frallor 35:- · standardsmörgåsar 45:- (student 40:-)." },
  { id: "sallader", label: "Sallader",         emoji: "🥗", count: 6,
    image: "../../assets/food/grilled-chicken-platter.png",
    note: "Välj mellan bulgur eller quinoa. Bröd & läsk 33cl ingår." },
  { id: "wraps",    label: "Wraps & Mezé",     emoji: "🌯", count: 5,
    image: "../../assets/food/meze-platter.png",
    note: "Grillas direkt på platta. Mezetallrik för delning." },
  { id: "drycker",  label: "Drycker",          emoji: "☕", count: 12,
    image: "../../assets/food/coffee-rose.png" },
  { id: "bakverk",  label: "Bakverk",          emoji: "🧁", count: 6,
    image: "../../assets/food/kanelbulle.png",
    note: "Bakat på morgonen. Slut är slut." },
];

window.OB_MENU = {
  brod: [
    { id: "ciabatta-salami",   title: "Salami ciabatta",   desc: "Mozzarella, ruccola, soltorkade tomater & örtpesto.", price: 80, student: 70, image: "../../assets/food/sub-sandwich.jpg", tag: "Färskt idag", tagTone: "skog" },
    { id: "focaccia-kyckling", title: "Focaccia kyckling", desc: "Kyckling, mozzarella, grönsaker & basilika dressing.", price: 70, student: 60, image: "../../assets/food/sandwich-platter.png" },
    { id: "vegan-smorgas",     title: "Vegan smörgås",     desc: "Surdeg, hummus, sallad, avokado, morötter & solfrön.", price: 70, student: 60, image: "../../assets/food/breads.jpg", tag: "Vegan", tagTone: "skog" },
    { id: "italiensk-prosciutto", title: "Italiensk prosciutto", desc: "Prosciutto, mozzarella, basilika, soltorkade tomater & örtpesto.", price: 80, student: 70, image: "../../assets/food/sub-sandwich.jpg" },
    { id: "avokado-agg",       title: "Avokado & ägg", desc: "Avokado, ägg & chili flakes på ciabatta.", price: 80, student: 70, image: "../../assets/food/citrus-board.png" },
  ],
  sallader: [
    { id: "halsosallad-kyckling", title: "Hälsosallad med kyckling", desc: "Grillad kyckling, hummus, halloumi, granatäpple & vitlökscreme.", price: 110, student: 90, image: "../../assets/food/grilled-chicken-platter.png", tag: "Stamkund", tagTone: "saffran" },
    { id: "halsosallad-rakor",    title: "Hälsosallad med räkor",    desc: "Räkor, fetaost, bönor, granatäpple, avokado, citron & ägg.",    price: 120, student: 110, image: "../../assets/food/meze-platter.png" },
    { id: "vegansallad",          title: "Vegansallad",              desc: "Falafel, kronärtskocka, hummus, vinbladsdolmar, tomat & lök.",    price: 110, student: 90, image: "../../assets/food/citrus-board.png", tag: "Vegan", tagTone: "skog" },
    { id: "vegetarisk",           title: "Vegetarisk sallad",        desc: "Fetaost, halloumi, paprikaröra, tomat, sallad, labneh & oliver.", price: 110, student: 90, image: "../../assets/food/kebab-bowl.png" },
    { id: "kyckling-linser",      title: "Kyckling med gröna linser", desc: "Grön hummus, färska grönsaker, bulgur eller quinoa.",            price: 110, student: 90, image: "../../assets/food/grilled-chicken-platter.png" },
    { id: "potatis-quinoa",       title: "Potatissallad med quinoa", desc: "Färska potatisar, grönsaker & basilika dressing.",                price: 110, student: 90, image: "../../assets/food/sandwich-platter.png" },
  ],
  wraps: [
    { id: "wrap-halloumi-kyckling", title: "Kyckling & halloumi wrap", desc: "Tomat & färsk mynta. Grillad på platta.", price: 85, student: 75, image: "../../assets/food/kebab-bowl.png" },
    { id: "wrap-falafel-halloumi",  title: "Falafel & halloumi wrap",  desc: "Vildgurka, tomat, färsk mynta & tahinisås.", price: 85, student: 75, image: "../../assets/food/citrus-board.png" },
    { id: "mezetallrik",            title: "Mezetallrik",              desc: "Hummus, tarator, auberginröra, paprikaröra, kibbe & libanesisk potatissallad.", price: 110, student: 90, image: "../../assets/food/kebab-skewers.png", tag: "Nytt", tagTone: "granat" },
    { id: "ostras-special",         title: "Östras special",           desc: "Kyckling, sojabönor, quinoa, hummus, rödlök & basilika dressing.", price: 85, student: 75, image: "../../assets/food/grilled-chicken-platter.png" },
    { id: "nottfars-spettrulle",    title: "Nötfärsspettrulle",        desc: "Halloumi, lök, persilja & vitlökscreme. Grillad.", price: 85, student: 75, image: "../../assets/food/kebab-skewers.png" },
  ],
  drycker: [
    { id: "ostras-mocka",  title: "Östras mocka",  desc: "Dubbel espresso, ångvispad mjölk, hasselnöt syrup & grädde.", price: 35, student: 25 },
    { id: "mocka-blanco",  title: "Mocka Blanco",  desc: "Enkel espresso, vaniljsyrup & ångvispad mjölk.",              price: 35, student: 25 },
    { id: "chai-latte",    title: "Chai latte",    desc: "Chai syrup, ångvispad mjölk & kanel krydda.",                  price: 35, student: 25 },
    { id: "caramello",     title: "Caramello",     desc: "Espresso, caramel syrup, ångvispad mjölk, kakao & grädde.",    price: 35, student: 25 },
    { id: "macchiato",     title: "Macchiato",     desc: "Enkel espresso & ångvispad mjölk.",                            price: 35, student: 25 },
    { id: "cortado",       title: "Cortado",       desc: "Dubbel espresso & varm mjölk.",                                price: 35, student: 25 },
    { id: "americano",     title: "Americano",     desc: "Dubbel espresso & hett vatten.",                               price: 35, student: 25 },
    { id: "iced-latte",    title: "Islatte",       desc: "Iskaffe med mjölk.",                                           price: 35, student: 25 },
    { id: "cappuccino",    title: "Cappuccino",                                                                          price: 35, student: 25 },
    { id: "varm-choklad",  title: "Varm choklad",  desc: "Mjölk, grädde & chokladsås.",                                  price: 35, student: 25 },
    { id: "kaffe",         title: "Kaffe",         desc: "Bryggkaffe från Löfbergs.",                                    price: 20, student: 10 },
    { id: "te",            title: "Te / Grönt te", desc: "Olika smaker.",                                                price: 20, student: 10 },
  ],
  bakverk: [
    { id: "kanelbulle",    title: "Kanelbulle",          desc: "Doftar genom hela vänthallen kl 07.",          price: 30, image: "../../assets/food/kanelbulle.png", tag: "Färskt idag", tagTone: "skog" },
    { id: "kardemummabulle", title: "Kardemummabulle",   desc: "Bakat på morgonen.",                            price: 32 },
    { id: "tiramisu",      title: "Tiramisu i glas",     desc: "Espresso, mascarpone, kakao.",                  price: 45 },
    { id: "pistage-tryffel", title: "Pistage-tryffel",   desc: "Hemgjord, två per portion.",                    price: 35 },
    { id: "panna-cotta",   title: "Panna cotta · jordgubb", desc: "Med färska jordgubbar.",                     price: 45 },
    { id: "wienerbrod",    title: "Wienerbröd · vanilj", desc: "Smörig, gyllenbrun, klassisk.",                 price: 35 },
  ],
};

window.OB_TIERS = [
  { name: "Lilla brickan", price: 95,  items: ["3 sorters smörgåsar", "Sallad i bägare", "Kaffe eller te"] },
  { name: "Stora brickan", price: 145, highlight: true, items: ["Mezé för delning", "2 wraps per person", "Bakverk", "Kaffe + juice"] },
  { name: "Kontorslunch",  price: 185, items: ["Hela menyn att välja från", "Levereras till dörren", "Engångsservis ingår", "Faktura"] },
];

window.OB_QUOTES = [
  { text: "Bästa halloumi-wrappen i Stockholm. Jag tar tåget från Tekniska bara för det.", name: "Marwa A.", role: "Stamkund · KTH" },
  { text: "Vi har beställt catering tre gånger. Snabbt, gott, alla på kontoret blir glada.", name: "Johan S.", role: "PR-byrå, Östermalm" },
  { text: "Kanelbullarna doftar genom hela vänthallen. Klockan sju på morgonen.", name: "Anna K.", role: "Pendlare" },
];
