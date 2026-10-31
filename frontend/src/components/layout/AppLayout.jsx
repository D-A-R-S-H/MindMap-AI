import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, ClipboardCheck, Mic, BarChart3, CalendarClock, Users } from "lucide-react";

const links = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/diagnostic", label: "Diagnostic", icon: ClipboardCheck },
  { to: "/recall", label: "Speak & Recall", icon: Mic },
  { to: "/mastery", label: "Mastery", icon: BarChart3 },
  { to: "/revision", label: "Revision", icon: CalendarClock },
  { to: "/teacher", label: "Teacher", icon: Users },
];

export default function AppLayout() {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="hidden md:flex w-64 flex-col bg-[#0f1b4d] text-white p-5">
        <h1 className="text-xl font-bold mb-8">🧠 MindMap AI</h1>
        <nav className="space-y-1">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-xl text-sm transition ${
                  isActive ? "bg-indigo-500/30 text-white" : "text-slate-300 hover:bg-white/10"
                }`
              }
            >
              <Icon size={18} /> {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-6 md:p-10">
        <Outlet />
      </main>
    </div>
  );
}
