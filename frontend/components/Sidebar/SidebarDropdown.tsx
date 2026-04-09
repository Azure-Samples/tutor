import Link from "next/link";
import { usePathname } from "next/navigation";
import type React from "react";

type SidebarDropdownItem = {
  route: string;
  label: string;
};

type SidebarDropdownProps = {
  item: SidebarDropdownItem[];
};

const SidebarDropdown: React.FC<SidebarDropdownProps> = ({ item }) => {
  const pathname = usePathname();

  return (
    <>
      <ul className="mb-5.5 mt-4 flex flex-col gap-2.5 pl-6">
        {item.map((dropdownItem) => (
          <li key={dropdownItem.route}>
            <Link
              href={dropdownItem.route}
              className={`group relative flex items-center gap-2.5 rounded-md px-4 font-medium text-bodydark2 duration-300 ease-in-out hover:text-black ${
                pathname === dropdownItem.route ? "text-black" : ""
              }`}
            >
              {dropdownItem.label}
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
};

export default SidebarDropdown;
