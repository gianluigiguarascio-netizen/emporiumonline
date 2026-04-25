const fs = require('fs');
const path = require('path');

const newProducts = [
  // ABBIGLIAMENTO
  { asin:"B0GWLYGTQQ", name:"Abito Elegante Donna Monospalla Stampa Fantasia Gonna Ampia", category:"abbigliamento", emoji:"👗", clr1:"#ff6b9d", clr2:"#a78bfa", image:"https://m.media-amazon.com/images/I/71rq7SFq5sL._AC_SL300_.jpg", price:22.59, oldPrice:null, discount:null, offerBadge:false },
  { asin:"B0C3ZN76M5", name:"Abiti Lunghi Donna Eleganti Estivi Fantasia Floreale Vestito Casual Spiaggia", category:"abbigliamento", emoji:"👗", clr1:"#34d399", clr2:"#f472b6", image:"https://m.media-amazon.com/images/I/61K217CxPWL._AC_SL300_.jpg", price:28.03, oldPrice:null, discount:null, offerBadge:false },
  { asin:"B0B8RGXTNW", name:"ORANDESIGNE Abito Lungo Donna Senza Maniche Stampa Floreale Estivo", category:"abbigliamento", emoji:"👗", clr1:"#fbbf24", clr2:"#34d399", image:"https://m.media-amazon.com/images/I/61ORC-tWTPL._AC_SL300_.jpg", price:29.99, oldPrice:null, discount:null, offerBadge:false },
  { asin:"B0CB8F23T3", name:"Onsoyours Vestito Estivo Donna Boho Stampa Fantasia Spiaggia Corto", category:"abbigliamento", emoji:"👗", clr1:"#fb923c", clr2:"#38bdf8", image:"https://m.media-amazon.com/images/I/71dFywTbxaL._AC_SL300_.jpg", price:15.99, oldPrice:null, discount:null, offerBadge:false },
  { asin:"B0GK8ZN7W7", name:"GISELA Abito Copricostume Donna Stampa Etnica Boho Multicolor Viscosa 100%", category:"abbigliamento", emoji:"👗", clr1:"#0ea5e9", clr2:"#f97316", image:"https://m.media-amazon.com/images/I/81Rz7ioEdLL._AC_SL300_.jpg", price:19.90, oldPrice:null, discount:null, offerBadge:false },
  { asin:"B0FCMQ76TW", name:"Abito Estivo Donna Floreale Boho Scollo U Stampa Fantasia Casual Spiaggia", category:"abbigliamento", emoji:"👗", clr1:"#f472b6", clr2:"#22c55e", image:"https://m.media-amazon.com/images/I/61K9h5zyb8L._AC_SL300_.jpg", price:10.99, oldPrice:null, discount:null, offerBadge:true },
  { asin:"B0B31R9V6K", name:"Onsoyours Abito Estivo Donna T-Shirt Casual Stampa Floreale Fantasia con Tasche", category:"abbigliamento", emoji:"👗", clr1:"#a78bfa", clr2:"#34d399", image:"https://m.media-amazon.com/images/I/51t64fGzvuL._AC_SL300_.jpg", price:17.99, oldPrice:null, discount:null, offerBadge:false },
  { asin:"B0GM53W8FK", name:"Abiti Estivi Casual Donna Stampa Uccelli Colorati con Tasche Scollo V", category:"abbigliamento", emoji:"👗", clr1:"#38bdf8", clr2:"#f43f5e", image:"https://m.media-amazon.com/images/I/610aULsnQML._AC_SL300_.jpg", price:25.86, oldPrice:null, discount:null, offerBadge:false },
  // SCARPE
  { asin:"B0BZLRH8X3", name:"Sneakers Arcobaleno Donna Leggere Sportive Colorate Suola Spessa Moda Strada", category:"scarpe", emoji:"👟", clr1:"#ff6b9d", clr2:"#38bdf8", image:"https://m.media-amazon.com/images/I/610f8WAFnEL._AC_SL300_.jpg", price:22.04, oldPrice:null, discount:null, offerBadge:false },
  { asin:"B0BZLSZHKP", name:"Scarpe Arcobaleno Donna Sneakers Colorate Sportive Moda di Strada Suola Spessa", category:"scarpe", emoji:"👟", clr1:"#fbbf24", clr2:"#a78bfa", image:"https://m.media-amazon.com/images/I/61SzaofhIML._AC_SL300_.jpg", price:22.04, oldPrice:null, discount:null, offerBadge:false },
  { asin:"B083NDY23J", name:"Hitmars Scarpe Running Donna Ginnastica Sneaker Leggere Traspiranti Multicolore", category:"scarpe", emoji:"👟", clr1:"#34d399", clr2:"#fb923c", image:"https://m.media-amazon.com/images/I/61ku6-QDBtL._AC_SL300_.jpg", price:33.99, oldPrice:null, discount:null, offerBadge:false },
  { asin:"B09WMSDY73", name:"inblu Ciabatte Donna Fascia Fantasia Jungle con Plantare Sughero Naturale", category:"scarpe", emoji:"👡", clr1:"#22c55e", clr2:"#fbbf24", image:"https://m.media-amazon.com/images/I/61ZBMytKBOL._AC_SL300_.jpg", price:9.25, oldPrice:null, discount:null, offerBadge:true },
  { asin:"B0D9WHXNMN", name:"Reebok Sneakers Multicolore Donna Shaq Victory Pump in Pelle", category:"scarpe", emoji:"👟", clr1:"#818cf8", clr2:"#f472b6", image:"https://m.media-amazon.com/images/I/616f2o0wsCL._AC_SL300_.jpg", price:69.95, oldPrice:null, discount:null, offerBadge:true },
  // CASA
  { asin:"B0FRSPZ5ZZ", name:"Vaso in Vetro Cristallo Colorato Dipinto a Mano Alto 17.5 cm Centrotavola Decorativo", category:"casa", emoji:"🌿", clr1:"#38bdf8", clr2:"#f472b6", image:"https://m.media-amazon.com/images/I/711mmQiUvWL._AC_SL300_.jpg", price:27.99, oldPrice:null, discount:null, offerBadge:false },
  { asin:"B0FBRRHCG5", name:"Vaso Libro Colorato Impilabile Decorativo Casa Mensola Ufficio Regalo", category:"casa", emoji:"🌿", clr1:"#fbbf24", clr2:"#34d399", image:"https://m.media-amazon.com/images/I/71BXDdxUPSL._AC_SL300_.jpg", price:18.59, oldPrice:null, discount:null, offerBadge:true },
  { asin:"B0B9JYS6GB", name:"Arte Astratta Donna Scultura Colorata Figura Yoga Decorazione Moderna Casa", category:"casa", emoji:"🎨", clr1:"#f97316", clr2:"#a78bfa", image:"https://m.media-amazon.com/images/I/61t9Ep3XnWL._AC_SL300_.jpg", price:45.99, oldPrice:null, discount:null, offerBadge:false },
  { asin:"B0BK3HZW2L", name:"Elefante Astratto Resina Graffiti Colorato Statua Decorazione Casa Arte", category:"casa", emoji:"🐘", clr1:"#38bdf8", clr2:"#fb923c", image:"https://m.media-amazon.com/images/I/71mDxPFrMGL._AC_SL300_.jpg", price:32.88, oldPrice:null, discount:null, offerBadge:false },
  { asin:"B0FD77ZGMB", name:"Decorazioni Murali Metallo Multicolore Fiori 2 Pezzi Soggiorno Camera da Letto", category:"casa", emoji:"🌸", clr1:"#f43f5e", clr2:"#22c55e", image:"https://m.media-amazon.com/images/I/71mUXYEkFsL._AC_SL300_.jpg", price:22.29, oldPrice:null, discount:null, offerBadge:false },
];

