import { createClient } from '@supabase/supabase-js';
const supabase = createClient('https://rlpchduiprqrmpoknqhd.supabase.co', 'sb_publishable_6-Z1fhU1CU_ATfh9LJH1LA_gCDSwFLn');
async function test() {
  const { data, error } = await supabase.from('buildings').select('*');
  const bd = data.filter(b => b.name.toLowerCase().includes('bạch đằng') || b.name.toLowerCase().includes('bach dang'));
  console.log(JSON.stringify(bd, null, 2));
}
test();
