
import {
  BookOpen,
  Bookmark,
  FileText,
  Sparkles,
  Settings,
} from "lucide-react";

const navigationItems = [
  { label: "Research Library", icon: BookOpen },
  { label: "Saved Papers", icon: Bookmark },
  { label: "Summaries", icon: FileText },
  { label: "Search & Ask", icon: Sparkles },
];

function Sidebar() {
  return (
    <aside className="flex h-screen w-60 shrink-0 flex-col border-r border-stone-200 bg-white px-5 py-8">
      {/* Brand */}
      <div className="mb-12 px-3">
        <h1 className="whitespace-nowrap font-serif text-2xl font-bold text-stone-900">
  Research Desk
        </h1>
        <p className="mt-1 text-sm text-stone-500">
          AI Research Assistant
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-2">
        {navigationItems.map((item, index) => {
          const Icon = item.icon;

          return (
            <button
              key={item.label}
              className={`flex items-center gap-4 rounded-lg px-4 py-3 text-left transition-colors ${
                index === 0
                  ? "bg-[#e8e9d8] text-[#4d5934]"
                  : "text-stone-700 hover:bg-stone-100"
              }`}
            >
              <Icon size={21} strokeWidth={1.7} />
              <span className="text-sm font-medium">
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>

      {/* Settings */}
      <div className="mt-8 border-t border-stone-200 pt-6">
        <button className="flex w-full items-center gap-4 rounded-lg px-4 py-3 text-stone-700 transition-colors hover:bg-stone-100">
          <Settings size={21} strokeWidth={1.7} />
          <span className="text-sm font-medium">Settings</span>
        </button>
      </div>

    </aside>
  );
}

export default Sidebar;
