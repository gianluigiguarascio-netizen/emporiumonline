// Catalogo prodotti moda dropshipping
const fashionProducts = [
  { id: 1, emoji: "👗", name: "Vestito Floreale Arcobaleno", tag: "Donna", price: "29.99", oldPrice: "59.99", clr1: "#ff6b9d", clr2: "#fbbf24", link: "#", discount: "-50%" },
  { id: 2, emoji: "🌈", name: "Gonna a Ruota Multicolor", tag: "Donna", price: "24.90", oldPrice: "44.90", clr1: "#a78bfa", clr2: "#38bdf8", link: "#", discount: "-44%" },
  { id: 3, emoji: "🎽", name: "T-Shirt Tie-Dye Neon", tag: "Unisex", price: "18.50", oldPrice: "35.00", clr1: "#34d399", clr2: "#fbbf24", link: "#", discount: "-47%" },
  { id: 4, emoji: "🧥", name: "Giacca Colorblock Vibrante", tag: "Uomo", price: "54.90", oldPrice: "99.90", clr1: "#fb923c", clr2: "#a78bfa", link: "#", discount: "-45%" },
  { id: 5, emoji: "👚", name: "Hoodie Arcobaleno Oversized", tag: "Unisex", price: "39.90", oldPrice: "74.90", clr1: "#38bdf8", clr2: "#ff6b9d", link: "#", discount: "-47%" },
  { id: 6, emoji: "🩱", name: "Coordinato Crop + Shorts Neon", tag: "Donna", price: "32.00", oldPrice: "58.00", clr1: "#fbbf24", clr2: "#34d399", link: "#", discount: "-45%" },
  { id: 7, emoji: "🩲", name: "Shorts Colorati da Spiaggia", tag: "Uomo", price: "19.90", oldPrice: "38.00", clr1: "#ff6b9d", clr2: "#38bdf8", link: "#", discount: "-48%" },
  { id: 8, emoji: "🎀", name: "Abito Maxi con Stampe Tropicali", tag: "Donna", price: "44.90", oldPrice: "84.90", clr1: "#34d399", clr2: "#ff6b9d", link: "#", discount: "-47%" },
];

const shoesProducts = [
  { id: 10, emoji: "👟", name: "Sneakers Chunky Arcobaleno", tag: "Sneakers", price: "64.90", oldPrice: "119.90", clr1: "#ff6b9d", clr2: "#a78bfa", link: "#", discount: "-46%" },
  { id: 11, emoji: "🌈", name: "Slip-On Neon Multicolor", tag: "Casual", price: "42.00", oldPrice: "78.00", clr1: "#fbbf24", clr2: "#34d399", link: "#", discount: "-46%" },
  { id: 12, emoji: "👠", name: "Sandali Platform Colorati", tag: "Donna", price: "38.90", oldPrice: "72.90", clr1: "#38bdf8", clr2: "#ff6b9d", link: "#", discount: "-47%" },
  { id: 13, emoji: "🥿", name: "Mocassini Tie-Dye Comfort", tag: "Unisex", price: "49.90", oldPrice: "89.90", clr1: "#a78bfa", clr2: "#fbbf24", link: "#", discount: "-44%" },
  { id: 14, emoji: "👞", name: "Scarpe da Skate Vivaci", tag: "Uomo", price: "55.00", oldPrice: "99.00", clr1: "#fb923c", clr2: "#38bdf8", link: "#", discount: "-44%" },
  { id: 15, emoji: "🩴", name: "Infradito Tropicali Colorati", tag: "Estate", price: "22.90", oldPrice: "39.90", clr1: "#34d399", clr2: "#ff6b9d", link: "#", discount: "-43%" },
  { id: 16, emoji: "🥾", name: "Stivali Colorblock Bold", tag: "Autunno", price: "79.90", oldPrice: "149.90", clr1: "#a78bfa", clr2: "#fb923c", link: "#", discount: "-47%" },
  { id: 17, emoji: "👡", name: "Décolleté Arcobaleno Vernice", tag: "Donna", price: "58.00", oldPrice: "108.00", clr1: "#ff6b9d", clr2: "#fbbf24", link: "#", discount: "-46%" },
];

// Prodotti Amazon Affiliate (da aggiornare con ASIN reali)
const amazonProducts = [
  { id: 20, emoji: "🔥", name: "Amazon: Vestito Estivo Floreale", tag: "Amazon", price: "27.99", oldPrice: "49.99", clr1: "#fbbf24", clr2: "#fb923c", asin: "B0XXXXXX01", discount: "-44%" },
  { id: 21, emoji: "⭐", name: "Amazon: Sneakers Donna Colorate", tag: "Amazon", price: "34.90", oldPrice: "64.90", clr1: "#ff6b9d", clr2: "#a78bfa", asin: "B0XXXXXX02", discount: "-46%" },
  { id: 22, emoji: "💥", name: "Amazon: Hoodie Colorblock Uomo", tag: "Amazon", price: "29.90", oldPrice: "55.00", clr1: "#34d399", clr2: "#38bdf8", asin: "B0XXXXXX03", discount: "-46%" },
  { id: 23, emoji: "🎯", name: "Amazon: Gonna Midi Multicolor", tag: "Amazon", price: "24.99", oldPrice: "44.99", clr1: "#a78bfa", clr2: "#fbbf24", asin: "B0XXXXXX04", discount: "-44%" },
  { id: 24, emoji: "🛍️", name: "Amazon: Scarpe Platform Neon", tag: "Amazon", price: "44.90", oldPrice: "84.90", clr1: "#fb923c", clr2: "#ff6b9d", asin: "B0XXXXXX05", discount: "-47%" },
  { id: 25, emoji: "✨", name: "Amazon: T-Shirt Tie-Dye Pack 3pz", tag: "Amazon", price: "32.00", oldPrice: "58.00", clr1: "#38bdf8", clr2: "#34d399", asin: "B0XXXXXX06", discount: "-45%" },
  { id: 26, emoji: "🏆", name: "Amazon: Completo Sportivo Colorato", tag: "Amazon", price: "39.90", oldPrice: "72.90", clr1: "#fbbf24", clr2: "#a78bfa", asin: "B0XXXXXX07", discount: "-45%" },
  { id: 27, emoji: "💫", name: "Amazon: Zaino Colorblock Fashion", tag: "Amazon", price: "28.90", oldPrice: "52.90", clr1: "#ff6b9d", clr2: "#34d399", asin: "B0XXXXXX08", discount: "-45%" },
];

// Tag affiliato Amazon — sostituisci con il tuo tag reale
const AMAZON_TAG = "emporiumonl-21";

function buildAmazonLink(asin) {
  return `https://www.amazon.it/dp/${asin}?tag=${AMAZON_TAG}`;
}
