import React from "react";
import Link from "next/link";
import SidebarDropdown from "@/components/Sidebar/SidebarDropdown";
import { usePathname } from "next/navigation";

const SidebarItem = ({ item, pageName, setPageName, className = "" }: any) => {
  const handleClick = () => {
    const updatedPageName =
      pageName !== item.label.toLowerCase() ? item.label.toLowerCase() : "";
    return setPageName(updatedPageName);
  };

  const pathname = usePathname();

  const isActive = (item: any) => {
    if (item.route === pathname) return true;
    if (item.children) {
      return item.children.some((child: any) => isActive(child));
    }
    return false;
  };

  const isItemActive = isActive(item);
  const gradient = item.gradient || "from-cyan-400 to-blue-500";
  const hoverText = item.hoverText || "text-cyan-500";
  const iconGradient = item.gradient || "from-cyan-400 to-blue-500";

  return (
    <li>
      <Link
        href={item.route}
        onClick={handleClick}
        className={`group relative flex items-center gap-2.5 rounded-xl px-4 py-2 font-medium text-black dark:text-white duration-300 ease-in-out
          border-2 border-transparent
          ${isItemActive ? `bg-gradient-to-br ${iconGradient} text-white border-blue-400` : ""}
          hover:bg-white hover:text-white hover:border-2 hover:border-gradient-to-br
          focus:outline-none focus:ring-2 focus:ring-blue-400
          transition-all
          ${className}`}
      >
        <span
          className={`flex items-center justify-center w-10 h-10 rounded-full p-2 transition-all duration-300
            bg-gradient-to-br ${iconGradient} text-white
            hover:bg-white hover:${hoverText}
          `}
        >
          {React.cloneElement(item.icon.props.children, {
            className: `w-6 h-6 transition-all duration-300 text-white group-hover:bg-gradient-to-br group-hover:${iconGradient} group-hover:text-transparent group-hover:bg-clip-text`
          })}
        </span>
        <span className={isItemActive ? "" : `bg-gradient-to-r ${gradient} bg-clip-text text-transparent`}>
          {item.label}
        </span>
        {item.children && (
          <svg
            className={`absolute right-4 top-1/2 -translate-y-1/2 fill-current ${
              pageName === item.label.toLowerCase() && "rotate-180"
            }`}
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M4.41107 6.9107C4.73651 6.58527 5.26414 6.58527 5.58958 6.9107L10.0003 11.3214L14.4111 6.91071C14.7365 6.58527 15.2641 6.58527 15.5896 6.91071C15.915 7.23614 15.915 7.76378 15.5896 8.08922L10.5896 13.0892C10.2641 13.4147 9.73651 13.4147 9.41107 13.0892L4.41107 8.08922C4.08563 7.76378 4.08563 7.23614 4.41107 6.9107Z"
              fill=""
            />
          </svg>
        )}
      </Link>
      {item.children && (
        <div
          className={`translate transform overflow-hidden ${
            pageName !== item.label.toLowerCase() && "hidden"
          }`}
        >
          <SidebarDropdown item={item.children} />
        </div>
      )}
    </li>
  );
};

export default SidebarItem;
