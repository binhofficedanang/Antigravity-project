import { useEffect } from 'react';

/**
 * Sets document title, meta description, and optional Schema markup.
 */
export function useSEO({ title, description, schema }) {
  useEffect(() => {
    // Title
    document.title = title ? `${title} | Office43` : 'Cho thuê văn phòng Đà Nẵng | Office43';

    // Meta description
    let metaDesc = document.querySelector('meta[name="description"]');
    if (!metaDesc) {
      metaDesc = document.createElement('meta');
      metaDesc.name = 'description';
      document.head.appendChild(metaDesc);
    }
    metaDesc.content = description || 'Tìm thuê văn phòng tại Đà Nẵng hạng A, B, C. Bộ lọc thông minh, so sánh trực quan, nhận báo giá tức thì.';

    // Canonical
    let canonical = document.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.rel = 'canonical';
      document.head.appendChild(canonical);
    }
    canonical.href = window.location.href;

    // Schema JSON-LD
    const existingSchema = document.getElementById('page-schema');
    if (existingSchema) existingSchema.remove();

    if (schema) {
      const script = document.createElement('script');
      script.type = 'application/ld+json';
      script.id = 'page-schema';
      script.textContent = JSON.stringify(schema);
      document.head.appendChild(script);
    }

    return () => {
      const el = document.getElementById('page-schema');
      if (el) el.remove();
    };
  }, [title, description, schema]);
}

/**
 * Generate FAQ Schema for a page
 */
export function generateFAQSchema(faqs) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqs.map(f => ({
      "@type": "Question",
      "name": f.q,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": f.a
      }
    }))
  };
}

/**
 * Generate LocalBusiness Schema
 */
export function generateLocalBusinessSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "RealEstateAgent",
    "name": "Office43",
    "description": "Dịch vụ cho thuê văn phòng chuyên nghiệp tại Đà Nẵng",
    "url": "https://office43.vn",
    "telephone": "+84935723727",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Đà Nẵng",
      "addressCountry": "VN"
    },
    "areaServed": {
      "@type": "City",
      "name": "Đà Nẵng"
    }
  };
}

/**
 * Generate WebSite Schema to fix Google Search Site Name
 */
export function generateWebSiteSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "Office43",
    "alternateName": "Cho thuê văn phòng Đà Nẵng",
    "url": "https://office43.vn"
  };
}
