import Link from "next/link";
import DarkModeSwitcher from "@/components/Header/DarkModeSwitcher";
import DropdownUser from "@/components/Header/DropdownUser";
import SidebarSwitcher from "@/components/Header/SidebarSwitcher";
import Image from "next/image";

const Header = (props: {
  sidebarOpen: boolean;
  setSidebarOpen: (arg0: boolean) => void;
  sidebarSwitcherRef?: React.RefObject<HTMLButtonElement>;
}) => {
  console.log(props.sidebarOpen);
  return (
    <header className="fixed top-0 left-0 z-999 flex w-full h-16 bg-white drop-shadow-1 dark:bg-boxdark dark:drop-shadow-none items-center px-10">
      <div className="flex items-center h-full gap-4">
        <Link href="/" className="flex items-center justify-center h-full">
          <Image
            width={60}
            height={60}
            src={"/images/logo/logo.webp"}
            alt="Logo"
            priority
            className="rounded-full object-cover"
          />
        </Link>
      </div>
      <div className="flex flex-grow items-center justify-end px-2 h-full">
        <div className="flex items-center gap-3 2xsm:gap-7">
          <ul className="flex items-center gap-2 2xsm:gap-4">
            <DarkModeSwitcher />
            <li className="hidden 2xsm:block"/>
            <SidebarSwitcher
              sidebarOpen={props.sidebarOpen}
              setSidebarOpen={props.setSidebarOpen}
              ref={props.sidebarSwitcherRef}
            />
          </ul>
          <DropdownUser />
        </div>
      </div>
    </header>
  );
};

export default Header;
