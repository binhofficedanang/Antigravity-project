import { createClient } from '@supabase/supabase-js';
import { buildingsData } from '../src/data/buildings.js';

const supabase = createClient('https://rlpchduiprqrmpoknqhd.supabase.co', 'sb_publishable_6-Z1fhU1CU_ATfh9LJH1LA_gCDSwFLn');

async function restore() {
  console.log('Restoring addresses from local buildingsData to Supabase...');
  for (const b of buildingsData) {
    if (b.address) {
      // Clean up the address slightly by removing ", Đà Nẵng" because it's redundant
      let cleanAddress = b.address.replace(/,\s*(Thành phố |TP\.?\s*)?Đà Nẵng/gi, '').trim();
      if (!cleanAddress.includes('Phường')) {
        cleanAddress = `${cleanAddress} (${b.district})`;
      }
      const { error } = await supabase.from('buildings').update({ address: cleanAddress }).eq('id', b.id);
      if (error) {
        console.error(`Error updating ${b.id}:`, error);
      }
    }
  }
  console.log('Done restoring addresses!');
}

restore();
