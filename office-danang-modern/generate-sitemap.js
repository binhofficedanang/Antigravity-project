import fs from 'fs';
import path from 'path';
import { createClient } from '@supabase/supabase-js';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const supabaseUrl = 'https://rlpchduiprqrmpoknqhd.supabase.co';
const supabaseKey = 'sb_publishable_6-Z1fhU1CU_ATfh9LJH1LA_gCDSwFLn';
const supabase = createClient(supabaseUrl, supabaseKey);

const SITE_URL = 'https://office43.vn';

async function generateSitemap() {
  console.log('Fetching buildings from Supabase...');
  const { data: buildings, error } = await supabase
    .from('buildings')
    .select('id, name');

  if (error) {
    console.error('Error fetching buildings:', error);
    process.exit(1);
  }

  const currentDate = new Date().toISOString().split('T')[0];

  let xml = `<?xml version="1.0" encoding="UTF-8"?>\n`;
  xml += `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n`;

  // Add homepage
  xml += `  <url>\n`;
  xml += `    <loc>${SITE_URL}</loc>\n`;
  xml += `    <lastmod>${currentDate}</lastmod>\n`;
  xml += `    <changefreq>daily</changefreq>\n`;
  xml += `    <priority>1.0</priority>\n`;
  xml += `  </url>\n`;

  // Add buildings
  for (const b of buildings) {
    // Generate slug exactly as done in BuildingCard.jsx (id-name)
    const slug = `${b.id}-${b.name.toLowerCase().replace(/\\s+/g, '-').replace(/[&]/g, 'and')}`;
    // Encode XML special characters
    const encodedLoc = `${SITE_URL}/toa-nha/${encodeURIComponent(slug)}`.replace(/&/g, '&amp;').replace(/'/g, '&apos;').replace(/"/g, '&quot;');
    
    xml += `  <url>\n`;
    xml += `    <loc>${encodedLoc}</loc>\n`;
    xml += `    <lastmod>${currentDate}</lastmod>\n`;
    xml += `    <changefreq>weekly</changefreq>\n`;
    xml += `    <priority>0.8</priority>\n`;
    xml += `  </url>\n`;
  }

  xml += `</urlset>`;

  const publicDir = path.join(__dirname, 'public');
  if (!fs.existsSync(publicDir)) {
    fs.mkdirSync(publicDir);
  }

  fs.writeFileSync(path.join(publicDir, 'sitemap.xml'), xml);
  console.log(`Generated sitemap.xml with ${buildings.length + 1} URLs.`);

  // Generate robots.txt
  const robotsTxt = `User-agent: *\nAllow: /\n\nSitemap: ${SITE_URL}/sitemap.xml\n`;
  fs.writeFileSync(path.join(publicDir, 'robots.txt'), robotsTxt);
  console.log('Generated robots.txt');
}

generateSitemap();
