import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(VUE_APP_SUPABASE_URL, VUE_APP_SUPABASE_KEY)
