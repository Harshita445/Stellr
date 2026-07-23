"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const at = localStorage.getItem("access_token");
    const did = localStorage.getItem("device_id");
    if (at && did) {
      router.replace("/dashboard");
    } else {
      router.replace("/register");
    }
  }, [router]);

  return null;
}
