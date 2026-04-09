import Link from "next/link";
interface BreadcrumbProps {
  pageName: string;
  subtitle?: string;
}
const Breadcrumb = ({ pageName, subtitle }: BreadcrumbProps) => {
  return (
    <div className="mb-8 rounded-[1.5rem] border border-stone-200 bg-white/88 p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900/75">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-teal-700">
            Current view
          </p>
          <h2 className="mt-3 text-3xl font-semibold text-slate-900 dark:text-slate-50">
            {pageName}
          </h2>
          {subtitle && (
            <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-600 dark:text-slate-300">
              {subtitle}
            </p>
          )}
        </div>
        <nav aria-label="Breadcrumb trail">
          <ol className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <li>
              <Link
                className="font-medium text-slate-600 transition hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:text-slate-300 dark:hover:text-slate-50"
                href="/"
              >
                Tutor
              </Link>
            </li>
            <li>/</li>
            <li aria-current="page" className="font-medium text-slate-900 dark:text-slate-50">
              {pageName}
            </li>
          </ol>
        </nav>
      </div>
    </div>
  );
};

export default Breadcrumb;
