"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  
  const links = [
    { href: "/admin", label: "Dashboard" },
    { href: "/admin/turfs", label: "Turfs" },
    { href: "/admin/owners", label: "Owners" },
    { href: "/admin/payments", label: "Payments" },
  ];

  return (
    <div className="flex h-screen bg-bg-app">
      <aside className="w-64 bg-sidebar text-white flex flex-col">
        <div className="p-4 font-bold text-xl text-arena-green">TurfPro Admin</div>
        <nav className="flex-1 mt-6">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`block px-4 py-3 hover:bg-accent ${pathname === l.href ? "bg-accent" : ""}`}
            >
              {l.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
