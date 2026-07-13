import { createClient } from '@supabase/supabase-js';
import { buildingsData } from '../src/data/buildings.js';

const supabase = createClient('https://rlpchduiprqrmpoknqhd.supabase.co', 'sb_publishable_6-Z1fhU1CU_ATfh9LJH1LA_gCDSwFLn');

async function cleanAddresses() {
  console.log('Standardizing addresses in Supabase...');
  for (const b of buildingsData) {
    if (b.address) {
      // Step 1: Remove trailing ", Đà Nẵng" or ", TP Đà Nẵng"
      let cleanAddress = b.address.replace(/,\s*(Thành phố |TP\.?\s*)?Đà Nẵng/gi, '').trim();

      const wardStr = b.district; // e.g. 'Phường Hải Châu'
      const wardRawName = wardStr.replace('Phường ', '').trim(); // e.g. 'Hải Châu'

      // Step 2: Look for existing ward mentions and replace them with standard 'Phường X'
      // We look for "P. Hải Châu", "Phường Hải Châu", or just "Hải Châu" (only if it's at the end or preceded by a comma)
      
      // Regex to find ", P. Hải Châu", ", Phường Hải Châu", ", Hải Châu", or just "P. Hải Châu"
      const regex = new RegExp(`(,?)\\s*(P\\.|Phường)?\\s*${wardRawName}$`, 'i');
      
      if (regex.test(cleanAddress)) {
        // Replace it with exactly ", Phường X"
        cleanAddress = cleanAddress.replace(regex, `, ${wardStr}`);
      } else {
        // If the address doesn't contain the ward name at the end at all, append it
        cleanAddress = `${cleanAddress}, ${wardStr}`;
      }
      
      // Clean up double commas if any
      cleanAddress = cleanAddress.replace(/,,/g, ',').replace(/\s+,/g, ',');

      console.log(`${b.id}: ${cleanAddress}`);

      const { error } = await supabase.from('buildings').update({ address: cleanAddress }).eq('id', b.id);
      if (error) {
        console.error(`Error updating ${b.id}:`, error);
      }
    }
  }
  console.log('Done standardizing addresses!');
}

cleanAddresses();