const filePath = path.join(__dirname, '../js/products.js');
let content = fs.readFileSync(filePath, 'utf8');
// safe eval
const tmp = {};
new Function('window', content)(tmp);
const existingProducts = tmp.products;
const existingAsins = new Set(existingProducts.map(p => p.asin));
const today = new Date().toISOString().split('T')[0];

const toAdd = newProducts.filter(p => !existingAsins.has(p.asin));
console.log('Nuovi prodotti:', toAdd.length, '| Duplicati saltati:', newProducts.length - toAdd.length);

let nextId = Math.max(...existingProducts.map(p => p.id)) + 1;
toAdd.forEach(p => {
  p.id = nextId++;
  p.currency = 'EUR';
  p.amazonLink = 'https://www.amazon.it/dp/' + p.asin + '?tag=prezzotop08-21';
  p.importedAt = today;
});

const allProducts = [...existingProducts, ...toAdd];
const categories = ['abbigliamento', 'scarpe', 'casa'];
const catLabels = {
  abbigliamento: '── ABBIGLIAMENTO ──────────────────────────────────────────',
  scarpe:        '── SCARPE ────────────────────────────────────────────────',
  casa:          '── CASA ──────────────────────────────────────────────────',
};

let body = '';
for (const cat of categories) {
  const items = allProducts.filter(p => p.category === cat);
  if (!items.length) continue;
  items.sort((a, b) => (b.offerBadge ? 1 : 0) - (a.offerBadge ? 1 : 0));
  body += '\n  // ' + catLabels[cat] + '\n';
  items.forEach(p => {
    body += '  ' + JSON.stringify(p, null, 2).split('\n').join('\n  ') + ',\n\n';
  });
}
body = body.trimEnd().replace(/,$/, '');

const out =
`// EmporiumOnline - Prodotti reali con immagini e link Amazon verificati
// Tag affiliato: prezzotop08-21

window.AMAZON_TAG = "prezzotop08-21";

window.products = [
${body}
];

function buildAmazonLink(asin) {
  return "https://www.amazon.it/dp/" + asin + "?tag=" + window.AMAZON_TAG;
}
`;

fs.writeFileSync(filePath, out);
console.log('Totale prodotti:', allProducts.length);
console.log('Breakdown:', categories.map(c => c + ':' + allProducts.filter(p => p.category === c).length).join(', '));
