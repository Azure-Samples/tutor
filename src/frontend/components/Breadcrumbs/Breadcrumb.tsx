import Link from "next/link";
interface BreadcrumbProps {
  pageName: string;
  subtitle?: string;
}
const Breadcrumb = ({ pageName, subtitle }: BreadcrumbProps) => {
  return (
    <div className="flex flex-col mb-10 gap-2 sm:flex-row sm:items-center sm:justify-between bg-gradient-to-r from-cyan-50 to-green-50 dark:from-blue-900 dark:to-green-900 rounded-xl p-4 shadow-md border border-cyan-100 dark:border-cyan-900 animate-fade-in">
      <div>
        <h2 className="text-title-md2 font-semibold text-fulvous dark:text-white flex items-center gap-2">
          <span className="inline-block animate-wiggle-slow">📚</span>
          {pageName}
        </h2>
        {subtitle && (
          <p className="mt-1 text-base text-blue-700 dark:text-blue-200 font-medium animate-fade-in-slow">
            {subtitle}
          </p>
        )}
      </div>
      <nav aria-label="Breadcrumb">
        <ol className="flex items-center gap-2">
          <li>
            <Link className="font-medium text-kelly-green hover:underline transition-colors duration-200" href="/">
              Tutor /
            </Link>
          </li>
          <li className="font-medium text-non-photo-blue">{pageName}</li>
        </ol>
      </nav>
    </div>
  );
};

export default Breadcrumb;
