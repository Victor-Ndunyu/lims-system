import { useRouter } from "next/router";
import { useEffect } from "react";
import { getStoredToken, getStoredUser } from "./session";

export function useRequireAuth() {
  const router = useRouter();
  useEffect(() => {
    if (!getStoredToken()) {
      router.replace("/login");
    }
  }, [router]);
}

export function useRequireRole(role: string) {
  const router = useRouter();
  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.replace("/login");
      return;
    }
    if (user.role_name !== role) {
      router.replace("/login");
    }
  }, [router, role]);
}
