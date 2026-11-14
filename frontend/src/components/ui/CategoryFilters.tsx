
const categories = [
  "All",
  "AI",
  "Machine Learning",
  "NLP",
  "Computer Vision",
  "Robotics",
  "Multimodal",
];

type CategoryFiltersProps = {
  activeCategory: string;
  onCategoryChange: (category: string) => void;
};

function CategoryFilters({
  activeCategory,
  onCategoryChange,
}: CategoryFiltersProps) {
  return (
    <div className="mt-6 flex flex-wrap items-center gap-3">
      {categories.map((category) => (
        <button
          key={category}
          onClick={() => onCategoryChange(category)}
          className={`rounded-full border px-5 py-2 text-sm transition-colors ${
            activeCategory === category
              ? "border-[#59643d] bg-[#59643d] text-white"
              : "border-stone-300 bg-white text-stone-700 hover:bg-stone-100"
          }`}
        >
          {category}
        </button>
      ))}
    </div>
  );
}

export default CategoryFilters;
