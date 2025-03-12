import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://rpwmcpmrzfveosdcvwjz.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJwd21jcG1yemZ2ZW9zZGN2d2p6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAzODAxNTksImV4cCI6MjA1NTk1NjE1OX0.FDafYWgJbHN8AktZ202GJrBhDX_hM2NUqAyHLBAwtC8';

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);