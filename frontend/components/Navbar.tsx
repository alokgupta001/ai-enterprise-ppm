"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { 
  LayoutDashboard, 
  ClipboardList, 
  MessageSquare, 
  FolderGit2, 
  LogOut, 
  User, 
  Building,
  Sparkles
} from "lucide-react";
import { fetchCurrentUser } from "@/lib/api";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<any>(null);

  useEffect(() => {
    // Fetch profile to verify token and display user/org details
    fetchCurrentUser()
      .then((data) => {
        setCurrentUser(data);
      })
      .catch(() => {
        // Redirect to login if token invalid/missing
        if (pathname !== "/login") {
          router.push("/login");
        }
      });
  }, [pathname, router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  const getOrgNameFromEmail = (email: string): string => {
    try {
      if (!email || typeof email !== 'string') return 'Organization';
      const domain = email.split("@")[1];
      if (!domain) return 'Organization';
      const orgName = domain.split(".")[0];
      return orgName ? orgName.toUpperCase() : 'Organization';
    } catch {
      return 'Organization';
    }
  };

  const navItems = [
    { name: "Assessments", href: "/assessments", icon: ClipboardList },
    { name: "PMO Assistant", href: "/assistant", icon: MessageSquare },
  ];

  if (pathname === "/login") return null;

  return (
    <aside className="w-64 bg-zinc-950 text-zinc-300 border-r border-zinc-800 flex flex-col justify-between select-none">
      <div>
        {/* Branding */}
        <div className="p-6 border-b border-zinc-800 flex items-center gap-3">
          <div className="p-2 bg-indigo-600 rounded-lg text-white">
            <Sparkles className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-bold text-white text-lg tracking-tight leading-none">PMO</h1>
            <span className="text-xs text-indigo-400 font-semibold uppercase tracking-wider">Enterprise PPM</span>
          </div>
        </div>

        {/* Org Context */}
        {currentUser && (
          <div className="p-4 mx-4 my-3 bg-zinc-900 border border-zinc-800 rounded-lg flex items-center gap-3">
            <div className="p-2 bg-zinc-800 rounded text-zinc-400">
              <Building className="h-4 w-4" />
            </div>
            <div className="overflow-hidden">
              <p className="text-xs text-zinc-500 font-medium">Organization</p>
              <p className="text-sm font-semibold text-zinc-200 truncate">{getOrgNameFromEmail(currentUser.email)}</p>
            </div>
          </div>
        )}

        {/* Navigation Links */}
        <nav className="px-4 py-3 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive 
                    ? "bg-indigo-600/15 text-indigo-400 border-l-4 border-indigo-500 pl-3" 
                    : "hover:bg-zinc-900 hover:text-white"
                }`}
              >
                <Icon className={`h-5 w-5 ${isActive ? "text-indigo-400" : "text-zinc-400"}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* User Session profile & logout */}
      {currentUser && (
        <div className="p-4 border-t border-zinc-800 space-y-3">
          <div className="flex items-center gap-3 px-2">
            <div className="h-9 w-9 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-zinc-300 font-bold">
              {currentUser.name.charAt(0).toUpperCase()}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-semibold text-white truncate">{currentUser.name}</p>
              <p className="text-xs text-zinc-500 truncate">{currentUser.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium text-zinc-400 hover:bg-red-500/10 hover:text-red-400 transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Sign Out
          </button>
        </div>
      )}
    </aside>
  );
}
