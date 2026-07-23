import { VisibleStars } from "@/components/dashboard/visible-stars";
import { Constellations } from "@/components/dashboard/constellations";
import { NextAlignment } from "@/components/dashboard/next-alignment";

export default function DashboardPage() {
  return (
    <main className="min-h-screen p-4 max-w-2xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">
          Your Space
        </h1>
        <p className="text-sm text-text-muted mt-1">
          Track your schedule and connected stars
        </p>
      </div>

      <NextAlignment />
      <VisibleStars />
      <Constellations />
    </main>
  );
}
