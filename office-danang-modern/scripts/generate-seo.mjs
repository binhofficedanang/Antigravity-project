import { createClient } from '@supabase/supabase-js';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const supabaseUrl = 'https://rlpchduiprqrmpoknqhd.supabase.co';
const supabaseKey = 'sb_publishable_6-Z1fhU1CU_ATfh9LJH1LA_gCDSwFLn';
const supabase = createClient(supabaseUrl, supabaseKey);

const BASE_URL = 'https://office43.vn';
const DIST_DIR = path.resolve(__dirname, '../dist');

function toSlug(str) {
  return (str || '')
    .toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

// Strip HTML tags helper
function stripHtml(html) {
  return (html || '')
    .replace(/<[^>]*>/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

async function run() {
  console.log('Generating SEO pages, sitemap, schema & llms.txt...');
  
  if (!fs.existsSync(DIST_DIR)) {
    console.error('dist directory not found! Run npm run build first.');
    return;
  }

  const indexPath = path.join(DIST_DIR, 'index.html');
  if (!fs.existsSync(indexPath)) {
    console.error('index.html not found in dist!');
    return;
  }
  
  const baseHtml = fs.readFileSync(indexPath, 'utf-8');

  // 1. Fetch Buildings from Supabase
  let { data: buildings, error } = await supabase.from('buildings').select('*');
  if (error) {
    console.error('Error fetching buildings:', error);
    return;
  }

  // Filter out whole building listings (> 100 USD/m2) or bad entries
  buildings = buildings.filter(b => !b.price || parseFloat(b.price) <= 100 || b.price === 'Liên hệ');
  console.log(`Found ${buildings.length} buildings after filtering.`);

  // Blog posts are now managed independently via Office43's own CMS
  // No longer fetching from external WordPress API
  let posts = [];

  const sitemapUrls = [];
  
  // Base URLs
  sitemapUrls.push(`${BASE_URL}/`);
  sitemapUrls.push(`${BASE_URL}/tim-kiem`);
  sitemapUrls.push(`${BASE_URL}/blog`);

  // 2.5 Rewrite Root index.html (Homepage) statically to ensure correct Open Graph and Site Name metadata
  const homepageTitle = 'Cho thuê văn phòng Đà Nẵng — Hạng A, B, C giá tốt nhất | Office43';
  const homepageDesc = 'Tìm thuê văn phòng tại Đà Nẵng hạng A, B, C. Bộ lọc thông minh theo quận, giá, hạng. Hơn 110+ tòa nhà cập nhật mới nhất. Liên hệ nhận báo giá miễn phí.';
  const homepageUrl = `${BASE_URL}/`;
  const homepageSchema = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "Office43",
    "alternateName": "Cho thuê văn phòng Đà Nẵng",
    "url": BASE_URL
  };
  const homepageOg = `
    <meta name="description" content="${homepageDesc}" />
    <meta property="og:title" content="${homepageTitle}" />
    <meta property="og:description" content="${homepageDesc}" />
    <meta property="og:image" content="${BASE_URL}/assets/modern_office_generic.jpg" />
    <meta property="og:url" content="${homepageUrl}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Office43" />
    <meta name="twitter:card" content="summary_large_image" />
    <script type="application/ld+json">${JSON.stringify(homepageSchema)}</script>
  `;
  let homepageHtml = baseHtml;
  homepageHtml = homepageHtml.replace(/<title>.*?<\/title>/, `<title>${homepageTitle}</title>`);
  homepageHtml = homepageHtml.replace('</head>', `${homepageOg}</head>`);
  fs.writeFileSync(indexPath, homepageHtml);

  // 3. Generate Ward Pages (SSG)
  const wards = [...new Set(buildings.map(b => b.district))];
  for (const ward of wards) {
    const slug = toSlug(ward);
    const url = `${BASE_URL}/phuong/${slug}`;
    sitemapUrls.push(url);

    const targetDir = path.join(DIST_DIR, 'phuong', slug);
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }

    const cleanWardName = ward.replace(/^(Phường|P\.)\s+/i, '');
    const wardBuildings = buildings.filter(b => b.district === ward);
    const totalCount = wardBuildings.length;
    const validPrices = wardBuildings
      .map(b => parseFloat(b.price))
      .filter(p => !isNaN(p) && p > 0);
    const avgPrice = validPrices.length > 0 
      ? (validPrices.reduce((sum, p) => sum + p, 0) / validPrices.length).toFixed(1)
      : 'Liên hệ';
    const avgPriceText = avgPrice !== 'Liên hệ' ? `$${avgPrice}/m²` : 'Liên hệ';

    const title = `Cho thuê văn phòng Phường ${cleanWardName} — ${totalCount} Tòa nhà giá từ ${avgPriceText}`;
    const desc = `Hiện có ${totalCount} tòa nhà văn phòng cho thuê tại Phường ${cleanWardName}, Đà Nẵng. Mức giá trung bình đạt ${avgPriceText}/tháng. Bản đồ & so sánh giá trực quan.`;
    
    // WebPage Schema
    const schema = {
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": title,
      "description": desc,
      "url": url
    };

    const ogTags = `
      <meta name="description" content="${desc}" />
      <meta property="og:title" content="${title}" />
      <meta property="og:description" content="${desc}" />
      <meta property="og:image" content="${BASE_URL}/assets/modern_office_generic.jpg" />
      <meta property="og:url" content="${url}" />
      <meta property="og:type" content="website" />
      <meta name="twitter:card" content="summary_large_image" />
      <script type="application/ld+json">${JSON.stringify(schema)}</script>
    `;

    let newHtml = baseHtml;
    newHtml = newHtml.replace(/<title>.*?<\/title>/, `<title>${title}</title>`);
    newHtml = newHtml.replace('</head>', `${ogTags}</head>`);
    fs.writeFileSync(path.join(targetDir, 'index.html'), newHtml);
  }

  // 4. Generate Building Pages (SSG) with Product Schema
  for (const b of buildings) {
    const slug = b.id;
    const url = `${BASE_URL}/van-phong/${slug}`;
    sitemapUrls.push(url);

    const targetDir = path.join(DIST_DIR, 'van-phong', slug);
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }

    const cleanDistrict = b.district.replace(/^(Phường|P\.)\s+/i, '');
    const title = `${b.name} - Cho thuê văn phòng Phường ${cleanDistrict} | Office43`;
    const desc = `Cho thuê văn phòng tại ${b.name}, ${b.address}. Hạng ${b.grade}, giá từ $${b.price}/m2. Liên hệ nhận báo giá chi tiết.`;
    let img = b.imageUrl || b.image;
    if (!img) img = `${BASE_URL}/assets/modern_office_generic.jpg`;

    // Product Schema
    const priceNum = parseFloat(b.price);
    const offerSchema = !isNaN(priceNum) && priceNum > 0 ? {
      "@type": "Offer",
      "price": priceNum,
      "priceCurrency": "USD",
      "priceSpecification": {
        "@type": "UnitPriceSpecification",
        "price": priceNum,
        "priceCurrency": "USD",
        "unitText": "m2"
      }
    } : {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD",
      "description": "Liên hệ báo giá"
    };

    const schema = {
      "@context": "https://schema.org",
      "@type": "Product",
      "name": b.name,
      "image": img,
      "description": desc,
      "offers": offerSchema
    };

    const ogTags = `
      <meta name="description" content="${desc}" />
      <meta property="og:title" content="${title}" />
      <meta property="og:description" content="${desc}" />
      <meta property="og:image" content="${img}" />
      <meta property="og:url" content="${url}" />
      <meta property="og:type" content="website" />
      <meta name="twitter:card" content="summary_large_image" />
      <script type="application/ld+json">${JSON.stringify(schema)}</script>
    `;

    let newHtml = baseHtml;
    newHtml = newHtml.replace(/<title>.*?<\/title>/, `<title>${title}</title>`);
    newHtml = newHtml.replace('</head>', `${ogTags}</head>`);
    fs.writeFileSync(path.join(targetDir, 'index.html'), newHtml);
  }

  // 5. Generate Blog Pages (SSG) with BlogPosting Schema
  for (const post of posts) {
    const slug = post.slug;
    const url = `${BASE_URL}/blog/${slug}`;
    sitemapUrls.push(url);

    const targetDir = path.join(DIST_DIR, 'blog', slug);
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }

    const title = `${post.title} | Office43`;
    const desc = post.excerpt.substring(0, 160);

    // BlogPosting Schema
    const schema = {
      "@context": "https://schema.org",
      "@type": "BlogPosting",
      "headline": post.title,
      "image": post.image,
      "datePublished": post.date,
      "description": desc,
      "author": {
        "@type": "Organization",
        "name": "Office43",
        "url": BASE_URL
      }
    };

    const ogTags = `
      <meta name="description" content="${desc}" />
      <meta property="og:title" content="${title}" />
      <meta property="og:description" content="${desc}" />
      <meta property="og:image" content="${post.image}" />
      <meta property="og:url" content="${url}" />
      <meta property="og:type" content="article" />
      <meta name="twitter:card" content="summary_large_image" />
      <script type="application/ld+json">${JSON.stringify(schema)}</script>
    `;

    let newHtml = baseHtml;
    newHtml = newHtml.replace(/<title>.*?<\/title>/, `<title>${title}</title>`);
    newHtml = newHtml.replace('</head>', `${ogTags}</head>`);
    fs.writeFileSync(path.join(targetDir, 'index.html'), newHtml);
  }

  // 6. Generate llms.txt & llms-full.txt for AI Search Bots
  let baseLlmsText = '';
  try {
    baseLlmsText = fs.readFileSync(path.join(__dirname, '../public/llms.txt'), 'utf-8');
  } catch (err) {
    baseLlmsText = `# Office43 - Cho thuê văn phòng Đà Nẵng\n\nWebsite cung cấp danh sách văn phòng cho thuê chuyên nghiệp hạng A, B, C tại các phường trung tâm TP Đà Nẵng.\n\n## Địa Chỉ Liên Hệ\n- Hotline: 0931.334.654\n- Website: ${BASE_URL}\n\n`;
  }
  
  let llmsTxt = baseLlmsText + `\n\n## Danh sách Phường (Theo khu vực)\n`;
  wards.forEach(w => {
    llmsTxt += `- [Phường ${w.replace(/^(Phường|P\.)\s+/i, '')}](${BASE_URL}/phuong/${toSlug(w)})\n`;
  });
  
  llmsTxt += `\n## Danh sách Tòa nhà tiêu biểu\n`;
  buildings.slice(0, 25).forEach(b => {
    llmsTxt += `- [${b.name}](${BASE_URL}/van-phong/${b.id}): Hạng ${b.grade}, giá từ $${b.price}/m2. Địa chỉ: ${b.address}\n`;
  });
  
  fs.writeFileSync(path.join(DIST_DIR, 'llms.txt'), llmsTxt);

  // llms-full.txt containing deep structural content of ALL offices
  let llmsFullTxt = baseLlmsText + `\n\n## Dữ liệu Toàn bộ Tòa nhà (${buildings.length})\n\n`;
  buildings.forEach(b => {
    llmsFullTxt += `### ${b.name}\n`;
    llmsFullTxt += `- **ID / Link**: [${b.id}](${BASE_URL}/van-phong/${b.id})\n`;
    llmsFullTxt += `- **Phân hạng**: Hạng ${b.grade}\n`;
    llmsFullTxt += `- **Giá thuê**: $${b.price}/m2\n`;
    llmsFullTxt += `- **Địa chỉ**: ${b.address}\n`;
    if (b.description) {
      llmsFullTxt += `- **Mô tả chi tiết**: ${stripHtml(b.description).substring(0, 500)}...\n`;
    }
    llmsFullTxt += `\n`;
  });
  
  fs.writeFileSync(path.join(DIST_DIR, 'llms-full.txt'), llmsFullTxt);

  // 7. Write sitemap.xml
  const sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  ${sitemapUrls.map(url => `
  <url>
    <loc>${url}</loc>
    <changefreq>weekly</changefreq>
    <priority>${url === BASE_URL + '/' ? '1.0' : '0.8'}</priority>
  </url>`).join('')}
</urlset>`;
  fs.writeFileSync(path.join(DIST_DIR, 'sitemap.xml'), sitemapXml);
  
  // 8. Write robots.txt
  const robotsTxt = `User-agent: *
Allow: /
Sitemap: ${BASE_URL}/sitemap.xml`;
  fs.writeFileSync(path.join(DIST_DIR, 'robots.txt'), robotsTxt);

  console.log('SEO Generation Complete! 🎉');
}

run();
