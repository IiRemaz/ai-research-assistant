
import {
  CalendarDays,
  Bookmark,
  Sparkles,
  ExternalLink,
  Hash,
} from "lucide-react";

import type { Paper } from "../../services/papersService";

interface PaperCardProps {
  paper: Paper;
}

function PaperCard({ paper }: PaperCardProps) {
  const publishedDate = new Date(paper.published ?? 0).toLocaleDateString(
    "en-US",
    {
      year: "numeric",
      month: "short",
      day: "numeric",
    }
  );

  return (
    <article className="rounded-xl border border-stone-200 bg-white p-5 transition-shadow hover:shadow-sm">
      <div className="flex items-start gap-5">
        <div className="flex h-32 w-24 shrink-0 items-center justify-center rounded-lg border border-stone-200 bg-stone-50">
          <span className="font-serif text-sm text-stone-400">
            PDF
          </span>
        </div>

        <div className="min-w-0 flex-1">
          <div className="mb-3 flex flex-wrap gap-2">
            <span className="rounded-full bg-[#e8e9d8] px-3 py-1 text-xs text-[#59643d]">
              Research Paper
            </span>

            <span className="rounded-full bg-stone-100 px-3 py-1 text-xs text-stone-600">
              arXiv
            </span>
          </div>

          <h2 className="font-serif text-xl font-bold leading-snug text-stone-900">
            {paper.title}
          </h2>

          <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-sm text-stone-500">
            <span className="flex items-center gap-2">
              <Hash size={16} />
              {paper.arxiv_id}
            </span>

            <span className="flex items-center gap-2">
              <CalendarDays size={16} />
              {publishedDate}
            </span>
          </div>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-3 border-t border-stone-100 pt-4">
        <button className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-[#59643d] px-4 py-2.5 text-sm text-white hover:bg-[#46512f]">
          <Sparkles size={16} />
          Summarize
        </button>

        <button className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-stone-300 px-4 py-2.5 text-sm text-stone-700 hover:bg-stone-50">
          <Bookmark size={16} />
          Save
        </button>

        <a
          href={paper.pdf_link ?? undefined}
          target="_blank"
          rel="noopener noreferrer"
          className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-stone-300 px-4 py-2.5 text-sm text-stone-700 hover:bg-stone-50"
        >
          View PDF
          <ExternalLink size={15} />
        </a>
      </div>
    </article>
  );
}

export default PaperCard;
