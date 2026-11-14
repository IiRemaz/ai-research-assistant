
import { RefreshCw } from "lucide-react";

function Header() {
  return (
    <header className="flex flex-wrap items-start justify-between gap-5">
      <div className="min-w-0 flex-1">
        <h1 className="font-serif text-4xl font-bold text-stone-900">
          Research Library
        </h1>

        <p className="mt-2 text-stone-500">
          Browse the latest AI research papers from arXiv.
        </p>
      </div>

      <button className="flex shrink-0 items-center gap-3 rounded-lg border border-[#59643d] px-4 py-3 text-sm font-medium text-[#4d5934] transition-colors hover:bg-[#f3f4ec]">
        <RefreshCw size={18} />
        <span className="whitespace-nowrap">Update Papers</span>
      </button>
    </header>
  );
}

export default Header;

