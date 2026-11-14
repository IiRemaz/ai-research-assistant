
import { Search } from "lucide-react";

type SearchBarProps = {
  value: string;
  onChange: (value: string) => void;
};

function SearchBar({ value, onChange }: SearchBarProps) {
  return (
    <div className="mt-10 flex items-center gap-3 rounded-lg border border-stone-300 px-5 py-4">
      <Search size={21} className="text-[#59643d]" />

      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Search papers by title, topic, or keyword..."
        className="w-full bg-transparent text-sm text-stone-800 outline-none placeholder:text-stone-400"
      />
    </div>
  );
}

export default SearchBar;
