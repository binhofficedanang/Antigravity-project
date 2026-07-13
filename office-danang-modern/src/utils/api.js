import { geoData } from '../data/geo';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://rlpchduiprqrmpoknqhd.supabase.co';
const supabaseKey = 'sb_publishable_6-Z1fhU1CU_ATfh9LJH1LA_gCDSwFLn';
export const supabase = createClient(supabaseUrl, supabaseKey);

/**
 * Fetch all buildings from Supabase database
 */
export async function fetchBuildings() {
  const { data, error } = await supabase
    .from('buildings')
    .select('*')
    .order('created_at', { ascending: true });

  if (error) {
    console.error('Error fetching buildings from Supabase:', error);
    return [];
  }
  
  // Merge geo data and filter out whole building listings (e.g. price > 100)
  const mergedData = data
    .filter(b => !b.price || parseFloat(b.price) <= 100 || b.price === 'Liên hệ')
    .map(b => ({
      ...b,
      lat: b.lat || geoData[b.id]?.lat || 16.060,
      lng: b.lng || geoData[b.id]?.lng || 108.220
    }));
  
  return mergedData;
}

/**
 * Fetch all blog posts — returns empty for now, blog will be managed via Office43 CMS
 */
export async function fetchPosts() {
  return [];
}
