import { type NextRequest } from "next/server";

import { createClient } from "@/utils/supabase/middleware";

export async function proxy(request: NextRequest) {
  const { supabase, response } = createClient(request);

  // Required by Supabase SSR to refresh expired auth cookies.
  await supabase.auth.getUser();

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except static assets and image optimization.
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
