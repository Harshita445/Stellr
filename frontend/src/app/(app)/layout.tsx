import { Sidebar } from "@/components/layout/sidebar";

export default function AppLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 ml-60 p-6 lg:p-8 relative z-10">
        {children}
      </main>
    </div>
  );
}
